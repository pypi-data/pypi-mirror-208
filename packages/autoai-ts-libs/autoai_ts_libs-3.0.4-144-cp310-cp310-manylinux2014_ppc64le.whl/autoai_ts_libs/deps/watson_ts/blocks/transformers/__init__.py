"""
Transformer blocks perform various data transformations on timeseries data
"""

# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import (
    fctk,
    srom_advanced_summary_statistics,
    srom_data_stationarizer,
    srom_difference_flatten,
    srom_fft_features,
    srom_flatten,
    srom_localized_flatten,
    srom_log,
    srom_summary_statistics,
    srom_ts_min_max_scaler,
    srom_ts_standard_scaler,
    tspy_segmenters,
    tspy_transform_base,
    tspy_transformers,
)

# Block classes hoisted to the top level
# NOTE: These must come after the module imports so that the block modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
