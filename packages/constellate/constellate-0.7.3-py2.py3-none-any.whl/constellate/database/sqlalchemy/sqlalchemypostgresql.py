import asyncio
import functools
from typing import Dict, Optional, Tuple

from sqlalchemy import create_engine, inspect
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import database_exists

from constellate.database.common.databasetype import DatabaseType
from constellate.database.migration.migrate import migrate
from constellate.database.migration.constant import MigrationAction
from constellate.database.migration.migrationcontext import MigrationContext, ConnectionContext
from constellate.database.sqlalchemy.execution.execute import execute_discard_result
from constellate.database.sqlalchemy.expression.schema.create import CreateSchema
from constellate.database.sqlalchemy.sqlalchemy import SQLAlchemy
from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig
from constellate.database.sqlalchemy.sqlalchemyengineconfig import _EngineConfig

_POOL_CONNECTION_PERMANENT_SIZE = 10
_POOL_CONNECTION_OVERFLOW_SIZE = 5


class SQLAlchemyPostgresql(SQLAlchemy):
    def __init__(self):
        super().__init__()
        self._migrate_db_creation_lock = asyncio.Lock()
        self._migrate_db_schema_creation_lock = asyncio.Lock()

    def _get_database_driver_name(self) -> Optional[str]:
        return "asyncpg"

    async def _create_engine(
        self, instance: SQLAlchemyDBConfig, options: Dict = {}
    ) -> _EngineConfig:
        """
        :options:
        - server_host:str               . DB host
        - server_port:str               . DB port
        - database_username:str         . DB user name
        - database_password:str         . DB user password
        - database_name:str             . DB name
        - database_name_fallback:str    . DB name to connect to if the database "database_name" does not exist (yet)
        - database_schema_name:str      . DB schema name
        - pool_connection_size:int            . Max permanent connection held in the pool. Default: 10
        - pool_connection_overflow_size:int            . Max connection returned in addition to the ones in the pool. Default: 5
        - pool_connection_timeout:float . Max timeout to return a connection, in seconds. Default: 30.0 (sec)
        - pool_pre_ping: bool. Default: False
        - application_name: str. Default: None. Set the postgres application name (visible in logs via app=%a). src: https://stackoverflow.com/a/15691283/219728
        - custom: Dict[any,any]. Dictionary of custom attribute, never used by constellate
        - asynchronous:bool . Use asyncio enabled sqlalchemy engine. Default: False
        """
        # Create engine
        # - https://docs.sqlalchemy.org/en/14/dialects/postgresql.html
        username_port = ":".join(
            filter(
                None,
                [options.get("database_username", None), options.get("database_password", None)],
            )
        )
        host_port = ":".join(
            filter(None, [options.get("server_host", None), options.get("server_port", None)])
        )
        credential_host = f"{username_port}@{host_port}"

        db_name = options.get("database_name", None)
        db_name_default = options.get("database_name_fallback", "postgres")
        db_schema = options.get("database_schema_name", "public")
        execution_options = options.get("engine_execution_options", None)
        application_name = options.get("application_name", "constellate")

        scheme_driver = f"postgresql+{self._get_database_driver_name()}"
        connection_uri = f"{scheme_driver}://{credential_host}/{db_name}"
        connection_uri_plain = f"postgresql://{credential_host}/{db_name}"
        connection_uri_plain_schema = f"postgresql://{credential_host}/{db_name}?schema={db_schema}"
        connection_default_uri_plain = f"{scheme_driver}://{credential_host}/{db_name_default}"

        pool_class = options.get("pool_class", QueuePool)
        pool_size = options.get("pool_connection_size", 10)
        pool_overflow_size = options.get("pool_connection_overflow_size", 5)
        pool_timeout = options.get("pool_connection_timeout", 30.0)
        pool_pre_ping = options.get("pool_pre_ping", False)

        kwargs = {
            "future": True,
            "echo": False,
            "echo_pool": False,
            "poolclass": pool_class,
        }

        if pool_class == QueuePool:
            kwargs.update(
                {
                    "pool_size": pool_size,
                    "max_overflow": pool_overflow_size,
                    "pool_timeout": pool_timeout,
                    "pool_pre_ping": pool_pre_ping,
                }
            )
        elif pool_class == NullPool:
            kwargs.update(
                {
                    "pool_pre_ping": pool_pre_ping,
                }
            )
        else:
            raise NotImplementedError("Unsupported pool class so far")

        kwargs_async_engine = {}
        kwargs_sync_engine = {}
        if execution_options is not None:
            kwargs.update({"execution_options": execution_options})
        if application_name is not None:
            # asyncpg driver: 'server_settings' is a special argument to pass PG's client runtime parameters
            # src: https://magicstack.github.io/asyncpg/current/api/index.html#connection
            kwargs_async_engine.update(
                connect_args={"server_settings": {"application_name": application_name}}
            )
            # psycopg2 driver: no special argument for the driver to pass PG's client runtime parameters
            # src: https://www.psycopg.org/docs/module.html#psycopg2.connect
            kwargs_sync_engine.update(connect_args={"application_name": application_name})

        engine = create_async_engine(
            connection_uri,
            **kwargs,
            **kwargs_async_engine,
        )

        sync_engine = create_engine(connection_uri_plain, **kwargs, **kwargs_sync_engine)
        return _EngineConfig(
            connection_uri=connection_uri,
            connection_uri_plain=connection_uri_plain,
            connection_uri_plain_schema=connection_uri_plain_schema,
            connection_default_uri=connection_default_uri_plain,
            engine=engine,
            sync_engine=sync_engine,
        )

    async def _create_database(
        self, connection_uri: str = None, db_name: str = None, encoding="UTF8"
    ):
        @execute_discard_result
        async def __create_database(**kargs):
            return text(f"CREATE DATABASE {db_name} ENCODING {encoding};")

        async with create_async_engine(
            connection_uri, isolation_level="AUTOCOMMIT"
        ).connect() as connection:
            await __create_database(session=connection)

    async def __database_schema_create(self, connection_uri: str = None, name: str = None):
        @execute_discard_result
        async def __create_database_schema(**kargs):
            return CreateSchema(name, if_not_exists=True)

        async with create_async_engine(connection_uri).connect() as connection:
            try:
                await __create_database_schema(session=connection)
                await connection.commit()
            except BaseException:
                await connection.rollback()
                raise

    async def _setup_engine_before_cursor_execute(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        await super()._setup_engine_before_cursor_execute(
            instance=instance, engine=engine, options=options
        )

        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def switch_shard_schema_postgres(conn, cursor, statement, parameters, context, executemany):
            if conn.engine.dialect.name == "postgresql":
                CURRENT_SHARD_SHEMA_ID_KEY = "current_shard_schema_id"
                NEW_SHARD_SHEMA_ID_KEY = "shard_schema_id"
                # FIXME Use SetShardSchemaOption instead
                shard_schema_id = conn._execution_options.get(
                    NEW_SHARD_SHEMA_ID_KEY,
                    context.execution_options.get(NEW_SHARD_SHEMA_ID_KEY, None),
                )
                current_shard_schema_id = conn.info.get(CURRENT_SHARD_SHEMA_ID_KEY, None)

                if current_shard_schema_id != shard_schema_id:
                    instance.logger.debug(
                        f"Switching schema from {current_shard_schema_id} to {shard_schema_id}"
                    )
                    paths = ",".join(
                        list(filter(lambda x: x is not None, [shard_schema_id, "public"]))
                    )
                    cursor.execute(f"SET search_path TO {paths}")
                    conn.info[CURRENT_SHARD_SHEMA_ID_KEY] = shard_schema_id

    async def _migrate(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        # Create database + schema
        db_skip_creation = options.get("database_skip_creation", False)
        db_schema_skip_creation = options.get("database_schema_skip_creation", False)
        db_skip_migration = options.get("database_skip_migration", False)

        if not db_skip_creation:
            async with self._migrate_db_creation_lock:
                # Serialize database creation to avoid race condition during concurrent
                # migration on the same database but different schema
                if not database_exists(instance.engine_config.connection_uri_plain):
                    uri = make_url(instance.engine_config.connection_uri_plain)
                    await self._create_database(
                        connection_uri=instance.engine_config.connection_default_uri,
                        db_name=uri.database,
                    )

        if not db_schema_skip_creation:
            uri = make_url(instance.engine_config.connection_uri_plain_schema)
            # FIXME Critical blocker https://github.com/sqlalchemy/sqlalchemy/issues/9682
            #       ONCE FIXED resume https://docs.sqlalchemy.org/en/20/errors.html#error-b8d9 ?
            db_schema = (uri.normalized_query or {}).get("schema", None)
            if isinstance(db_schema, Tuple):
                # Case: ('public,)
                db_schema = db_schema[0]

            if db_schema is not None:
                async with self._migrate_db_schema_creation_lock:
                    await self.__database_schema_create(
                        connection_uri=instance.engine_config.connection_uri, name=db_schema
                    )

        if not db_skip_migration:
            # Migrate database
            inspector = inspect(instance.engine_config.sync_engine)
            await migrate(
                connection_context=ConnectionContext(
                    connection_url=instance.engine_config.connection_uri_plain_schema,
                    engine=instance.engine_config.engine,
                    session_create=functools.partial(self.session_scope, config=instance),
                ),
                migration_context=options.get(
                    "migration_context",
                    MigrationContext(
                        database_type=DatabaseType.POSTGRESQL,
                        action=MigrationAction.UPGRADE,
                        schema=instance.options.get(
                            "database_schema_name", inspector.default_schema_name
                        ),
                    ),
                ),
                user_context=self,
                logger=instance.logger,
            )

    async def _vacuum(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        """
        :options:
        - profiles: A vacumm profile. Values:
        -- analyze: Updates statistics used by the planner (to speed up queries)
        -- default: Sensible defaults
        """
        # Vacuum requires a connection/session without transaction enabled.
        async with instance.engine_config.engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as connection:
            commands = {
                "analyze": ["VACUUM ANALYZE;"],
                "default": ["VACUUM (ANALYZE, VERBOSE);"],
            }
            for profile in options.get("profiles", ["default"]):
                for statement in commands[profile]:
                    try:

                        @execute_discard_result
                        async def __command(**kargs):
                            return text(statement)

                        await __command(session=connection)
                    except BaseException as e:
                        raise Exception(f"Vacuum statement failed: {statement}") from e
