from typing import Union, Callable, Dict, Optional

import pandas as pd
import regex
import sqlalchemy
from pandas._typing import DtypeArg

from constellate.database.sqlalchemy.session.multienginesession import MultiEngineSession
from constellate.database.sqlalchemy.utils.sql_query import resolve_engine_from_query
from pandas import DataFrame
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import Engine, Connection
from sqlalchemy.sql import Select


def _driverless_engine_url(engine: AsyncEngine = None):
    url = str(engine.url)
    # match foo+bar in foo+bar://something
    match_drivername = regex.match("^.+?(?=:\\/)", url)
    span = match_drivername.span()
    db_driver_protocol = url[span[0] : span[1]]
    parts = db_driver_protocol.split("+")

    driver_protocol = parts[1]
    url = url.replace(driver_protocol, "", 1).replace("+", "", 1)
    return url


async def read_sql_query(sql: str = None, engine: AsyncEngine = None) -> DataFrame:
    # As of June 2021: Pandas does not yet support SQLALchemy 2.x engine / AsyncEngine
    # So, transform the async engine url into a driver agnostic url for pandas
    # to connect to it directly
    url = _driverless_engine_url(engine=engine.url)
    df = pd.read_sql_query(sql, url)
    return df


async def read_sql_query2(
    session: Union[MultiEngineSession] = None,
    query: Select = None,
    params: Dict = None,
    find_async_engine: Callable[[Engine], AsyncEngine] = None,
    coerce_float: bool = True,
    dtype: Optional[DtypeArg] = None,
) -> DataFrame:
    async_engine: AsyncEngine = None
    sync_engine_url: str = None

    # Resolve engine
    sync_engine = await resolve_engine_from_query(session=session, query=query.limit(0))

    # Resolve final engine
    if find_async_engine is not None:
        async_engine = await find_async_engine(engine=sync_engine)
    else:
        sync_engine_url = _driverless_engine_url(engine=sync_engine.url)

    params = params or {}
    if async_engine is not None:
        async with async_engine.begin() as connection:

            def execute_query(connection: Connection) -> DataFrame:
                return pd.read_sql_query(
                    query, connection, params=params, dtype=dtype, coerce_float=coerce_float
                )

            return await connection.run_sync(execute_query)
    elif sync_engine_url is not None:
        return pd.read_sql_query(
            query, sync_engine_url, params=params, dtype=dtype, coerce_float=coerce_float
        )
    else:
        raise NotImplementedError()
