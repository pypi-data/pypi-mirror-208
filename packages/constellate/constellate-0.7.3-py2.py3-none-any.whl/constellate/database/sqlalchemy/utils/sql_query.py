from typing import Dict, Union

from sqlalchemy.engine import Engine
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql import Select, Executable


def stringify(
    query: Union[Select, Executable] = None,
    engine: Engine = None,
    dialect: DefaultDialect = None,
    compile_kwargs: Dict = {},
) -> str:
    """@query: Query object to get plain SQL query from
    @engine: Database type to know the SQL dialect to convert into

    src: https://stackoverflow.com/a/23835766/219728

    :param query: Union[Select:
    :param Executable]:  (Default value = None)
    :param engine: Engine:  (Default value = None)
    :param dialect: DefaultDialect:  (Default value = None)
    :param compile_kwargs: Dict:  (Default value = {})

    """
    return (
        query.compile(engine)
        if engine is not None
        else query.compile(
            dialect=dialect, compile_kwargs={"literal_binds": True, **compile_kwargs}
        )
    )


async def resolve_engine_from_query(
    session: AsyncSession = None, query: Union[Select, Executable] = None
) -> AsyncEngine:
    """
    Resolve the engine used by the query. Useful when the db session uses shards
    """
    # PERF: This will execute the query!!!! As of 2021 May, I did not find a way to get this info without executing the
    # query against the db
    result = await session.execute(query)

    # Fetch 1 or 0 result and **release the underlying cursor**, to prevent
    # virtual transaction to be held open on the database
    ignored = result.scalars().all()

    engine = result.raw.connection.engine
    return engine
