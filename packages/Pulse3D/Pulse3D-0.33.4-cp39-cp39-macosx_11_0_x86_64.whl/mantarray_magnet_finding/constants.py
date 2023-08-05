# -*- coding: utf-8 -*-
from labware_domain_models import LabwareDefinition

NUM_ACTIVE_WELLS = 24
WELLS_PER_COL = 4

NUM_SENSORS = 3
NUM_AXES = 3
NUM_CHANNELS = NUM_AXES * NUM_SENSORS
GUESS_INCR = 1

TWENTY_FOUR_WELL_PLATE = LabwareDefinition(row_count=4, column_count=6)
TISSUE_SENSOR_READINGS = "tissue_sensor_readings"
