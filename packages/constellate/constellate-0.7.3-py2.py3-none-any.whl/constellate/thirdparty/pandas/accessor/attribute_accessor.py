import re
from functools import partial
from typing import Union, Any, Dict

import pandas as pd
from pandas import (
    DatetimeIndex,
    TimedeltaIndex,
    PeriodIndex,
    RangeIndex,
    CategoricalIndex,
    MultiIndex,
    Index,
)
from pandas.core.indexes.extension import ExtensionIndex

# from pandas.core.indexes.numeric import NumericIndex, Int64Index, UInt64Index, Float64Index
from typing_extensions import TypeAlias

PandasObject: TypeAlias = Union[pd.DataFrame, pd.Series]


def _fget(self, obj=None, name=None) -> Union[Any, pd.Series]:
    return obj[name]


def _fset(self, value, obj=None, name=None) -> None:
    obj[name] = value


def _fdel(self, obj=None, name=None) -> None:
    del obj[name]


class _AttributeAccessor:
    _RENAME_REGEX = re.compile(r"[^A-Za-z0-9 ]+", re.IGNORECASE)

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._generate_accessor_properties(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # No validation for now
        pass

    def _generate_accessor_properties(self, pandas_obj):
        def _rename(name) -> str:
            return _AttributeAccessor._RENAME_REGEX.sub("", name)

        # Find space free name, without conflict
        names = [_rename(name) for name in self._get_names(pandas_obj)]
        assert len(set(names)) == len(names)

        # Generate properties
        props = {
            name: property(
                partial(_fget, obj=pandas_obj, name=name),
                partial(_fset, obj=pandas_obj, name=name),
                partial(_fdel, obj=pandas_obj, name=name),
            )
            for name in names
        }

        self._add_properties(instance=self, props=props)

    def _add_properties(self, instance: Any = None, props: Dict = None):
        # src: https://stackoverflow.com/a/49031311/219728
        class_name = instance.__class__.__name__ + "Child"
        child_class = type(class_name, (instance.__class__,), props)

        instance.__class__ = child_class

    def _get_names(self, pandas_obj):
        raise NotImplementedError("Sub class must implement")


@pd.api.extensions.register_dataframe_accessor("aa")
class DataFrameAttributeAccessor(_AttributeAccessor):
    def _get_names(self, pandas_obj):
        return list(pandas_obj.columns)


@pd.api.extensions.register_series_accessor("aa")
class SeriesAttributeAccessor(_AttributeAccessor):
    def _get_names(self, pandas_obj):
        index = pandas_obj.index
        if (
            isinstance(
                pandas_obj,
                (
                    RangeIndex,
                    CategoricalIndex,
                    MultiIndex,
                    DatetimeIndex,
                    TimedeltaIndex,
                    PeriodIndex,
                    ExtensionIndex,
                ),
            )
            or isinstance(pandas_obj, Index)
            and pandas_obj.dtype in ["int64", "uint64", "float64"]
        ):
            # Pandas 2.x removed: NumericIndex, Int64Index, UInt64Index, Float64Index,
            raise NotImplementedError(f"{type(index)}")
        return list(index.values)
