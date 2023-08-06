from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import Engine

from constellate.thirdparty.pandas.io.sql.sqlalchemy_execution_option import get_execution_options


async def find_async_engine(engine: Engine = None):
    # FIXME logger not set
    schema_id = (
        get_execution_options(connectable=engine, default_value={})
        .get("schema_translate_map", {})
        .get("per_unit")
    )
    params = {"schema_translate_map": {"per_unit": schema_id}}
    return create_async_engine(engine.url).execution_options(**params)
