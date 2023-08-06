# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import k_shape

# Block classes hoisted to the top level
# NOTE: These must come after the module imports so that the block modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
