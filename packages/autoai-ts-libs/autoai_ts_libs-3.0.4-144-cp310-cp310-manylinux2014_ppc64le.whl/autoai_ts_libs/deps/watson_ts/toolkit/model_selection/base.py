# Standard
from contextlib import contextmanager
from typing import Any, Dict
import copy

# Third Party
import numpy as np

# First Party
import alog

# Local
from autoai_ts_libs.deps.watson_ts.data_model import AnyTimeSeriesType
from autoai_ts_libs.deps.watson_ts.toolkit.timeseries_conversions import to_ndarray

log = alog.use_channel("CrossValidator")


class CrossValidator:
    """Base class for all cross-validators
    Implementations must define `_iter_test_masks` or `_iter_test_indices`.
    """

    __doc__ = __doc__
    # _WRAPPED_CLASS = WrappedEstimator
    _TS_COL_PARAM = None
    _INTERNAL_TIMESERIES_TYPE = "numpy"

    # Set this if the wrapped model needs to find one or more value columns
    # using a member attribute
    _VAL_COLS_PARAM = None

    def __init__(self, *args, **kwargs):
        """Construct the underlying model unless the model is given directly"""
        # Set up the internal model either from a prebuilt model or by
        # delegating the init args to the wrapped class
        cls = self.__class__
        model = kwargs.pop("model", None)
        log.debug("Constructing with wrapper model arguments")
        self._wrapped_model = cls._WRAPPED_CLASS(*args, **kwargs)
        self._has_col_params = any(
            [col is not None for col in [cls._TS_COL_PARAM, cls._VAL_COLS_PARAM]]
        )

    @contextmanager
    def _convert_to_internal_timeseries_type(
        self,
        timeseries: AnyTimeSeriesType,
        **kwargs,
    ) -> AnyTimeSeriesType:
        """Shared conversion wrapper for arbitrary input timeseries types. This
        wrapper will, if configured to do so, update the local params to point
        to the post-conversion columns, then return them after the context
        exits.

        WARNING: This is NOT thread safe! If multiple threads enter contexts
            concurrently with different values, they may conflict with each
            other badly! In a multi-threaded environment, conversion args that
            are managed as instance params should not be used.
        """

        # Shallow copy the kwargs so that mutating ops don't accidentally
        # mutate a shared kwargs dict
        kwargs = copy.copy(kwargs)

        cls = self.__class__
        if cls._INTERNAL_TIMESERIES_TYPE == "numpy":
            timeseries = to_ndarray(timeseries)
        yield timeseries, kwargs

    def split(
        self, timeseries: AnyTimeSeriesType, *args, **kwargs
    ) -> AnyTimeSeriesType:
        with self._convert_to_internal_timeseries_type(timeseries, **kwargs) as (
            timeseries,
            kwargs,
        ):
            return self._wrapped_model.split(timeseries, *args, **kwargs)
