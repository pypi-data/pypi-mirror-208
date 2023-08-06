from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator, TransformerMixin


class StateSpaceEstimator(ABC):
    """
    == BASE / ABSTRACT == \
    An Forecaster class implements the default version of the pipeline which other Auto pipelines \
    will build upon.
    """

    @abstractmethod
    def fit(self, X, y=None):
        pass

    @abstractmethod
    def predict(self, X):
        pass


class StateSpaceTransformer(BaseEstimator, TransformerMixin):
    """
    == BASE / ABSTRACT == \
    An Forecaster class implements the default version of the pipeline which other Auto pipelines \
    will build upon.
    """

    @abstractmethod
    def fit(self, X, y=None):
        pass

    @abstractmethod
    def transform(self, X):
        pass
