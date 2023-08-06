################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2022, 2023. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import abc

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_array

from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.anomaly_detection.estimators.constants import NON_ANOMALY, ANOMALY


class TSADPipeline(Pipeline):
    def _check_missing(self, X, missing_value=np.NaN):
        """Check whether input matrix include missing values.
           If the input include missing value, raise an error

        Args:
            X (np.ndarray): Input data
            missing_value ([type], optional): Specifies which value to count as missing.
                Useful for applying function on a boolean mask matrix. Defaults to np.NaN.
        """
        X = check_array(X, dtype=np.float64, force_all_finite=False)

        if missing_value is np.NaN:
            missing_nums = np.isnan(X).sum(axis=0)
        else:
            missing_nums = (X == missing_value).sum(axis=0)
        for num in missing_nums:
            if num > 0:
                raise Exception(Messages.get_message(message_id="AUTOAITSADLIB0001E"))
        return X

    def _check_columns(self, X):
        """Check whether the columns of the input data are equal to the columns in the model.
           If not equal, raise an error

        Args:
            X (np.ndarray): Input data
        """
        est = self[-1]

        num_time_columns = 0
        if hasattr(est, 'ts_icol_loc'):
             num_time_columns = len(est.ts_icol_loc)
        elif hasattr(est, 'time_column'):
            if est.time_column is not None and est.time_column != -1:
                num_time_columns = 1

        if hasattr(est, 'target_column_indices'):
            if X.shape[1] != len(est.target_column_indices) and X.shape[1] != len(est.target_column_indices) + num_time_columns:
                raise Exception(Messages.get_message(len(est.target_column_indices), X.shape[1], message_id="AUTOAITSLIBS0105E"))
        elif hasattr(est, 'feature_columns'):
            if X.shape[1] != len(est.feature_columns) and X.shape[1] != len(est.feature_columns) + num_time_columns:
                raise Exception(Messages.get_message(len(est.feature_columns), X.shape[1], message_id="AUTOAITSLIBS0105E"))

    def fit(self, X, y=None, **fit_params):
        return super().fit(X, y=y, **fit_params)

    def predict(self, X=None, **predict_params):
        X = self._check_missing(X)
        #self._check_columns(X)
        return super().predict(X, **predict_params)

    def anomaly_score(self, X=None, **predict_params):
        """Compute anomaly score for provided data.

        This essentially calls transform/predict on steps prior to last step. Underlying assumption 
        is that the last step implements `anomaly_score`.

        Args:
            X (_type_, optional): _description_. Defaults to None.

        Returns:
            ndarray: Output containing anomaly score.
        """

        prep = self[:-1]
        est = self[-1]

        if len(prep) > 0:
            Xtmp = prep.transform(X)
        else:
            Xtmp = X
        # -- ensure scores returned is 2D array of (N,:)
        scores = np.asarray(est.anomaly_score(Xtmp))
        scores = scores.reshape(len(scores), -1)


        '''
                   WindowLOF, XGB, RandomForest return AD scores for each target series
                   So, aggregate (amax/or sum) scores to ensure one score per row, i.e. 
                   return scores = (N,1)
               '''
        if scores.shape[1] > 1:
            scores = np.amax(scores, axis=1, keepdims=True)  # or np.sum
        return scores

    def decision_function(self, X):
        """Implement decision_function required by some metrics, redirects to anomaly_score.

        Args:
            X (np.ndarray): Input time series data

        Returns:
            np.ndarray: Nx1 anomaly score per row of input time series
        """
        return self.anomaly_score(X).reshape(-1, 1)

    def get_pipeline_name(self,):
        _, est = self.steps[-1]
        try:
            return est.get_pipeline_name()
        except AttributeError:
            return None


class TSADEstimator(BaseEstimator):
    @abc.abstractmethod
    def fit(self, X, y=None, **fit_params):
        """Standard fit method"""

    @abc.abstractmethod
    def predict(self, X=None, **predict_params):
        """Standard predict method"""

    @abc.abstractmethod
    def anomaly_score(self, X=None, **predict_params):
        """Anomaly score method"""

    @property
    def classes_(self):
        """The classes labels."""
        return np.array([NON_ANOMALY, ANOMALY])
