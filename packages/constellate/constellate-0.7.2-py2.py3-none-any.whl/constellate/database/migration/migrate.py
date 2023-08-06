import contextlib
import logging
import urllib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from constellate.database.common.databasetype import DatabaseType
from constellate.database.migration.migrationcontext import (
    MigrationContext,
    ConnectionContext,
    ConnectionResolution,
)
from constellate.database.migration.migrationstep import migration_steps
from constellate.database.migration.standard.migrate import migrate as migrate_standard


def edit_connection_url_schema(url: str = None, schema: str = None):
    # FIXME (high) Is this still useful ?
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))

    if schema is not None:
        query.update({"schema": schema})

    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


async def _migrate_standard(
    migration_context: MigrationContext = None,
    user_context: Any = None,
    logger: logging.Logger = None,
) -> None:
    @contextlib.asynccontextmanager
    async def _create_session(migration_context: MigrationContext = None) -> AsyncSession:
        connection_context = migration_context.connection_context
        fn_session_create = None

        # Create the session making function
        for r in connection_context.resolution:
            if (
                r == ConnectionResolution.SESSION_CREATE
                and connection_context.session_create is not None
            ):
                fn_session_create = connection_context.session_create
                break
            elif r == ConnectionResolution.SESSION and connection_context.session is not None:

                @contextlib.asynccontextmanager
                async def _create_default_session():
                    logger.debug(f"Using session: {session}")
                    yield session

                fn_session_create = _create_default_session
                break
            elif r == ConnectionResolution.ENGINE and connection_context.engine is not None:

                @contextlib.asynccontextmanager
                async def _create_default_session():
                    session_maker = sessionmaker(
                        engine=connection_context.engine, class_=AsyncSession
                    )
                    async with session_maker() as session:
                        logger.debug(
                            f"Using session: {session} from engine {connection_context.engine}"
                        )
                        yield session

                fn_session_create = _create_default_session
                break
            elif (
                r == ConnectionResolution.CONNECTION_URL
                and connection_context.connection_url is not None
            ):

                @contextlib.asynccontextmanager
                async def _create_default_session():
                    engine = create_async_engine(connection_context.connection_url)

                    session_maker = sessionmaker(
                        engine=connection_context.engine, class_=AsyncSession
                    )
                    try:
                        async with session_maker() as session:
                            logger.debug(
                                f"Using session: {session} from engine {connection_context.engine} with url {connection_context.connection_url}"
                            )
                            yield session
                    except BaseException as e:
                        raise e
                    finally:
                        await engine.dispose()

                fn_session_create = _create_default_session
                break
            else:
                NotImplementedError(f"Create session from {r}")

        async with fn_session_create() as session:
            yield session

    await migrate_standard(
        migration_context=migration_context,
        user_context=user_context,
        fn_create_session=_create_session,
        logger=logger,
    )


def _migrate_unsupported(**kwargs):
    raise NotImplementedError()


async def migrate(
    migration_context: MigrationContext = None,
    connection_context: ConnectionContext = None,
    user_context: Any = None,
    logger: logging.Logger = None,
) -> None:
    """Run database migrations.

    m = MigrationContext(directory=d)
    where directory = 1 level tree of directories, where each directory contains .py or .sql migration scripts.
    Example: Each directory must contain 1+ sql/py file scripts.
             SQL file scripts must be named with script alphabetic order (executed in the alphabetic order across all directories):
               - 0001.up.foobar.sql
               - 0001.down.foobar.sql
               - 0002.up.zoobar.py
               - 0002.down.zoobar.py
               - etc ...

    Each 1 level directory can have metadata in __init__.py:
        from constellate.database.migration.constant import MigrationKind
        migration_dir = Path(os.path.dirname(__file__))
        kind = MigrationKind.SCHEMA
        schema = 'schema_1'

    Each SQL file can have metadata:
        -- kind = ????
        -- schema = 'schema_1'

    Each Python file can have metadata and functions:
        from constellate.database.migration.constant import MigrationKind
        migration_dir = Path(os.path.dirname(__file__))
        kind = MigrationKind.SCHEMA
        schema = 'schema_1'

        async def upgrade(**kwargs):
            pass

        async def downgrade(**kwargs):
            pass

    @param migration_context: Migration context
    @param connection_context: Connection context
    @param user_context: User specific context
    :raises:
        BaseException When migration fails
    """
    _migrate = {
        DatabaseType.SQLITE: _migrate_standard,
        DatabaseType.POSTGRESQL: _migrate_standard,
    }.get(migration_context.database_type, _migrate_unsupported)

    migration_context.connection_context = (
        migration_context.connection_context or connection_context
    )

    if len(migration_context.steps) == 0:
        # Auto populate some migration context steps properties
        # - migration steps
        kwargs = {}
        if migration_context.migration_context_step_name:
            kwargs.update(
                {"migration_context_step_file_name": migration_context.migration_context_step_name}
            )
        migration_steps(migration_context=migration_context, **kwargs)

    await _migrate(
        migration_context=migration_context,
        user_context=user_context,
        logger=logger,
    )
