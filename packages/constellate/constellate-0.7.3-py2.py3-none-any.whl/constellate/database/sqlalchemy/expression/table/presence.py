from typing import Any, Union

from sqlalchemy import func, column, case, Boolean, select
from sqlalchemy.util import immutabledict
from sqlalchemy.dialects.postgresql import REGCLASS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import Select
from sqlalchemy.sql import Executable, ClauseElement


async def has_table(
    session: AsyncSession = None,
    shard_id: str = None,
    shard_schema_id: str = None,
    table: Any = None,
) -> bool:
    # FIXME (high) has_table is also available in sqlalchemy/dialects/postgres/base.py (and other backends)
    # FIXME (high) Public API is Inspector.has_table` and legacy API is ` _engine.Engine.has_table`
    # FIXME (high) Use default shema returned by https://docs.sqlalchemy.org/en/14/core/reflection.html?highlight=inspector#sqlalchemy.engine.reflection.Inspector

    # SELECT to_regclass('schema_name.table_name');
    # src: https://stackoverflow.com/a/24089729/219728

    # SELECT (CASE WHEN found IS NULL
    #             THEN False
    #             ELSE True
    #        END) AS found
    # FROM ( SELECT CAST(to_regclass('some_schema_name.some_table_name') AS REGCLASS) ) AS found

    stmt_0 = select(func.to_regclass(table.__tablename__).cast(REGCLASS).label("result")).subquery()
    column_result = column("result")
    stmt_1 = select(
        case((column_result.is_(None), False), else_=True).label("found").cast(Boolean)
    ).select_from(stmt_0)

    # Note: Only compatible with (Sync)MultiEngineShardSession instances
    bind_arguments = {"shard_id": shard_id}
    execution_options = {"shard_schema_id": shard_schema_id}

    value = (
        await session.execute(
            stmt_1,
            bind_arguments=bind_arguments,
            execution_options=immutabledict({"synchronize_session": False, **execution_options}),
        )
    ).scalar()
    return value


class HasTable(Executable, ClauseElement):
    def __init__(
        self,
        table: Union[str,] = None,
        schema_name: str = None,
    ):
        self._option_table = table if not isinstance(table, str) else None
        self._option_table_name = table if isinstance(table, str) else None
        self._option_schema_name = schema_name


def _table_name(element) -> str:
    return (
        element._option_table.__tablename__
        if element._option_table is not None
        else element._option_table_name
    )


@compiles(HasTable, "postgresql")
def _visit_hastable(element, compiler, **kw):
    # SELECT to_regclass('schema_name.table_name');
    # src: https://stackoverflow.com/a/24089729/219728

    # SELECT (CASE WHEN found IS NULL
    #             THEN False
    #             ELSE True
    #        END) AS found
    # FROM ( SELECT CAST(to_regclass('some_schema_name.some_table_name') AS REGCLASS) ) AS found

    table_name = _table_name(element)
    stmt_0 = select(func.to_regclass(table_name).cast(REGCLASS).label("result")).subquery()
    column_result = column("result")
    stmt_1 = select(
        case((column_result.is_(None), False), else_=True).label("found").cast(Boolean)
    ).select_from(stmt_0)
    return compiler.process(stmt_1, **kw)


@compiles(HasTable, "sqlite")
def _visit_hastable(element, compiler, **kw):
    # https://stackoverflow.com/a/1604121/219728
    table_name = _table_name(element)
    return f"SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table_name}') AS 'result'"


@compiles(HasTable)
def _visit_hastable(element, compiler, **kw):
    raise NotImplementedError()
