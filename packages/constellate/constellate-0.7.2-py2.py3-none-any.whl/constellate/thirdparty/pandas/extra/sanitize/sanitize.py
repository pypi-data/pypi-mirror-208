from typing import List, Union, Dict

import inspect
import itertools
import pandas
import pandas as pd
import pandera.dtypes
from pandera.api.pandas.components import Index, MultiIndex, Column
from pandas import DataFrame, Series
from typing import Union, Any
from typing_extensions import TypeAlias
from typing import get_origin
from constellate.thirdparty.pandas.validation.validation import (
    PanderaSchema,
    pandera_schema_from_pydantic_schema,
)


def fillnone(df: DataFrame = None, column_names: List[str] = None) -> None:
    """Convert pandas.NA into None

    :param df: DataFrame:  (Default value = None)
    :param column_names: List[str]:  (Default value = None)

    """

    def _to_none(x):
        return None if isinstance(x, type(pandas.NA)) else x

    for col_name in column_names:
        # Turn nan/NaN/NAType into None
        # pandas v1.3.4: Works
        # pandas v1.4.0: Not Works
        # chunk[col_name] = chunk[col_name].replace({pandas.NA, None})

        # pandas v1.3.4: Untested
        # pandas v1.4.0: Works
        df[col_name] = df[col_name].apply(_to_none)


PandasData: TypeAlias = Union[DataFrame, Series]


def fill_missing_from_schema(schema: [PanderaSchema] = None, data: PandasData = None) -> PandasData:
    """Convert None into NaN or equivalent, convert index/colum dtype to schema type

    :param schema: [PanderaSchema]:  (Default value = None)
    :param data: Union[DataFrame,Series]:  (Default value = None)

    """

    pandera_schema = pandera_schema_from_pydantic_schema(schema=schema)

    #
    # Get index name / dtype pair
    #
    index = pandera_schema.index
    multi_indexed = isinstance(index, MultiIndex)

    indexes = dict()
    has_index = index is not None
    if has_index:
        if multi_indexed:
            indexes = index.columns
        else:
            indexes = _get_index_name_and_dtypes(schema=schema)

    # Get non index name / dtype pairs
    non_indexes = pandera_schema.columns

    # Create missing column name
    for indexed, fields in [(True, indexes.items()), (False, non_indexes.items())]:
        for col_position, (col_name, col_info) in enumerate(itertools.chain(fields)):
            if has_index and indexed:
                data.index = _create_column_name_from_schema(
                    data=data.index,
                    col_name=col_name,
                    col_info=col_info,
                    index=has_index,
                    multi_index=multi_indexed,
                    col_position=col_position,
                )
            else:
                data = _create_column_name_from_schema(
                    data=data,
                    col_name=col_name,
                    col_info=col_info,
                    index=False,
                    multi_index=False,
                    col_position=col_position,
                )

    # Edit column dtype
    for indexed, fields in [(True, indexes.items()), (False, non_indexes.items())]:
        for col_name, col_info in itertools.chain(fields):
            if has_index and indexed:
                data.index = _edit_column_dtype_from_schema(
                    data=data.index,
                    col_name=col_name,
                    col_info=col_info,
                    index=has_index,
                    multi_index=multi_indexed,
                )
            else:
                data = _edit_column_dtype_from_schema(
                    data=data, col_name=col_name, col_info=col_info, index=False, multi_index=False
                )

    return data


def _edit_column_dtype_from_schema(
    data=PandasData,
    col_name: str = None,
    col_info: Any = None,
    index: bool = False,
    multi_index: bool = False,
) -> PandasData:
    def _apply_dtype_dataframe(
        data: pd.DataFrame = None, col_name: str = None, col_type: Any = None
    ) -> pd.DataFrame:
        data[col_name] = data[col_name].astype(col_type)
        return data

    def _apply_dtype_series(
        data: pd.Series = None, col_name: str = None, col_type: Any = None
    ) -> pd.Series:
        data = data.astype(col_type)
        return data

    def _apply_dtype(
        data: PandasData = None, col_name: str = None, col_type: Any = None
    ) -> PandasData:
        if isinstance(data, pd.DataFrame):
            return _apply_dtype_dataframe(data=data, col_name=col_name, col_type=col_type)
        elif isinstance(data, pd.Series):
            return _apply_dtype_series(data=data, col_name=col_name, col_type=col_type)
        elif isinstance(data, pd.Index) and not isinstance(data, pd.MultiIndex):
            return _apply_dtype_series(data=data, col_name=col_name, col_type=col_type)
        else:
            raise NotImplementedError()

    def _to_numeric(data: PandasData = None, col_name: str = None) -> PandasData:
        if isinstance(data, pd.DataFrame):
            data[col_name] = pandas.to_numeric(data[col_name], errors="coerce", downcast=None)
            return data
        elif isinstance(data, pd.Series):
            data = pandas.to_numeric(data, errors="coerce", downcast=None)
            return data
        elif isinstance(data, pd.Index):
            data = pandas.to_numeric(data, errors="coerce", downcast=None)
            return data
        else:
            raise NotImplementedError()

    def _to_datetime(data: PandasData = None, col_name: str = None) -> PandasData:
        if isinstance(data, pd.DataFrame):
            data[col_name] = pandas.to_datetime(data[col_name], errors="coerce")
            return data
        elif isinstance(data, pd.Series):
            data = pandas.to_datetime(data, errors="coerce")
            return data
        elif isinstance(data, pd.Index):
            data = pandas.to_datetime(data, errors="coerce")
            return data
        else:
            raise NotImplementedError()

    def _to_timedelta(data: PandasData = None, col_name: str = None) -> PandasData:
        if isinstance(data, pd.DataFrame):
            data[col_name] = pandas.to_timedelta(data[col_name], errors="coerce")
            return data
        elif isinstance(data, pd.Series):
            data = pandas.to_timedelta(data, errors="coerce")
            return data
        elif isinstance(data, pd.Index):
            data = pandas.to_timedelta(data, errors="coerce")
            return data
        else:
            raise NotImplementedError()

    col_type = col_info.dtype

    data_orig = data
    mono_index = None
    if index and multi_index:
        mono_index = data.get_level_values(col_name)
        data = mono_index

    if pandera.dtypes.is_float(col_type):
        data = _to_numeric(data=data, col_name=col_name)
        # accepts pandas.NA since pandas v1.0.0
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_int(col_type):
        data = _to_numeric(data=data, col_name=col_name)
        # accepts pandas.NA since pandas v1.0.0
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_uint(col_type):
        data = _to_numeric(data=data, col_name=col_name)
        # accepts pandas.NA since pandas v1.0.0
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_bool(col_type):
        # accepts pandas.NA since pandas v1.0.0
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_string(col_type):
        # accepts pandas.NA since pandas v1.0.0
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_datetime(col_type):
        data = _to_datetime(data=data, col_name=col_name)
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)
    elif pandera.dtypes.is_timedelta(col_type):
        data = _to_timedelta(data=data, col_name=col_name)
        data = _apply_dtype(data=data, col_name=col_name, col_type=col_type.type)

    if index and multi_index:
        data = data_orig.set_levels(mono_index, level=col_name, verify_integrity=True)

    return data


def _create_column_name_from_schema(
    data=PandasData,
    col_name: str = None,
    col_info: Any = None,
    index: bool = False,
    multi_index: bool = False,
    col_position: int = None,
) -> PandasData:
    if isinstance(data, pd.DataFrame):
        col_missing = col_name not in data.columns
        if col_missing:
            data.insert(col_position, col_name, [], allow_duplicates=False)
    elif isinstance(data, pd.Series):
        pass
    elif isinstance(data, pd.Index) and not multi_index:
        data.rename(col_name, inplace=True)
    elif isinstance(data, pd.MultiIndex) and multi_index:
        pass
    else:
        raise NotImplementedError()

    return data


def enum_to_value(data: Union[DataFrame, Series] = None, dtypes: Dict = {}) -> None:
    _enum_value = lambda e: e.value
    for col_name in list(data.columns):
        if col_name not in dtypes:
            continue

        data[col_name] = data[col_name].apply(_enum_value)


def get_index_columns(schema: PanderaSchema = None) -> List[str]:
    schema2 = pandera_schema_from_pydantic_schema(schema=schema)
    if isinstance(schema2.index, pandera.api.pandas.components.MultiIndex):
        return list(schema2.index.columns.keys())
    elif isinstance(schema2.index, pandera.api.pandas.components.Index):
        annotations = next(
            iter(filter(lambda m: m[0] == "__annotations__", inspect.getmembers(schema))),
            ("__annotations__", {}),
        )[1]
        index_name = next(
            iter(
                [k for k, v in annotations.items() if get_origin(v) == pandera.typing.pandas.Index]
            ),
            None,
        )
        return [index_name]
    elif schema2.index is None:
        # Case: No index defined in the schema
        return []
    raise NotImplementedError()


def _get_index_name_and_dtypes(schema: PanderaSchema = None) -> Dict[str, Any]:
    schema2 = pandera_schema_from_pydantic_schema(schema=schema)
    if isinstance(schema2.index, pandera.api.pandas.components.MultiIndex):
        raise NotImplementedError("not implemented yet")
        # return list(schema2.index.columns.keys())
    elif isinstance(schema2.index, pandera.api.pandas.components.Index):
        annotations = next(
            iter(filter(lambda m: m[0] == "__annotations__", inspect.getmembers(schema))),
            ("__annotations__", {}),
        )[1]
        name = next(
            iter(
                [k for k, v in annotations.items() if get_origin(v) == pandera.typing.pandas.Index]
            ),
            None,
        )
        if name is None:
            raise ValueError()
        # get_origin(schema.__dict__['__annotations__']['some index name like timestamp']) does not seem to store the index name's dtype.
        # Hence, taking from dtype from schema2
        # Must return a <object> containing property path "dtype.type"
        return {name: schema2.index}
    raise NotImplementedError()
