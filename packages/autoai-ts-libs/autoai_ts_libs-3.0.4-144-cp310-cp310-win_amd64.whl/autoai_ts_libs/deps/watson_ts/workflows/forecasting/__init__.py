"""
Expose some workflows (pipelines) at the higher level
"""

# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import (
    fctk_pipeline,
    fctk_pipeline_factory_task,
    srom_differenceflattenautoensemble,
    srom_flattenautoensemble,
    srom_localizedflattenautoensemble,
    srom_normalizedflattenautoensemble,
    wts_fctk_extension,
)

# Workflow classes hoisted to the top level
# NOTE: These must come after the module imports so that the workflow modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
