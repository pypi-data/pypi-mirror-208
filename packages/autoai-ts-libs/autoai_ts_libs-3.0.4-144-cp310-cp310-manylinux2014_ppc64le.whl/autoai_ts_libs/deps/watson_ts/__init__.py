"""
The Watson TS library provides a unified python interface for Watson timeseries
alogirthms through Watson Core.
"""

# First Party
from autoai_ts_libs.deps.watson_core import beta
from autoai_ts_libs.deps.watson_core.model_manager import *
import import_tracker

# Local
from . import config
from .config import *
from .toolkit.extras import get_extras_modules

# Import the core workloads of the library with lazy import errors to allow for
# independent dependency sets


with import_tracker.lazy_import_errors(get_extras_modules=get_extras_modules):
    # Local
    from . import blocks, workflows
