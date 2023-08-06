"""
Base class for watson_ts blocks
"""

# First Party
from autoai_ts_libs.deps.watson_core.blocks.base import BlockBase

# Local
from ..base import EstimatorBase, MutableEstimatorBase, PredictorBase, TransformerBase

## Abstract Base Classes #######################################################
#
# The classes below define the set of abstract block types used throughout this
# library. They enforce standarad method signatures in order to match the
# expected sklearn interfaces (which are NOT enforced as abstract interfaces)
##


class EstimatorBlockBase(BlockBase, EstimatorBase):
    """The EstimatorBlockBase base class defines the abstract interface for
    blocks which can be trained.
    """


class MutableEstimatorBlockBase(BlockBase, MutableEstimatorBase):
    """The MutableEstimatorBlockBase base extends the MutableEstimatorBase
    to support mutuable blocks.
    """


class PredictorBlockBase(BlockBase, PredictorBase):
    """The PredictorBlockBase base extends the PredictorBase to support
    blocks which are predictors.
    """


class TransformerBlockBase(BlockBase, TransformerBase):
    """The TransformerBlockBase extends the TransformerBase to support
    transformer blocks.
    """
