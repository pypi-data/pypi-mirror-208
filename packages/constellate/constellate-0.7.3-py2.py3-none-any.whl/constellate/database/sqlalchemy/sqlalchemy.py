import asyncio
import itertools
import logging
import time
import warnings
from contextlib import asynccontextmanager
from typing import (
    Dict,
    Tuple,
    List,
    Iterator,
    AsyncGenerator,
    Optional,
    Any,
    Union,
    Callable,
    MutableMapping,
)

from deprecated.classic import deprecated
from sqlalchemy import event, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncSessionTransaction
from sqlalchemy.ext.horizontal_shard import ShardedSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy import Select
from sqlalchemy.orm.session import ORMExecuteState, Session

from constellate.database.sqlalchemy.exception.migrationexception import MigrationException
from constellate.database.sqlalchemy.exception.vacumexception import VacumException
from constellate.database.sqlalchemy.execution.execute import execute_scalar
from constellate.database.sqlalchemy.relationshiptype import RelationshipType

from constellate.database.sqlalchemy.session.multienginesession import MultiEngineSession
from constellate.database.sqlalchemy.session.syncmultienginesession import SyncMultiEngineSession
from constellate.database.sqlalchemy.session.syncmultiengineshardsession import (
    SyncMultiEngineShardSession,
)
from constellate.database.sqlalchemy.sharding.sharder import Sharder
from constellate.database.sqlalchemy.sharding.simplesession import (
    SimpleShardSession,
    SyncSimpleShardSession,
    SyncSimpleSession,
)
from constellate.database.sqlalchemy.sharding.shardoption import SetShardEngineOption
from constellate.database.sqlalchemy.sqlalchemydbconfig import DBConfigType, SQLAlchemyDBConfig
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager
from constellate.database.sqlalchemy.sqlalchemyengineconfig import _EngineConfig
from constellate.datatype.dictionary.update import dict_update, DictCondition


class _SQLAlchemyDBConfigLogger(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger = None, extra: Dict = None):
        super().__init__(logger, extra or {})

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        identifier = self.extra.get("identifier")
        return f"({identifier}) {msg}", kwargs


def FILTER_LOGICAL_SHARD_BY_NOTHING(storage: Any, config: SQLAlchemyDBConfig) -> bool:
    return True


def _warn_no_per_engine_option_found(options: Dict) -> None:
    engines = options.get("engines", None)
    if engines is None:
        warnings.warn(
            "options must be configured per engine. {engines:[{your options here}]}",
            DeprecationWarning,
        )


def _extract_engine_ids(options: Dict):
    engines = options.get("engines", [])
    engines_ids = [e.get("id", None) for e in engines]
    if None in engines_ids:
        raise ValueError("1+ engine is missing field: id")
    return engines_ids


def _get_engine_options(
    options: Dict = None, ignore_no_per_engine_option: bool = False
) -> List[Dict]:
    if not ignore_no_per_engine_option:
        _warn_no_per_engine_option_found(options)

    engines = options.get("engines", [])
    if len(engines) == 0:
        engines = [{"id": "default", **options}]
    return engines


class SQLAlchemy:
    """Use SQLAlchemy to interact with db
    Usage 1: With context manager
        s = SQLAlchemy()
        async with s.setup(...) as db:
            async with db.session_scope(...) as session:
                result = await session.execute(select(...)...)

    Usage 2: Without context manager
       s = SQLAlchemy()
       setup_options = await s.setup2(...)
       session = await s.session_scope2(...)
       result = await session.execute(select(...)...)
       await s.dispose2(setup_options)


    """

    def __init__(self):
        self._config_manager = SQLAlchemyDbConfigManager()

    @property
    def config_manager(self):
        return self._config_manager

    def _engines(
        self, engine_options: List[Dict], types: List[DBConfigType] = [DBConfigType.INSTANCE]
    ) -> Iterator[Tuple[SQLAlchemyDBConfig, Dict]]:
        engine_id_to_options = {
            engine_options.get("id"): engine_options for engine_options in engine_options
        }
        instance_id_to_instances = {k: v for k, v in self._config_manager if v.type in types}

        mapping = []
        for identifier, instance in instance_id_to_instances.items():
            e_options = engine_id_to_options.get(identifier, None)
            if e_options is not None:
                mapping.append((instance, e_options))

        return iter(mapping)

    @asynccontextmanager
    async def setup(self, options: Dict = {}):
        """
        :options: See each _setup_engine_XXXX method for available options in addition to the options below
        - key: engines: Per engine options
        -- Key: type: "instance" (default) => SQLAlchemy will connect to it. "template" SQLAlchemy will use the config for later
        -- Key: id:str. Any string value except "default"
        -- Key: logger:logging.Logger. Default: None
        -- Key: Dict. engine_execution_options: Default: None.

        Eg:
        options = {
            "engines": [
                {
                    "type": "instance",
                    "id": "shard_main",
                    "logger": ...
                    "engine_execution_options: : {...}
                    "migration_priority": 0
                },
                {
                    "type": "template",
                    "id": "shard_slave",
                    "logger": ...,
                    "migration_priority": 1
                }
            ]
        }
        """
        setup_engines_options = []
        try:
            setup_engines_options = await self.setup2(options=options)
            yield self
        finally:
            await self.__dispose_wrapper(
                setup_engines_options=setup_engines_options, ignore_no_per_engine_option=True
            )

    async def setup2(self, options: Dict = {}):
        setup_engines_options = []
        for engine_options in _get_engine_options(options=options):
            db_config_type = (
                DBConfigType.INSTANCE
                if engine_options.get("type", "instance") == "instance"
                else DBConfigType.TEMPLATE
            )

            instance = SQLAlchemyDBConfig()
            instance.identifier = engine_options.get("id", None)
            instance.type = db_config_type
            instance.options = engine_options
            instance.logger = _SQLAlchemyDBConfigLogger(
                engine_options.get("logger", logging.getLogger("constellate.sqlalchemy")),
                {"identifier": instance.identifier},
            )
            instance.logger.debug(f"setup database context: started")
            if instance.type == DBConfigType.INSTANCE:
                await self._setup(instance=instance, options=engine_options)
            instance.logger.debug(f"setup database context: completed")
            self._config_manager.update(instance=instance)
            setup_engines_options.append(engine_options)

        return setup_engines_options

    async def _setup(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        instance.engine_config = await self._create_engine(instance=instance, options=options)

        await self._setup_engine_logging(
            instance=instance, engine=instance.engine_config.engine, options=options
        )
        await self._setup_engine_before_cursor_execute(
            instance=instance, engine=instance.engine_config.engine, options=options
        )
        await self._setup_engine_after_cursor_execute(
            instance=instance, engine=instance.engine_config.engine, options=options
        )
        await self._setup_engine_connection_connect(
            instance=instance, engine=instance.engine_config.engine, options=options
        )
        await self._setup_engine_connection_begin(
            instance=instance, engine=instance.engine_config.engine, options=options
        )
        await self._setup_engine_session_maker(instance=instance)

    async def _create_engine(
        self, instance: SQLAlchemyDBConfig, options: Dict = {}
    ) -> _EngineConfig:
        raise NotImplementedError("Subclass must implemented")

    def _get_database_driver_name(self) -> Optional[str]:
        """


        :returns: If no driver, then None. Otherwise driver name

        """
        return None

    async def _setup_engine_logging(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        # Note: Log levels inspired from:
        # https://docs.sqlalchemy.org/en/14/core/engines.html#configuring-logging
        debug = options.get("debug", None)
        if debug is not None:
            severity1 = logging.INFO if debug.get("developer", False) else logging.WARN
            severity2 = logging.DEBUG if debug.get("developer", False) else logging.INFO
            # Turn on SQL Query logging
            logging.getLogger("sqlalchemy").setLevel(severity1)
            # INFO=Log SQL query. DEBUG=Log SQL query + result
            logging.getLogger("sqlalchemy.engine").setLevel(severity1)
            logging.getLogger("sqlalchemy.dialects").setLevel(severity1)
            # Turn on Connection Pool usage logging
            # INFO=Log connection invalidation + recycle events. DEBUG=Log all pool
            # checkings/checkouts
            logging.getLogger("sqlalchemy.pool").setLevel(severity2)
            # Turn on other things
            logging.getLogger("sqlalchemy.orm").setLevel(severity2)
            instance.logger.setLevel(logging.DEBUG)
        else:
            instance.logger.setLevel(logging.WARN)

    async def _setup_engine_before_cursor_execute(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        # Profile SQL query execution time
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def profile_query_exec_time_begin(
            conn, cursor, statement, parameters, context, executemany
        ):
            context._query_start_time = time.time()
            instance.logger.debug("Start Query:\n%s" % statement)
            # Modification for StackOverflow answer:
            # Show parameters, which might be too verbose, depending on usage..
            instance.logger.debug("Parameters:\n%r" % (parameters,))

    async def _setup_engine_after_cursor_execute(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def profile_query_exec_time_end(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - context._query_start_time
            # Modification for StackOverflow: times in milliseconds
            instance.logger.debug(f"Query Complete! Total Time: %.02fms" % (total * 1000))

    async def _setup_session_do_orm_execute(self, session=AsyncSession, options: Dict = None):
        logger = (options or {}).get("logger", logging.getLogger("constellate.dummy.logger"))

        def _switch_shard_engine(context: ORMExecuteState = None, shard_id: str = None):
            logger.debug(f"Using engine with shard_id={shard_id}")
            context.update_execution_options(_sa_shard_id=shard_id)

        @event.listens_for(session.sync_session, "do_orm_execute")
        def switch_shard_engine(context: ORMExecuteState):
            if isinstance(context.session, ShardedSession):
                #
                # ShardedSession official usages
                #

                # Usage: session.execute(select(...), bind_arguments={"shard_id": "engine_shard_id_3"})
                # - src: https://github.com/sqlalchemy/sqlalchemy/blob/979ea6b21f71605314dc0ac1231dd385eced98c4/lib/sqlalchemy/ext/horizontal_shard.py#L241
                # Usage: session.execute(select(...), execution_options={"_sa_shard_id": "engine_shard_id_3"})
                # - src: https://github.com/sqlalchemy/sqlalchemy/blob/979ea6b21f71605314dc0ac1231dd385eced98c4/lib/sqlalchemy/ext/horizontal_shard.py#L241

                #
                # ShardedSession unofficial usages
                #

                # Usage: Instruct session to use a particular engine whose shard_id is 'engine_shard_id_3' to execute THIS select(...)
                # Sample: session.execute(select(...).options(SetShardEngineOption("engine_shard_id_3"))
                # Conditions:
                # - Only supported for query with .options() available, I think
                # - Only supported for ShardedSession instances since they trigger do_orm_execute events
                # src: #
                # https://github.com/sqlalchemy/sqlalchemy/discussions/6885#discussioncomment-1186864
                # NOTE:
                # - Will be deprecated in favor of THIS ? THIS https://github.com/sqlalchemy/sqlalchemy/issues/7226#issuecomment-950440743
                for elem in context.user_defined_options:
                    found_shard_engine_option = isinstance(elem, SetShardEngineOption)
                    if found_shard_engine_option:
                        _switch_shard_engine(context=context, shard_id=elem.payload)
                        return

                # Usage: Instruct session to use a particular engine whose shard_id is 'engine_shard_id_3' for all statement by default,
                #        unless overwritten on an individual statement basis
                # Sample: async with self.session_scope(execution_options={'shard_id':SetShardEngineOption('engine_shard_id_3')}) as session:
                #           ...
                elem = context.execution_options.get("shard_id", None)
                found_shard_engine_option = isinstance(elem, SetShardEngineOption)
                if found_shard_engine_option:
                    _switch_shard_engine(context=context, shard_id=elem.payload)
                    return

    async def _setup_engine_connection_connect(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        pass

    async def _setup_engine_connection_begin(
        self, instance: SQLAlchemyDBConfig, engine: AsyncEngine = None, options: Dict = None
    ):
        pass

    async def _setup_engine_session_maker(self, instance: SQLAlchemyDBConfig = None, **kwargs):
        if instance is not None:
            kwargs.update({"bind": instance.engine_config.engine})

        instance.session_maker = await self._create_session_maker(**kwargs)

    async def migrate(self, options: Dict = {}):
        """
        :options per engine:
        - key: migration_context:MigrationContext, A migration context
        - key: migration_priority: int [0, max_size]. Default: 0. Migration priority amongst all engines.
               Engines with identical priority will be migrated concurrently. Otherwise serialized by ascending priority number
        """

        def _get_priority(options: Dict):
            return options.get("migration_priority", 0)

        pios = [
            (_get_priority(i_options), instance, i_options)
            for instance, i_options in self._engines(_get_engine_options(options=options))
        ]

        migration_orders = {}
        for p, i, o in pios:
            sub_migrations = migration_orders.get(p, [])
            sub_migrations.append((i, o))
            migration_orders[p] = sub_migrations

        async def __migrate(
            instance: SQLAlchemyDBConfig = None, options: Dict = None, concurrent: bool = None
        ):
            log_prefix = f"Migrating {'concurrently' if concurrent else ''}: {instance.identifier}"
            try:
                try:
                    instance.logger.info(f"{log_prefix}: started")
                    await self._migrate(instance=instance, options=options)
                    instance.logger.info(f"{log_prefix}: completed")
                except BaseException as e:
                    raise MigrationException() from e
            except BaseException as e:
                instance.logger.error(f"{log_prefix}: failed", exc_info=1)
                raise e

        for priority, migrations in migration_orders.items():
            concurrent = len(migrations) > 0
            await asyncio.gather(
                *[__migrate(instance=i, options=o, concurrent=concurrent) for i, o in migrations]
            )

    async def _migrate(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        raise NotImplementedError("Must be implemented by the sub class")

    async def database_compatible(self, options: Dict = {}) -> bool:
        """
        True when database is greater than the min database user version
        Option per engine:
        - database_user_version_compatible_query: SQLAlchemy SELECT query. To query the current database version from (incompatible with database_user_version_class_column).
                                                                           The queur must return a scalar boolean value: True == compatible
        - engine_execution_options: Dict. Execution options to pass on
        - database_compatibility_check: Callable[[AsyncSession, Select], AsyncGenerator[bool,None]]. Custom function to check if the database is compatible
        """

        async def has_compatibility(
            instance=None,
            version_check_query=None,
            execution_options={},
            compatibility_check: Callable[
                [AsyncSession, Any, Select], AsyncGenerator[bool, None]
            ] = None,
        ):
            async with self.session_scope(config=instance) as session:
                if compatibility_check is None:

                    async def user_version_compatible(
                        session: AsyncSession = None, version_check_query: Select = None
                    ) -> bool:
                        @execute_scalar
                        async def _read_database_compatibility(**kwargs):
                            return version_check_query

                        compatible = await _read_database_compatibility(session=session)
                        return compatible or False

                    compatibility_check = user_version_compatible

                return await compatibility_check(
                    session=session, version_check_query=version_check_query
                )

        compatibles = [
            has_compatibility(
                instance=instance,
                version_check_query=i_options.get("database_user_version_compatible_query"),
                execution_options=i_options.get("engine_execution_options", {}),
                compatibility_check=i_options.get("database_compatibility_check", None),
            )
            for instance, i_options in self._engines(_get_engine_options(options=options))
        ]
        compatibles = await asyncio.gather(*compatibles)
        return len(compatibles) > 0 and all(compatibles)

    async def vacuum(self, options: Dict = {}):
        """
        :raises:
            VacumException when vacum fails
        """
        for instance, i_options in self._engines(_get_engine_options(options=options)):
            try:
                instance.logger.info(f"Vacumming db: started")
                await self._vacuum(instance=instance, options=i_options)
                instance.logger.info(f"Vacumming db: completed")
            except BaseException as e:
                instance.logger.error(f"Vacumming db: failed", exc_info=1)
                raise VacumException() from e

    async def _vacuum(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        raise NotImplementedError("Must be implemented by the sub class")

    async def backup(self, options: Dict = {}):
        """
        :options:
        Key: db_file:str Source db absolute file path
        Key: db_file_backup:str Destination db absolute file path
        """
        for instance, i_options in self._engines(_get_engine_options(options=options)):
            try:
                instance.logger.info(f"Backup db: started")
                await self._backup(instance=instance, options=i_options)
                instance.logger.info(f"Backup db: completed")
            except BaseException:
                instance.logger.error(f"Backup db: failed", exc_info=1)
                raise

    async def _backup(self, instance: SQLAlchemyDBConfig = None, options: Dict = {}):
        raise NotImplementedError("Must be implemented by sub class")

    async def dispose(self, options: Dict = {}):
        await self.__dispose_wrapper(options=options)

    async def dispose2(self, setup_engines_options: List = []):
        await self.__dispose_wrapper(setup_engines_options=setup_engines_options)

    async def __dispose_wrapper(
        self,
        options: Dict = None,
        setup_engines_options: List = None,
        ignore_no_per_engine_option: bool = False,
    ):
        values = []
        if options is not None:
            values = self._engines(
                _get_engine_options(
                    options=options, ignore_no_per_engine_option=ignore_no_per_engine_option
                )
            )
        elif setup_engines_options is not None:
            values = itertools.chain(
                *[
                    self._engines(
                        _get_engine_options(
                            options=setup_engine_options,
                            ignore_no_per_engine_option=ignore_no_per_engine_option,
                        )
                    )
                    for setup_engine_options in setup_engines_options
                ]
            )
        else:
            raise ValueError()

        for instance, i_options in values:
            if instance.engine_config.engine is not None:
                await self._dispose(engine=instance.engine_config.engine)
            # FIXME (medium) pop will try to pop an identifier that was already poped
            self._config_manager.pop(instance.identifier)

    async def _dispose(self, engine: AsyncEngine = None):
        if engine is not None:
            await engine.dispose()

    async def _create_session_maker(self, **kwargs):
        dict_update(map=kwargs, when=DictCondition.MISSING, key="autoflush", value=True)
        dict_update(map=kwargs, when=DictCondition.MISSING, key="future", value=True)
        dict_update(map=kwargs, when=DictCondition.MISSING, key="expire_on_commit", value=True)
        dict_update(map=kwargs, when=DictCondition.MISSING, key="twophase", value=False)
        dict_update(map=kwargs, when=DictCondition.MISSING, key="execution_options", value={})
        # dict_update_when_missing(map=kwargs, when=DictCondition.MISSING, key='bind', value=...)
        dict_update(
            map=kwargs, when=DictCondition.MISSING, key="class_", value=self._get_session_class()
        )
        dict_update(
            map=kwargs,
            when=DictCondition.MISSING,
            key="sync_session_class",
            value=self._get_sync_session_class(),
        )

        return sessionmaker(**kwargs)

    def _get_session_class(self) -> AsyncSession:
        return MultiEngineSession

    def _get_sync_session_class(self) -> Session:
        return SyncMultiEngineSession

    @asynccontextmanager
    async def session_scope(self, **kwargs) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope around a series of database operations."""
        kwargs, custom_kwargs = self.__pop_custom_kwargs(kwargs=kwargs)
        session_maker = await self._create_session_maker(**kwargs)

        async for session in self.__session_scope(
            session_maker=session_maker,
            owner=self,
            config_manager=self._config_manager,
            **custom_kwargs,
        ):
            yield session
            await asyncio.sleep(0)

    async def session_scope2(self, **kwargs) -> AsyncSession:
        """Provide a transactional scope around a series of database operations."""
        kwargs, custom_kwargs = self.__pop_custom_kwargs(kwargs=kwargs)
        session_maker = await self._create_session_maker(**kwargs)

        async for session in self.__session_scope(
            session_maker=session_maker,
            owner=self,
            config_manager=self._config_manager,
            **custom_kwargs,
        ):
            # Note: This is not a generator function, by design
            return session

    @asynccontextmanager
    async def __session_scope_for_shard(
        self,
        shard_session_class: Any = None,
        shard_sync_session_class: Any = None,
        unshard_session_class: Any = None,
        unshard_sync_session_class: Any = None,
        autoflush=True,
        expire_on_commit=True,
        config: SQLAlchemyDBConfig = None,
        execution_options: Dict = None,
        bind_arguments: Dict = None,
        twophase: bool = False,
        sharded: bool = True,
        begin_explicit: bool = True,
        horizontal_shard_chooser: Callable = None,
        horizontal_id_chooser: Callable = None,
        horizontal_execute_chooser: Callable = None,
        logging_token: str = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Template function to provide sharded or unsharded session
        User should typically override `session_scope_for_shard`
        """
        if sharded:
            execution_options = execution_options or {}
            bind_arguments = bind_arguments or {}

            # Prepare sharded session DEFAULT settings
            # by selecting a database (and therefore an engine)
            # - with database level shards
            full_level_shards = {
                config.identifier: config.engine_config.engine.sync_engine
                for config in await self.for_each_engine(filter_fn=FILTER_LOGICAL_SHARD_BY_NOTHING)
            }
            bind_arguments.update({"shard_id": config.identifier})
            # by selecting a schema within the selected database
            # - with schema level shards
            #
            # This works for SQLAlchemy constructs supporting it such as:
            # - select()/delete()/etc from actual table object
            #
            shard_schema_id = config.options.get("custom").schema_id
            execution_options.update({"schema_translate_map": {"per_unit": shard_schema_id}})
            if logging_token is not None:
                # Doc: https://docs.sqlalchemy.org/en/14/core/engines.html#setting-per-connection-sub-engine-tokens
                execution_options.update({"logging_token": logging_token})

            # - with sharding choosers
            # Instantiate a sharded session
            async with self.session_scope(
                class_=shard_session_class,
                autoflush=autoflush,
                expire_on_commit=expire_on_commit,
                execution_options=execution_options,
                bind_arguments=bind_arguments,
                twophase=twophase,
                sync_session_class=shard_sync_session_class,
                shards=full_level_shards,
                id_chooser=horizontal_id_chooser,
                shard_chooser=horizontal_shard_chooser,
                execute_chooser=horizontal_execute_chooser,
                begin_explicit=begin_explicit,
            ) as session:
                yield session
        else:
            # Instantiate a un-sharded session
            async with self.session_scope(
                class_=unshard_session_class,
                autoflush=autoflush,
                expire_on_commit=expire_on_commit,
                execution_options=execution_options,
                bind_arguments=bind_arguments,
                twophase=twophase,
                sync_session_class=unshard_sync_session_class,
                bind=config.engine_config.engine,
                begin_explicit=begin_explicit,
            ) as session:
                yield session

    @asynccontextmanager
    async def session_scope_for_shard(
        self,
        shard_session_class: MultiEngineSession = SimpleShardSession,
        shard_sync_session_class: SyncMultiEngineShardSession = SyncSimpleShardSession,
        unshard_session_class: MultiEngineSession = SimpleShardSession,  # FIXME (high) Why is there the word SHARD in it ?
        unshard_sync_session_class: SyncMultiEngineSession = SyncSimpleSession,
        sharder: Sharder = None,
        **kwargs,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Create session using shards"""
        sharder = sharder or Sharder(config_manager=self.config_manager)
        async with self.__session_scope_for_shard(
            shard_session_class=shard_session_class,
            shard_sync_session_class=shard_sync_session_class,
            unshard_session_class=unshard_session_class,  # FIXME (high) Why is there the word SHARD in it ?
            unshard_sync_session_class=unshard_sync_session_class,
            horizontal_shard_chooser=sharder.shard_chooser,
            horizontal_id_chooser=sharder.id_chooser,
            horizontal_execute_chooser=sharder.execute_chooser,
            **kwargs,
        ) as session:
            yield session

    def __pop_custom_kwargs(self, kwargs: Dict = {}):
        custom_kwargs = {}

        begin_explicit = kwargs.pop("begin_explicit", None)
        if begin_explicit is not None:
            custom_kwargs["begin_explicit"] = begin_explicit

        return kwargs, custom_kwargs

    async def __session_scope(
        self,
        session_maker: sessionmaker = None,
        config: Any = None,
        begin_explicit: bool = False,
        invalidate_session_on_exception: bool = False,
        **kwargs,
    ) -> AsyncGenerator[Union[AsyncSession, AsyncSessionTransaction], None]:
        """Provide a transactional scope around a series of operations."""
        # If config manager hold max 1 engine instance, then the session default bind is to that engine.
        # Otherwise, the session bind is project implementation specific
        # (horizontal / vertical sharding)
        configs = [config] if config is not None else [s for s in kwargs.get("config_manager", [])]
        configs = (
            list(filter(lambda t: t[1].type == DBConfigType.INSTANCE, configs))
            if len(configs) < 2
            else configs
        )

        if len(configs) == 1:
            # Case SQLALchemy's AsyncSession is provided. SQLAlchemyDBConfig is not a supported option.
            # Fall back to binding the session to the sole engine available
            # NOTE: This applies to SQLALchemy's AsyncSession (not constelatte's AsyncSession subclasses like MultiEngineSession)
            # FIXME (low) config tuple is ugly. Use a proper attr enabled class
            default_config = configs[0]
            session_maker.configure(bind=default_config[1].engine_config.engine)
        else:
            # Case Constellate's AsyncSession subclasses are provided. SQLAlchemyDBConfig is a supported option.
            pass

        session = session_maker(**kwargs)
        invalidate_session = False
        try:
            await self._setup_session_do_orm_execute(session=session)

            if begin_explicit:
                session.begin()
            yield session
            await session.commit()
        except BaseException as e:
            invalidate_session = True
            await session.rollback()
            raise
        finally:
            if invalidate_session and invalidate_session_on_exception:
                await session.invalidate()
            else:
                await session.close()
