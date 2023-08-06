import sys
import threading
from typing import Any, Dict

from sqlalchemy.exc import UnboundExecutionError

from constellate.database.sqlalchemy.sharding.shardoption import SetShardEngineOption
from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager


class Sharder:
    """A shard is a database, referenced by a "shard id", itself an alias for a `SQLAlchemyDBConfig.identifier`
    A sharder bridge associate a shard to a particular execution context: query, table primary key, etc.
    See xxxx_chooser for details.


    """

    def __init__(self, config_manager: SQLAlchemyDbConfigManager = None):
        self._config_manager = config_manager
        self._lock_get_bind = threading.Lock()

    def shard_chooser(self, mapper, instance, clause=None):
        """Given a row instance (ie a row of a table), return the list of shard ids

        :param mapper:
        :param instance:
        :param clause:  (Default value = None)

        """
        return self._get_shard_ids_for_context(
            max_full_shard_id=1, mapper=mapper, clause=clause, instance=instance
        )

    def id_chooser(self, query, ident):
        """Given a table's primary key, return the list of shard ids

        :param query:
        :param ident:

        """
        return self._get_shard_ids_for_context(
            max_full_shard_id=sys.maxsize, query=query, ident=ident
        )

    def execute_chooser(self, orm_context):
        """, return the list of shard ids

        :param orm_context:

        """
        return self._get_shard_ids_for_context(
            max_full_shard_id=sys.maxsize, orm_context=orm_context
        )

    def _get_shard_ids_for_context(
        self,
        max_full_shard_id: int = 0,
        mapper: Any = None,
        clause: Any = None,
        instance: Any = None,
        query: Any = None,
        ident: Any = None,
        orm_context: Any = None,
    ):
        def update_when_non_null(
            kwargs: Dict = None, key: Any = None, value: Any = None, force: bool = False
        ):
            if value is not None:
                kwargs.update({key: value})
            if value is not None and force:
                kwargs.update({key: value})

        kwargs = {}
        update_when_non_null(kwargs=kwargs, key="config_manager", value=self._config_manager)
        update_when_non_null(kwargs=kwargs, key="mapper", value=mapper)
        update_when_non_null(kwargs=kwargs, key="clause", value=clause)
        update_when_non_null(kwargs=kwargs, key="instance", value=instance)
        update_when_non_null(kwargs=kwargs, key="query", value=query)
        update_when_non_null(kwargs=kwargs, key="ident", value=ident)
        update_when_non_null(kwargs=kwargs, key="orm_context", value=orm_context)

        config = None
        if mapper is not None or clause is not None:
            config = self._get_config_for_context(**kwargs)
        elif mapper is None and (query is not None or ident is not None):
            # if we are in a lazy load, we can look at the parent object
            # and limit our search to that same shard, assuming that's how we've
            # set things up.
            # https://github.com/sqlalchemy/sqlalchemy/discussions/6885#discussioncomment-1522561
            ident = (
                query.lazy_loaded_from.identity_token
                if hasattr(query, "lazy_loaded_from") and query.lazy_loaded_from
                else ident
            )
            update_when_non_null(kwargs=kwargs, key="ident", value=ident, force=True)
            config = self._get_config_for_context(**kwargs)
        elif orm_context is not None:
            update_when_non_null(
                kwargs=kwargs, key="mapper", value=orm_context.bind_mapper, force=True
            )
            update_when_non_null(
                kwargs=kwargs, key="execution_options", value=orm_context.execution_options
            )
            kwargs.pop("orm_context")
            config = self._get_config_for_context(**kwargs)
        else:
            raise NotImplementedError()

        return config.identifier if max_full_shard_id <= 1 else [config.identifier]

    def _get_config_for_context(
        self,
        config_manager: SQLAlchemyDbConfigManager = None,
        mapper: Any = None,
        clause: Any = None,
        instance: Any = None,
        ident: Any = None,
        query: Any = None,
        execution_options: Dict = None,
    ) -> SQLAlchemyDBConfig:
        """Find the SQLAlchemyDBConfig instance the current context wants to use execute SQL request upon

        :param config_manager: SQLAlchemyDbConfigManager:  (Default value = None)
        :param mapper: Any:  (Default value = None)
        :param clause: Any:  (Default value = None)
        :param instance: Any:  (Default value = None)
        :param ident: Any:  (Default value = None)
        :param query: Any:  (Default value = None)
        :param execution_options: Dict:  (Default value = None)

        """

        def bound_to_default_session_shard_id(instance: Any = None):
            return (
                instance is not None
                and instance._sa_instance_state.session._default_bind_arguments.get(
                    "shard_id", None
                )
                is not None
            )

        def bound_to_default_session_shard_id2(execution_options: Dict = None):
            return (
                execution_options is not None
                and execution_options.get("shard_id", None) is not None
            )

        def bound_to_dynamically_generated_table_shard_id(instance: Any = None):
            return (
                instance is not None
                and hasattr(instance, "metadata")
                and instance.metadata is not None
                and "shard_id" in instance.metadata.info
            )

        with self._lock_get_bind:
            if bound_to_dynamically_generated_table_shard_id(instance=instance):
                shard_id = instance.metadata.info.get("shard_id")
                return config_manager.get(identifier=shard_id)
            elif bound_to_default_session_shard_id(instance=instance):
                session = instance._sa_instance_state.session
                shard_id = session._default_bind_arguments.get("shard_id")
                shard_id = (
                    shard_id.payload if isinstance(shard_id, SetShardEngineOption) else shard_id
                )
                return session.config_manager.get(identifier=shard_id)
            elif bound_to_default_session_shard_id2(execution_options=execution_options):
                shard_id = execution_options.get("shard_id")
                shard_id = (
                    shard_id.payload if isinstance(shard_id, SetShardEngineOption) else shard_id
                )
                return config_manager.get(identifier=shard_id)
            else:
                raise UnboundExecutionError()
