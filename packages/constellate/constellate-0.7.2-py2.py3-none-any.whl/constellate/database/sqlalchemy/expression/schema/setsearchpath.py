from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateSchema as SQACreateSchema
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from typing import List, Union

from sqlalchemy.sql import ClauseElement, Executable


class SetSearchPathSchema(Executable, ClauseElement):
    """Change the search path for database supporting schemas"""

    def __init__(
        self,
        names: Union[str, List[str]] = None,
        ignore_unsupported_database_types: List[str] = None,
        **kw,
    ) -> None:
        super().__init__(**kw)

        if names is None:
            names = []
        elif isinstance(names, str):
            names = [names]

        self._option_schema_names = names
        self._option_ignore_unsupported_database_types = ignore_unsupported_database_types or []


def _visit_searchpath_schema_generic(
    element: SetSearchPathSchema, compiler: PGDDLCompiler, db_type: str = None, **kw
) -> str:
    if db_type in element._option_ignore_unsupported_database_types:
        return "NULL"
    raise NotImplementedError()


@compiles(SetSearchPathSchema)
def _visit_searchpath_schema(element: SetSearchPathSchema, compiler: PGDDLCompiler, **kw) -> str:
    _visit_searchpath_schema_generic(element, compiler, **kw)


@compiles(SetSearchPathSchema, "sqlite")
def _visit_searchpath_schema(element: SetSearchPathSchema, compiler: PGDDLCompiler, **kw) -> str:
    _visit_searchpath_schema_generic(element, compiler, db_type="sqlite", **kw)


@compiles(SetSearchPathSchema, "postgresql")
def _visit_searchpath_schema(element: SetSearchPathSchema, compiler: PGDDLCompiler, **kw) -> str:
    schema_names = ",".join(element._option_schema_names)
    return f"SET search_path TO {schema_names}"
