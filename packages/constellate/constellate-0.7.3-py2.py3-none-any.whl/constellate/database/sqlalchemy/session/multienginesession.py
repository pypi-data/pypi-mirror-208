from typing import Dict, Tuple

from sqlalchemy.exc import UnboundExecutionError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util._collections import EMPTY_DICT

from constellate.database.sqlalchemy.session.binder.binderresolver import BinderResolver
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager
from constellate.datatype.dictionary.pop import pop_param_when_available


class _ConfigManager:
    @property
    def config_manager(self):
        return self._config_manager


class _InjectDefaultExecutionOptions:
    def __inject_options(self, options: Dict = None, default_options: Dict = None):
        default_options = default_options or {}
        # Note: options is most of the time an immutabledict instance.
        options = dict(options)

        no_value = object()
        for key, value in default_options.items():
            current_value = options.get(key, no_value)
            if current_value == no_value:
                # Set default execution option value
                options.update({key: value})
            else:
                # Do not use default execution option value
                pass

        return options

    def _inject_default_bind_arguments(
        self, bind_arguments: Dict = EMPTY_DICT, kw: Dict = EMPTY_DICT
    ) -> Tuple[Dict, Dict]:
        if bind_arguments is not None:
            return (
                self.__inject_options(
                    options=bind_arguments,
                    default_options=self._default_bind_arguments,
                ),
                kw,
            )
        else:
            return bind_arguments, self.__inject_options(
                options=kw.get("bind_arguments", EMPTY_DICT),
                default_options=self._default_bind_arguments,
            )

    def _inject_default_execution_options(
        self, execution_options: Dict = EMPTY_DICT, kw: Dict = EMPTY_DICT
    ) -> Tuple[Dict, Dict]:
        if execution_options is not None:
            return (
                self.__inject_options(
                    options=execution_options,
                    default_options=self._default_execution_options,
                ),
                kw,
            )
        else:
            return execution_options, self.__inject_options(
                options=kw.get("execution_options", EMPTY_DICT),
                default_options=self._default_execution_options,
            )


class MultiEngineSession(AsyncSession, _InjectDefaultExecutionOptions, _ConfigManager):
    """Session holding multiple SQLAlchemy Engine."""

    def __init__(
        self,
        owner=None,
        config_manager: SQLAlchemyDbConfigManager = None,
        binder_resolver: BinderResolver = None,
        **kwargs,
    ):
        """
        @params: owner SQLAlchemy instance, owning the session
        @params: config_manager Proxy to get the list of SQLALchemyDBConfing from the owning SQLAlchemy instance
        @params: binder_resolver binder_resolver dynamically resolve the bind based on XXXX
        @params: config If provided and binder_resolver did not resolve the bind, this session will fallback to this config's engine for bind
        """
        sync_session_class = kwargs.get("sync_session_class", None)
        sync_session_class_customized = sync_session_class is not None

        config = None
        execution_options = None
        bind_arguments = None
        if sync_session_class_customized:
            # Case: Constellate's SyncMultiEngineSession or subclass
            execution_options = kwargs.get("execution_options", {})
            bind_arguments = kwargs.get("bind_arguments", {})
            kwargs.update({"owner": owner, "config_manager": config_manager})
            config = kwargs.get("config", None)
        else:
            # Case: SQLALchemy's Session or subclass
            # Extracting execution_options/bind_arguments from kwargs because super.init is not
            # supporting said param (keep in sync with SyncMultiEngineSession)
            execution_options = pop_param_when_available(
                kwargs=kwargs, key="execution_options", default_value={}
            )
            bind_arguments = pop_param_when_available(
                kwargs=kwargs, key="bind_arguments", default_value={}
            )
            config = pop_param_when_available(kwargs=kwargs, key="config", default_value={})

        super().__init__(**kwargs)
        self._owner = owner
        self._config_manager = config_manager
        self._default_execution_options = execution_options
        self._default_bind_arguments = bind_arguments

        default_binder = super()
        self._bind_resolver = (
            BinderResolver(resolvers=[default_binder], default_config=config)
            if binder_resolver is None
            else binder_resolver
        )

    def get_bind(
        self,
        mapper=None,
        clause=None,
        bind=None,
        _sa_skip_events=None,
        _sa_skip_for_implicit_returning=False,
    ):
        return self._bind_resolver.get_bind(
            mapper=mapper,
            clause=clause,
            bind=bind,
            _sa_skip_events=_sa_skip_events,
            _sa_skip_for_implicit_returning=_sa_skip_for_implicit_returning,
        )

    async def execute(
        self, statement, params=None, execution_options=EMPTY_DICT, bind_arguments=None, **kw
    ):
        execution_options, kw = self._inject_default_execution_options(
            execution_options=execution_options, kw=kw
        )
        bind_arguments, kw = self._inject_default_bind_arguments(
            bind_arguments=bind_arguments, kw=kw
        )
        return await super().execute(
            statement,
            params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw,
        )

    async def connection(self, **kw):
        execution_options, kw = self._inject_default_execution_options(kw=kw)
        bind_arguments, kw = self._inject_default_bind_arguments(
            bind_arguments=bind_arguments, kw=kw
        )
        return await super().connection(**kw)
