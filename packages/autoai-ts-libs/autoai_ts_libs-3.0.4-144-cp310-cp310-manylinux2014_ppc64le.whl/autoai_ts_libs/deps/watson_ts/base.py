"""
Base classes for watson_ts
"""

# Standard
from typing import Any, Dict, Union
import abc

# Third Party
from sklearn.base import BaseEstimator

# Local
from autoai_ts_libs.deps.watson_ts.data_model import AnyTimeSeriesType

## Abstract Base Classes #######################################################
#
# The classes below define the set of abstract types used throughout this
# library. They enforce standarad method signatures in order to match the
# expected sklearn interfaces (which are NOT enforced as abstract interfaces)
##


class EstimatorBase(BaseEstimator, abc.ABC):
    """The EstimatorBase base class defines the abstract interface for
    modules which can be trained.
    """

    @abc.abstractmethod
    def fit(
        self,
        X: AnyTimeSeriesType,
        *_,
        **kwargs: Dict[str, Any],
    ) -> "EstimatorBase":
        """The fit method performs from-scratch fitting using the configured
        parameter set on the instance. This implements the Estimator type in the
        sklearn ecosystem.

        Ref: https://scikit-learn.org/stable/developers/develop.html#different-objects

        Args:
            X:  AnyTimeSeriesType
                The timeseries data to fit the model to.

        Kwargs:
            **kwargs:  Dict[str, any]
                Additional keyword arguments that can influence the fit
                operation.

        Returns:
            self:  EstimatorBase
                The fit operation should return a handle to itself. This is used
                for function chaining in standard sklearn style code.
        """


class MutableEstimatorBase(EstimatorBase):
    """The MutableEstimatorBase base extends the EstimatorBase
    interface to require an implementation of partial_fit which can take
    additional timeseries data and update the in-memory model.
    """

    @abc.abstractmethod
    def partial_fit(
        self,
        X: AnyTimeSeriesType,
        *_,
        **kwargs: Dict[str, Any],
    ) -> "MutableEstimatorBase":
        """The partial_fit method performs incremental fitting using the
        newly available timeseries data to update the current model.

        Ref: https://scikit-learn.org/0.15/modules/scaling_strategies.html#incremental-learning

        Args:
            X:  AnyTimeSeriesType
                The timeseries data to fit the model to.

        Kwargs:
            **kwargs:  Dict[str, any]
                Additional keyword arguments that can influence the fit
                operation.

        Returns:
            self:  MutableEstimatorBase
                The fit operation should return a handle to itself. This is used
                for function chaining in standard sklearn style code.
        """


class PredictorBase(EstimatorBase):
    """The PredictorBase adds the required `predict` method signature
    needed to implement sklearn's Predictor concept for a timeseries module.
    """

    @abc.abstractmethod
    def predict(
        self,
        X: AnyTimeSeriesType,
        *_,
        **kwargs: Dict[str, Any],
    ) -> Union[AnyTimeSeriesType, int, tuple, dict]:
        """The predict method performs a non-mutating prediction operation using
        the trained model's parameters. This implements the Predictor type in
        the sklearn ecosystem.

        Ref: https://scikit-learn.org/stable/developers/develop.html#different-objects

        Args:
            X:  AnyTimeSeriesType
                The timeseries over which to perform prediction

        Kwargs:
            **kwargs:  Dict[str, any]
                Additional keyword arguments that can influence the predict
                operation.

        Returns:
            prediction_timeseries:  AnyTimeSeriesType
                An updated timeseries with values produced via run added as an
                additional value column
        """


class TransformerBase(EstimatorBase):
    """The TransformerBase adds the required `transform` method signature
    needed to implement sklearn's Transformer concept for a timeseries module. It
    also adds a default implementation of fit() which does nothing in order to
    allow children to implement stateless transformers.
    """

    @abc.abstractmethod
    def transform(
        self,
        X: AnyTimeSeriesType,
        *_,
        **kwargs: Dict[str, Any],
    ) -> AnyTimeSeriesType:
        """The transform method performs a non-mutating transformation operation
        on the input data series using the trained model's parameters. This
        implements the Transformer type in the sklearn ecosystem.

        Ref: https://scikit-learn.org/stable/developers/develop.html#different-objects

        Args:
            X:  AnyTimeSeriesType
                The timeseries object to be transformed

        Kwargs:
            **kwargs:  Dict[str, any]
                Additional keyword arguments that can influence the predict
                operation.

        Returns:
            transformed_timeseries:  AnyTimeSeriesType
                A timeseries with the defined transformation applied
        """

    def fit(self, *_, **__) -> "TransformerBase":
        """By default, a Transformer is stateless, so the fit() operation is a
        no-op. Transformers which need to maintain state should override this
        default implementation.

        Returns:
            self:  TransformerBase
                This method always returns the instance itself for chaining
        """
        return self
