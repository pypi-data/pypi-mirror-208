from sqlalchemy.ext.horizontal_shard import ShardedSession
from sqlalchemy.util import EMPTY_DICT

from constellate.database.sqlalchemy.session.binder.binderresolver import BinderResolver
from constellate.database.sqlalchemy.session.multienginesession import (
    _InjectDefaultExecutionOptions,
    _ConfigManager,
)
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager
from constellate.datatype.dictionary.pop import pop_param_when_available


class SyncMultiEngineShardSession(ShardedSession, _InjectDefaultExecutionOptions, _ConfigManager):
    def __init__(
        self,
        owner=None,
        config_manager: SQLAlchemyDbConfigManager = None,
        binder_resolver: BinderResolver = None,
        **kwargs,
    ):
        # Unsupported params in parent class
        execution_options = pop_param_when_available(
            kwargs=kwargs, key="execution_options", default_value={}
        )
        bind_arguments = pop_param_when_available(
            kwargs=kwargs, key="bind_arguments", default_value={}
        )

        super().__init__(**kwargs)
        self._owner = owner
        self._config_manager = config_manager
        self._default_execution_options = execution_options
        self._default_bind_arguments = bind_arguments

        default_binder = super()
        self._bind_resolver = (
            BinderResolver(resolvers=[default_binder])
            if binder_resolver is None
            else binder_resolver
        )

    def get_bind(self, mapper=None, shard_id=None, instance=None, clause=None, **kw):
        if shard_id is not None:
            return self._ShardedSession__binds[shard_id]

        return self._bind_resolver.get_bind(
            mapper=mapper, shard_id=shard_id, instance=instance, clause=clause, **kw
        )

    def execute(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        _parent_execute_state=None,
        _add_event=None,
        **kw,
    ):
        execution_options, kw = self._inject_default_execution_options(
            execution_options=execution_options, kw=kw
        )
        bind_arguments, kw = self._inject_default_bind_arguments(
            bind_arguments=bind_arguments, kw=kw
        )
        # Hint super() to use the proper super class. Details: https://bugs.python.org/issue15753
        return super().execute(
            statement,
            params,
            execution_options,
            bind_arguments,
            _parent_execute_state,
            _add_event,
            **kw,
        )

    def connection(
        self, bind_arguments=None, close_with_result=False, execution_options=None, **kw
    ):
        execution_options, kw = self._inject_default_execution_options(
            execution_options=execution_options, kw=kw
        )
        bind_arguments, kw = self._inject_default_bind_arguments(
            bind_arguments=bind_arguments, kw=kw
        )
        return super().connection(bind_arguments, close_with_result, execution_options, **kw)
