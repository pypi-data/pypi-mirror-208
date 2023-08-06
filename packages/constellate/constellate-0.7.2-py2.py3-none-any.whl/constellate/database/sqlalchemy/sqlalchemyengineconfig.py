import attr as attr
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


@attr.s(kw_only=True, auto_attribs=True)
class _EngineConfig:
    #
    # Database connection URIs
    #

    # scheme contain the database type name and optionally a driver name. Eg: postgresql+psyops2
    connection_uri: str = None
    # scheme only contain the database type name
    connection_uri_plain: str = None
    # scheme only contain the database type name + schema name
    connection_uri_plain_schema: str = None

    #
    # Default database connection URIs
    #

    # scheme contain the database type name and optionally a driver name. Eg: postgresql+psyops2
    # the database is a database known to always exists. Eg: 'postgres' for a PG server
    connection_default_uri: str = None

    # (Async) Engine is public engine for apps
    engine: AsyncEngine = None
    # Sync Engine is a private engine for vertical/horizontal sharding needs mostly
    sync_engine: Engine = None
