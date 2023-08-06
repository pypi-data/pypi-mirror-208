"""
Base class for watson_ts workflows
"""

# First Party
from autoai_ts_libs.deps.watson_core.workflows.base import WorkflowBase

# Local
from ..base import PredictorBase

## Abstract Base Classes #######################################################
#
# The classes below define the set of abstract workflow type used in this
# library. They enforce standarad method signatures in order to match the
# expected sklearn interfaces (which are NOT enforced as abstract interfaces)
##


class TSWorkflowBase(WorkflowBase, PredictorBase):
    __doc__ = __doc__
