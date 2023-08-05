# -*- coding: utf-8 -*-
import os
from typing import Any
from typing import Tuple

from h5py import File
from nptyping import NDArray
import numpy as np

from .constants import NUM_ACTIVE_WELLS
from .constants import NUM_SENSORS
from .constants import TISSUE_SENSOR_READINGS
from .constants import TWENTY_FOUR_WELL_PLATE


# Beta 2 Memsic to magnetic field conversion factors. Valid as of 11/19/21
MEMSIC_CENTER_OFFSET = 2**15
MEMSIC_MSB = 2**16
MEMSIC_FULL_SCALE = 16
GAUSS_PER_MILLITESLA = 10

ARRAY_SHAPE_TYPE = (NUM_ACTIVE_WELLS * NUM_SENSORS, Any)


def calculate_magnetic_flux_density_from_memsic(
    memsic_data: NDArray[ARRAY_SHAPE_TYPE, int]
) -> NDArray[ARRAY_SHAPE_TYPE, np.float64]:
    """Convert raw data from memsic sensor into magnetic flux density.

    Conversion values are valid as of 11/19/2021

    Args:
        memsic_data: A 216xN array of raw memsic signal

    Returns:
        A 216xN array of magnetic flux density
    """
    samples_in_milliteslas = (
        (memsic_data.astype(np.int64) - MEMSIC_CENTER_OFFSET)
        * MEMSIC_FULL_SCALE
        / MEMSIC_MSB
        / GAUSS_PER_MILLITESLA
    )
    return samples_in_milliteslas.astype(np.float64)


def load_h5_folder_as_array(
    path_to_recording_folder: str,
) -> Tuple[NDArray[ARRAY_SHAPE_TYPE], NDArray[ARRAY_SHAPE_TYPE]]:

    datas = (np.empty((0,), dtype=np.float64), np.empty((0,), dtype=np.float64))

    for data, is_calibration_file in zip(datas, (False, True)):
        recording_name = _get_recording_name(path_to_recording_folder, is_calibration_file)

        for well_idx in range(24):
            well_name = TWENTY_FOUR_WELL_PLATE.get_well_name_from_well_index(well_idx)
            file_path = os.path.join(path_to_recording_folder, f"{recording_name}__{well_name}.h5")
            with File(file_path, "r") as well_file:
                tissue_data = np.array(well_file[TISSUE_SENSOR_READINGS][:], dtype=np.float64)

            if data.shape == (0,):
                # if the array hasn't been created yet, do that now that the number of samples is known
                num_samples = tissue_data.shape[-1]
                data.resize((24 * 9, num_samples), refcheck=False)

            reshaped_data = tissue_data.reshape((9, num_samples))
            data[well_idx * 9 : well_idx * 9 + 9, :] = reshaped_data

        if data.shape == (0,):  # pragma: no cover
            raise ValueError("No data found in files")

    return datas


def _get_recording_name(path_to_recording_folder: str, calibration: bool) -> str:
    first_h5_file = next(  # pragma: no cover
        f
        for f in os.listdir(path_to_recording_folder)
        if (("Calibration" in f) is calibration) and f.endswith(".h5")
    )
    # remove the well name
    recording_name = "__".join(first_h5_file.split("__")[:-1])
    return recording_name
