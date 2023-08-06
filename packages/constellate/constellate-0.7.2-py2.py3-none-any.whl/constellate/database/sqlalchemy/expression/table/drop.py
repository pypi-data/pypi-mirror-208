import sys
from typing import List, Union, Iterable

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.base import Executable
from sqlalchemy.dialects.postgresql.asyncpg import PGCompiler_asyncpg
from sqlalchemy.dialects.postgresql.psycopg import PGCompiler_psycopg
from sqlalchemy.dialects.sqlite.base import SQLiteCompiler


class DropTable(Executable, ClauseElement):
    inherit_cache = True

    def __init__(
        self,
        element: Union[object, List[object]] = None,
        if_exists: bool = False,
        cascade: bool = False,
    ) -> None:
        super().__init__()
        self._element = element
        self._option_if_exists = if_exists
        self._option_cascade = cascade


def _visit_drop_generic(
    element: DropTable,
    compiler: Union[SQLiteCompiler, PGCompiler_asyncpg, PGCompiler_psycopg],
    max_table: int = 0,
    db_type: str = None,
    **kw,
) -> str:
    if db_type == "sqlite":
        if element._option_cascade:
            raise ValueError("sqlite: CASCADE not supported")

    pre_options = " ".join(
        filter(lambda x: x is not None, ["IF EXISTS" if element._option_if_exists else None])
    )
    post_options = " ".join(
        filter(lambda x: x is not None, ["CASCADE" if element._option_cascade else None])
    )

    tables = element._element if isinstance(element._element, Iterable) else [element._element]
    tables = [t for t in tables]
    if len(tables) > max_table:
        raise ValueError(
            f"{db_type}: supports no more than {max_table} dropped tables per statement"
        )

    tables = ", ".join([compiler.process(t.__table__, asfrom=True, **kw) for t in tables])
    return "DROP TABLE %s %s %s" % (pre_options, tables, post_options)


@compiles(DropTable)
def _visit_drop_table(element: DropTable, compiler: SQLiteCompiler, **kw) -> str:
    raise NotImplementedError()


@compiles(DropTable, "postgresql")
def _visit_drop_table(element: DropTable, compiler: SQLiteCompiler, **kw) -> str:
    return _visit_drop_generic(element, compiler, max_table=sys.maxsize, db_type="postgresql", **kw)


@compiles(DropTable, "sqlite")
def _visit_drop_table(element: DropTable, compiler: SQLiteCompiler, **kw) -> str:
    return _visit_drop_generic(element, compiler, max_table=1, db_type="sqlite", **kw)
