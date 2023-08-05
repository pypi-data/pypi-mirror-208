from __future__ import annotations

import logging
import typing as t

import pandas as pd

from sarus.dataspec_wrapper import (
    IGNORE_WARNING,
    DataSpecVariant,
    DataSpecWrapper,
)
from sarus.typing import SPECIAL_WRAPPER_ATTRIBUTES
from sarus.utils import (
    create_lambda_op,
    create_method,
    register_ops,
    sarus_init,
    sarus_method,
    sarus_property,
)

logger = logging.getLogger(__name__)


class DataFrame(DataSpecWrapper[pd.DataFrame]):
    @sarus_init("pandas.PD_DATAFRAME")
    def __init__(
        self, data=None, index=None, columns=None, dtype=None, copy=None
    ):
        ...

    @sarus_method("std.SETITEM", inplace=True)
    def __setitem__(self, key, newvalue):
        ...

    @sarus_property("pandas.PD_COLUMNS")
    def columns(self):
        ...

    @sarus_property("pandas.PD_AXES")
    def axes(self):
        ...

    @sarus_property("pandas.PD_DTYPES")
    def dtypes(self):
        ...

    @sarus_property("pandas.PD_INDEX")
    def index(self):
        ...

    @sarus_property("pandas.PD_SHAPE")
    def shape(self):
        ...

    @sarus_property("pandas.PD_NDIM")
    def ndim(self):
        ...

    @sarus_property("pandas.PD_SIZE")
    def size(self):
        ...

    @sarus_property("pandas.PD_VALUES")
    def values(self):
        ...

    @property
    def loc(self) -> _SarusLocIndexer:
        return _SarusLocIndexer(self)

    @property
    def iloc(self) -> _SarusLocIndexer:
        return _SarusILocIndexer(self)

    def __getattr__(self, name: str) -> t.Any:
        # Overload __getattr__ to enable indexing by column name
        if name in IGNORE_WARNING:
            return object.__getattribute__(self, name)

        if name in SPECIAL_WRAPPER_ATTRIBUTES:
            return super().__getattr__(name=name)

        if name in self.__sarus_eval__(verbose=0).columns:
            return self.loc[:, name]

        return super().__getattr__(name=name)

    def __setattr__(self, name: str, value: t.Any) -> None:
        # Overload __setattr__ to enable setting by column name
        if name in SPECIAL_WRAPPER_ATTRIBUTES:
            return super().__setattr__(name, value)

        if name in self.__sarus_eval__().columns:
            key = (slice(None, None), name)
            new_df = _pd_set_loc(self, key, value)
            self._set_dataspec(new_df._dataspec)
            return

        return super().__setattr__(name, value)

    def copy(self, deep: bool = False) -> DataFrame:
        return DataFrame.from_dataspec(
            self.dataspec(kind=DataSpecVariant.USER_DEFINED)
        )


# This registration process is an exception
_pd_loc = create_method(
    "pandas.PD_LOC",
    module_name=__name__,
    class_name="DataFrame",
    method_name="loc",
)
_pd_iloc = create_method(
    "pandas.PD_ILOC",
    module_name=__name__,
    class_name="DataFrame",
    method_name="iloc",
)
_ = create_method(
    "pandas.PD_LOC",
    module_name=__name__,
    class_name="Series",
    method_name="loc",
)
_ = create_method(
    "pandas.PD_ILOC",
    module_name=__name__,
    class_name="Series",
    method_name="iloc",
)
_pd_set_loc = create_lambda_op("pandas.PD_SET_LOC")
_pd_set_iloc = create_lambda_op("pandas.PD_SET_ILOC")


class _SarusLocIndexer:
    def __init__(self, df: DataFrame) -> None:
        self.df = df

    def __getitem__(self, key) -> DataFrame:
        return _pd_loc(self.df, key)

    def __setitem__(self, key, newvalue) -> None:
        new_df = _pd_set_loc(self.df, key, newvalue)
        self.df._set_dataspec(new_df._dataspec)


class _SarusILocIndexer:
    def __init__(self, df: DataFrame) -> None:
        self.df = df

    def __getitem__(self, key) -> DataFrame:
        return _pd_iloc(self.df, key)

    def __setitem__(self, key, newvalue) -> None:
        new_df = _pd_set_iloc(self.df, key, newvalue)
        self.df._set_dataspec(new_df._dataspec)


class Series(DataSpecWrapper[pd.Series]):
    @sarus_init("pandas.PD_SERIES")
    def __init__(
        data=None,
        index=None,
        dtype=None,
        name=None,
        copy=False,
        fastpath=False,
    ):
        ...

    @sarus_method("std.SETITEM", inplace=True)
    def __setitem__(self, key, newvalue):
        ...

    @sarus_property("pandas.PD_INDEX")
    def index(self):
        ...

    @sarus_property("pandas.PD_DTYPE")
    def dtype(self):
        ...

    @sarus_property("pandas.PD_SHAPE")
    def shape(self):
        ...

    @sarus_property("pandas.PD_NDIM")
    def ndim(self):
        ...

    @sarus_property("pandas.PD_SIZE")
    def size(self):
        ...

    @sarus_property("pandas.PD_NAME")
    def name(self):
        ...

    @sarus_property("pandas.PD_VALUES")
    def values(self):
        ...

    def copy(self, deep: bool = False) -> Series:
        return Series.from_dataspec(
            self.dataspec(kind=DataSpecVariant.USER_DEFINED)
        )


register_ops()
