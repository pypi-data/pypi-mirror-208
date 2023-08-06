"""
Anomaly detection workflows solve the problem of taking a raw timeseries,
performing any necessary transformations, and then running an anomaly detection
algorithm on the results.
"""

# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import (
    srom_deep_ad,
    srom_extended_window_ad,
    srom_pred_ad,
    srom_reconstruct_ad,
    srom_relationship_ad,
    srom_window_ad,
)

# Workflow classes hoisted to the top level
# NOTE: These must come after the module imports so that the workflow modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
