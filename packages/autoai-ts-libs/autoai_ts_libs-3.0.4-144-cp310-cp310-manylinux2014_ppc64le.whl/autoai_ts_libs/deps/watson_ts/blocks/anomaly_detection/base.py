"""
Shared base class for anomaly detection estimators. Anomaly estimators support fit, predict, anomaly_score.
"""

# Standard
import abc
import inspect

# Local
from ...blocks.base import EstimatorBlockBase
from autoai_ts_libs.deps.watson_ts.data_model import AnyTimeSeriesType


class AnomalyDetectorBase(EstimatorBlockBase):
    __doc__ = __doc__

    @abc.abstractmethod
    def anomaly_score(self, X: AnyTimeSeriesType, *args, **kwargs) -> AnyTimeSeriesType:
        """The anomaly_score method provides an indication of the degree of abnormality

        Args:
            X: AnyTimeSeriesType
                The timeseries data to fit the model to.

        Kwargs:
            **kwargs: Dict[str, any]
                Additional keyword arguments that can influence the anomaly_score
                operation.

        Returns:
            anomaly_score: Time series type
                The anomaly score is another time series where the values indicate the
                degree of abnormality
        """


class SKLearnAnomalyDetectorMixin(AnomalyDetectorBase):
    def anomaly_score(self, X: AnyTimeSeriesType, *args, **kwargs) -> AnyTimeSeriesType:
        """Delegate anomaly_score to the wrapped pipeline"""
        with self._convert_to_internal_timeseries_type(X, **kwargs) as (
            X,
            kwargs,
        ):
            return self._wrapped_model.anomaly_score(X, *args, **kwargs)

    def decision_function(
        self, X: AnyTimeSeriesType, *args, **kwargs
    ) -> AnyTimeSeriesType:
        """Delegate decision_score to the wrapped pipeline"""
        with self._convert_to_internal_timeseries_type(X, **kwargs) as (
            X,
            kwargs,
        ):
            return self._wrapped_model.decision_function(X, *args, **kwargs)


class SROMAnomalyDetectorMixin(SKLearnAnomalyDetectorMixin):
    def __init__(self, *args, **kwargs):
        # remap "special" parameters
        if "base_learner" in inspect.signature(self._WRAPPED_CLASS.__init__).parameters:
            if "base_learner" in kwargs:
                kwargs["base_learner"] = self.__class__._unwrap_object(
                    kwargs["base_learner"]
                )
        super().__init__(*args, **kwargs)
