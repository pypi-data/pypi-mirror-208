# -*- coding: utf-8 -*-
"""More accurate estimation of magnet positions."""

from typing import Any
from typing import Dict
from typing import Union

from immutabledict import immutabledict
from nptyping import NDArray
from numba import njit
import numpy as np
from scipy.optimize import least_squares

from .constants import GUESS_INCR
from .constants import NUM_ACTIVE_WELLS
from .constants import NUM_AXES
from .constants import NUM_CHANNELS
from .constants import NUM_SENSORS
from .constants import WELLS_PER_COL
from .exceptions import UnableToConvergeError

ADJACENT_WELL_DISTANCE_MM = 19.5

# machine epsilon for float64, calibrated for 2-point derivative calculation
EPS_ADJ = np.finfo(np.float64).eps ** 0.5

DEFAULT_INITIAL_GUESS_VALUES = immutabledict(
    {"X": 2, "Y": 2, "Z": -5.0, "THETA": np.radians(90), "PHI": 0.0, "REMN": 1200.0}
)  # X position, Y position, Z position, Pitch, Yaw, Remanence (Br)


WELL_VERTICAL_SPACING = np.asarray([0, ADJACENT_WELL_DISTANCE_MM, 0])
WELL_HORIZONTAL_SPACING = np.asarray([-ADJACENT_WELL_DISTANCE_MM, 0, 0])
SENSOR_DISTANCES_FROM_CENTER_POINT = np.array([[-2.25, 2.25, 0], [2.25, 2.25, 0], [0, -2.25, 0]])
PARAMS = np.array(list(DEFAULT_INITIAL_GUESS_VALUES.keys()))
NUM_PARAMS = len(list((DEFAULT_INITIAL_GUESS_VALUES.keys())))

# Kevin (11/15/22): This is part of the dipole model
DIPOLE_MODEL_FACTOR = 4 * np.pi
# Kevin (11/15/22): for cylindrical magnet with diameter .75 mm and height 1 mm
MAGNET_VOLUME = np.pi * (0.75 / 2.0) ** 2

# typing consts
MANTA_SHAPE = (NUM_AXES, NUM_ACTIVE_WELLS * NUM_SENSORS, NUM_SENSORS)


# Compute moment vector of magnet
@njit(fastmath=True)  # type: ignore
def compute_moment(
    theta: float, phi: float, remn: float
) -> NDArray[
    (Any,), float
]:  # pragma: no cover  # Tanner (1/9/22): codecov cannot cover functions compiled with numba
    st = np.sin(theta)
    sph = np.sin(phi)
    ct = np.cos(theta)
    cph = np.cos(phi)
    return MAGNET_VOLUME * remn * np.array([[st * cph], [st * sph], [ct]])  # moment vectors


@njit(fastmath=True)  # type: ignore
def compute_jacobian(
    pos: NDArray[(1, Any), float],
    # b_meas is necessary since scipy will call this function with it, but it is not actually used
    b_meas: NDArray[(1, Any), float],
    manta: NDArray[MANTA_SHAPE, float],
) -> NDArray[
    (Any, Any), float
]:  # pragma: no cover  # Tanner (1/9/22): codecov cannot cover functions compiled with numba
    """The jacobian is a matrix of partial derivatives of the cost function
    w.r.t.

    each parameter at each axis of each sensor used by a least squares
    algorithm to compute the derivative of the rms of the cost function
    for minimization. Built-in scipy least_squares computation of the
    jacobian is inefficient in the context of multi-magnet finding
    problems, scaling with M*(N)**3 where N is the number of magnets,
    for an M parameter fit. Computing it separately from least_squares
    with the following method lets it scale by M*(N)**2. This approach
    speeds up pure python alg ~30x, numba accelerated ~10x for 24 well
    plate with data from the beta 2.2 The least_squares "method" should
    be set to "lm" and "ftol" to 1e-1 for specified performance The
    first 10 or so data points should be ignored, since there's a small
    transient
    """
    xpos, ypos, zpos, theta, phi, remn = pos.reshape(NUM_PARAMS, NUM_ACTIVE_WELLS)
    jacobian = np.zeros((NUM_CHANNELS * NUM_ACTIVE_WELLS, NUM_PARAMS * NUM_ACTIVE_WELLS))
    # compute change in parameter to compute derivative
    sign_x0 = np.zeros(len(pos))
    for x in range(0, len(pos)):
        sign_x0[x] = 1 if pos[x] >= 0 else -1

    dx0 = EPS_ADJ * sign_x0 * np.maximum(1.0, np.abs(pos))
    # compute contributions from each magnet
    for axis in range(0, NUM_AXES):
        for magnet in range(0, NUM_ACTIVE_WELLS):
            r = -np.array([xpos[magnet], ypos[magnet], zpos[magnet]]) + manta[axis]  # radii to moment
            r_abs = np.sqrt(np.sum(r**2, axis=1))
            m = compute_moment(theta[magnet], phi[magnet], remn[magnet])

            f0 = (np.transpose(3 * r * np.dot(r, m)) / r_abs**5 - m / r_abs**3)[axis]  # dipole model

            # compute contributions from each parameter of each magnet
            for param_idx, param in enumerate(PARAMS):
                r_pert = r.copy()
                r_abs_pert = r_abs.copy()
                m_pert = m.copy()
                pert = dx0[magnet + NUM_ACTIVE_WELLS * param_idx]  # perturbation of variable
                perturbation_xyz = np.zeros((1, 3))
                perturbation_theta = theta[magnet]
                perturbation_phi = phi[magnet]
                perturbation_remn = remn[magnet]

                if param in ("X", "Y", "Z"):
                    perturbation_xyz[0, param_idx] = pert
                    r_pert = r - perturbation_xyz  # recompute r
                    r_abs_pert = np.sqrt(np.sum(r_pert**2, axis=1))
                else:
                    if param == "THETA":
                        perturbation_theta += pert
                    elif param == "PHI":
                        perturbation_phi += pert
                    else:  # REMN
                        perturbation_remn += pert
                    m_pert = compute_moment(perturbation_theta, perturbation_phi, perturbation_remn)

                f1 = (
                    np.transpose(3 * r_pert * np.dot(r_pert, m_pert)) / r_abs_pert**5
                    - m_pert / r_abs_pert**3
                )[axis]
                # Assign output to column of jacobian
                jacobian[
                    np.arange(0, NUM_AXES * len(f1), 3) + axis, magnet + NUM_ACTIVE_WELLS * param_idx
                ] = (np.transpose(f1 - f0) / DIPOLE_MODEL_FACTOR / dx0[magnet + param_idx * NUM_ACTIVE_WELLS])
    return jacobian


@njit(fastmath=True)  # type: ignore
def objective_function(
    pos: NDArray[(1, Any), float], b_meas: NDArray[(1, Any), float], manta: NDArray[MANTA_SHAPE, float]
) -> NDArray[
    (Any,), float
]:  # pragma: no cover  # Tanner (1/9/22): codecov cannot cover functions compiled with numba
    """Cost function."""
    xpos, ypos, zpos, theta, phi, remn = pos.reshape(NUM_PARAMS, NUM_ACTIVE_WELLS)

    fields = np.zeros((NUM_SENSORS * NUM_ACTIVE_WELLS, NUM_AXES))
    fields_from_magnet = np.zeros((NUM_SENSORS * NUM_ACTIVE_WELLS, NUM_AXES))

    for magnet in range(0, NUM_ACTIVE_WELLS):
        for axis in range(0, NUM_AXES):
            m = compute_moment(theta[magnet], phi[magnet], remn[magnet])

            r = -np.asarray([xpos[magnet], ypos[magnet], zpos[magnet]]) + manta[axis]  # radii to moment
            r_abs = np.sqrt(np.sum(r**2, axis=1))

            # simulate fields at sensors using dipole model for each magnet
            fields_from_magnet[:, axis] = (
                (np.transpose(3 * r * np.dot(r, m)) / r_abs**5 - m / r_abs**3) / DIPOLE_MODEL_FACTOR
            )[axis]
        fields += fields_from_magnet

    return fields.reshape((1, NUM_AXES * len(r)))[0] - b_meas


def get_positions(
    data: NDArray[(NUM_ACTIVE_WELLS * NUM_CHANNELS, Any), float],
    **initial_guess_config: Dict[str, Union[int, float]],
) -> Dict[str, NDArray[(1, Any), float]]:
    """Run the least squares optimizer on instrument data to get magnet
    positions. Assumes 3 active sensors for each well, that all active wells
    have magnets, and that all magnets have the well beneath them active.

    Args:
        data: an array indexed as [TODO]. Data
            should be the difference of the data with plate on the instrument
            and empty plate calibration data.
        initial_guess_config: custom initial guess values
    """
    initial_guess_values = dict(DEFAULT_INITIAL_GUESS_VALUES)
    if initial_guess_config:  # pragma: no cover
        if invalid_params := set(initial_guess_config) - set(initial_guess_values):
            raise ValueError(f"Invalid param(s) in initial_guess_config: {invalid_params}")
        initial_guess_values.update(initial_guess_config)
        # Tanner (3/20/23): Due to the walking initial guess no longer allowing the initial X guess to be overridden.
        # It needs to start at this value to ensure the entire range of possible X values is tested
        initial_guess_values["X"] = DEFAULT_INITIAL_GUESS_VALUES["X"]

    # Tanner (12/2/21): Every well/sensor/axis will always be active as of now
    active_wells = np.arange(NUM_ACTIVE_WELLS)

    # Kevin (12/1/21): Manta gives the locations of all active sensors on all arrays with respect to a common point
    # computing the locations of each centrally located point about which each array is to be distributed,
    # for the purpose of offsetting the values in triad by the correct well spacing
    # The values in "triad" and "manta" relate to layout of the board itself so they don't change at all so long as the board doesn't
    triad = SENSOR_DISTANCES_FROM_CENTER_POINT.copy()
    manta = np.zeros((triad.shape[0] * NUM_ACTIVE_WELLS, triad.shape[1]))
    for well_idx in range(0, NUM_ACTIVE_WELLS):
        well_slice = slice(well_idx * triad.shape[0], (well_idx + 1) * triad.shape[0])
        manta[well_slice, :] = (
            triad
            + well_idx % WELLS_PER_COL * WELL_VERTICAL_SPACING
            + (well_idx // WELLS_PER_COL) * WELL_HORIZONTAL_SPACING
        )

    # Sensing element locations (listed as component_position) [[x_x, y_y, z_z], [y_x, y_y, y_z], [z_x, z_y, z_z]]

    sensor_offsets = np.array([[0, 0, 0], [0, 0.7, 0], [0, 0.6, 0]])

    manta_xyz = np.tile(manta, (3, 1, 1))

    for i in range(0, 3):
        manta_xyz[i] = manta_xyz[i] + sensor_offsets[i]

    # Kevin (12/1/21): Each magnet has its own positional coordinates and other characteristics depending on where it's located in the consumable. Every magnet
    # position is referenced with respect to the center of the array beneath well A1, so the positions need to be adjusted to account for that, e.g. the magnet in
    # A2 has the x/y coordinate (19.5, 0), so guess is processed in the below loop to produce that value. prev_guess contains the guesses for each magnet at each position
    prev_guess = [
        initial_guess_values["X"] - ADJACENT_WELL_DISTANCE_MM * (well_idx // WELLS_PER_COL)
        for well_idx in active_wells
    ]
    prev_guess.extend(
        [
            initial_guess_values["Y"] + ADJACENT_WELL_DISTANCE_MM * (well_idx % WELLS_PER_COL)
            for well_idx in active_wells
        ]
    )
    for param in list(initial_guess_values.keys())[2:]:
        prev_guess.extend([initial_guess_values[param]] * NUM_ACTIVE_WELLS)

    params = tuple(initial_guess_values.keys())
    estimations = {param: np.zeros((data.shape[-1], NUM_ACTIVE_WELLS)) for param in params}

    # Tanner (12/8/21): should probably add some sort of logging eventually
    # Kevin (12/1/21): Run the algorithm on each time index. The algorithm uses its previous outputs as its initial guess for all datapoints but the first one
    optimal_initial_guess_found = False
    # change x position guess incrementally, uniformly for all wells until the algorithm converges properly
    for _ in range(0, 10):
        b_meas = data[:, 0]
        # increment previous guess
        prev_guess = prev_guess + np.append(
            np.ones(NUM_ACTIVE_WELLS) * -GUESS_INCR, np.zeros((NUM_PARAMS - 1) * NUM_ACTIVE_WELLS)
        )

        res = least_squares(
            objective_function,
            prev_guess,
            args=(b_meas, manta_xyz),
            method="lm",
            ftol=1e-1,
            verbose=0,
            jac=compute_jacobian,
        )

        if optimal_initial_guess_found := res.optimality < 1e-5:
            break

    # Luci (05/10/23) raise exception if no guess is found. Will be caught and displayed to user.
    if not optimal_initial_guess_found:
        raise UnableToConvergeError()

    for data_idx in range(0, data.shape[-1]):
        b_meas = data[:, data_idx]

        res = least_squares(
            objective_function,
            prev_guess,
            args=(b_meas, manta_xyz),
            method="lm",
            ftol=1e-1,
            verbose=0,
            jac=compute_jacobian,
        )

        # Tanner (12/2/21): set the start of all subsequent loops as the estimation from the first loop
        prev_guess = np.array(res.x)  # type: ignore

        outputs = np.asarray(res.x).reshape(NUM_PARAMS, NUM_ACTIVE_WELLS)
        for i, param in enumerate(params):
            estimations[param][data_idx, :] = outputs[i]

    return estimations
