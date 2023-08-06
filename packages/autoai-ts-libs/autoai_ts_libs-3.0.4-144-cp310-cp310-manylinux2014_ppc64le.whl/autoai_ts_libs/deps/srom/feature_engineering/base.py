# IBM Confidential Materials
# Licensed Materials - Property of IBM
# IBM Smarter Resources and Operation Management
# (C) Copyright IBM Corp. 2021 All Rights Reserved.
# US Government Users Restricted Rights
#  - Use, duplication or disclosure restricted by
#    GSA ADP Schedule Contract with IBM Corp.


"""
.. module:: base
   :synopsis: Contains DataTransformer class.

.. moduleauthor:: SROM Team
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances


class DataTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """

    def __init__(self):
        """Init method"""
        pass

    def fit(self, X, y=None):
        """
        Fit method.
        Parameters:
            X (pandas.DataFrame, required): Training set.
            y (pandas.DataFrame, optional):
        """
        X = check_array(X, accept_sparse=True)
        self.n_features_ = X.shape[1]
        return self

    def transform(self, X):
        """
        Parameters:
            X (pandas.DataFrame, required): Training set.
        """
        check_is_fitted(self, "n_features_")
        X = check_array(X, accept_sparse=True)

        if X.shape[1] != self.n_features_:
            raise ValueError(
                "Shape of input is different from what was seen" "in `fit`"
            )
        pass


class ColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """


class StateFulTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """


class TargetTransformer(BaseEstimator, TransformerMixin):
    """
    Base transformer class in which the number of rows is \
    preserved during transformation.
    """

    def inverse_transform(self, y):
        pass
