"""
Shared baseclasses for anomaly detection pipelines. Anomaly pipelines support fit, predict, anomaly_score.
"""

# Standard
import abc

# Third Party
import numpy as np
import pandas as pd

# First Party
from autoai_ts_libs.deps.watson_core.toolkit import error_handler
import alog

# Local
from ...data_model import AnyTimeSeriesType
from ...toolkit.types import ADReturnTypes, PredictionTypes
from ..base import TSWorkflowBase
from ..sklearn_mixins import SKLearnWorkflowMixin

log = alog.use_channel("AD_WF_BSE")
error = error_handler.get(log)


class AnomalyDetectorWorkflowBase(TSWorkflowBase):
    __doc__ = __doc__

    @abc.abstractmethod
    def anomaly_score(
        self, timeseries: AnyTimeSeriesType, *args, **kwargs
    ) -> AnyTimeSeriesType:
        """The anomaly_score methods provides an indication of the degree of abnormality

        Args:
            timeseries: AnyTimeSeriesType
                The timeseries data to fit the model to.

        Kwargs:
            **kwargs: Dict[str, any]
                Additional keyword arguments that can influence the anomaly_score
                operation.

        Returns:
            anomaly_score: AnyTimeSeriesType
                The anomaly score is another time series where the values indicate the
                degree of abnormality
        """


class SKLearnAnomalyDetectorWorkflowMixin(
    SKLearnWorkflowMixin, AnomalyDetectorWorkflowBase
):
    """
    Mixin for sklearn native anomaly detector workflows
    """

    def anomaly_score(self, X: AnyTimeSeriesType, *args, **kwargs) -> AnyTimeSeriesType:
        """Delegate anomaly_score to the wrapped pipeline"""
        with self._convert_to_internal_timeseries_type(X, **kwargs) as (
            X,
            kwargs,
        ):
            return self._wrapped_model.anomaly_score(X, *args, **kwargs)


class SROMAnomalyMixin(SKLearnAnomalyDetectorWorkflowMixin):
    """
    Mixin for managing aspects of SROM specific anomaly pipelines
    """

    def __init__(self, *args, **kwargs):
        if "steps" in kwargs:
            kwargs["steps"] = self.__class__._unwrap_steps(kwargs["steps"])

        super().__init__(*args, **kwargs)

    def run(
        self,
        X: AnyTimeSeriesType,
        prediction_type=PredictionTypes.Sliding.value,
        return_type=ADReturnTypes.Labels.value,
    ) -> AnyTimeSeriesType:
        """Create a single-row array and delegate to predict or anomaly_score

        Args:
            X: AnyTimeSeriesType
                Time series input to provide predictions for.
            prediction_type: str, default=PredictionTypes.Sliding.value
                (Optional) Type of prediction requested, used to get both binary labels and anomaly scores. Options are available in PredictionTypes.
            return_type: str, default=ADReturnTypes.Labels.value
                (Optional) Type of output requested, options are ADReturnTypes.Labels to get binary label predictions and ADReturnTypes.Scores for anomaly scores.

        Returns:
            AnyTimeSeriesType
                The output predictions with labels or anomaly scores for the given timeseries data.
        """

        error.value_check(
            "<WTS94662986F>",
            (return_type in [val.value for val in ADReturnTypes]),
            "Invalid return_type {}, only options in ADReturnTypes are supported.",
            return_type,
        )

        if return_type is ADReturnTypes.Labels.value:
            return self.predict(X, prediction_type=prediction_type)

        if return_type is ADReturnTypes.Scores.value:
            return self.anomaly_score(X, prediction_type=prediction_type)

    def predict(self, X: AnyTimeSeriesType, *args, **kwargs) -> AnyTimeSeriesType:
        """Predict method. Calls the predict method of the superclass, but handles the prediction
        type appropriately.

        Args:
            X (AnyTimeSeriesType): Time series input

        Returns:
            AnyTimeSeriesType: Output predictions
        """

        if "prediction_type" not in kwargs:
            kwargs["prediction_type"] = PredictionTypes.Sliding.value

        return super().predict(X, *args, **kwargs)

    def anomaly_score(self, X: AnyTimeSeriesType, *args, **kwargs) -> AnyTimeSeriesType:
        """Anomaly score method. Calls the anomaly score method of the superclass, but handles the prediction
        type appropriately.

        Args:
            X (AnyTimeSeriesType): Time series input

        Returns:
            AnyTimeSeriesType: Output predictions
        """

        if "prediction_type" not in kwargs:
            kwargs["prediction_type"] = PredictionTypes.Sliding.value

        return super().anomaly_score(X, *args, **kwargs)

    @classmethod
    def _unwrap_steps(cls, steps):
        return [(name_, cls._unwrap_object(step)) for name_, step in steps]
