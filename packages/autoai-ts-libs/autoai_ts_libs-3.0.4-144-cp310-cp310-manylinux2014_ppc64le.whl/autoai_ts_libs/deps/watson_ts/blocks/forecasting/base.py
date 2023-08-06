"""
Shared baseclass for forecasting blocks. Forecaster blocks are Predictors at a
minimum. Most will also inherit from EstimatorBlockBase and implement fit() when
training is needed.
"""

# Local
from ..base import PredictorBlockBase


class ForecasterBase(PredictorBlockBase):
    __doc__ = __doc__


class PipelineBase(PredictorBlockBase):
    """Shared base class for pipeline blocks"""
