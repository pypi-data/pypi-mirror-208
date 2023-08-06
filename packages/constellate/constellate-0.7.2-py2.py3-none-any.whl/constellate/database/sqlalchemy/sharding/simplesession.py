from typing import Dict

from constellate.database.sqlalchemy.session.multienginesession import MultiEngineSession
from constellate.database.sqlalchemy.session.syncmultienginesession import (
    SyncMultiEngineSession,
)
from constellate.database.sqlalchemy.session.syncmultiengineshardsession import (
    SyncMultiEngineShardSession,
)
from constellate.database.sqlalchemy.sharding.unittoshardmixin import UnitToShardMixin
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager
from sqlalchemy.util._collections import EMPTY_DICT


class SimpleToShardMixin(UnitToShardMixin):
    def __int__(self, data: Dict = None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

    def _get_shard_id_for_unit(self, **kwargs) -> str:
        return self._data.get()


class SimpleShardSession(MultiEngineSession, SimpleToShardMixin):
    def __init__(self, owner=None, config_manager: SQLAlchemyDbConfigManager = None, **kwargs):
        data = kwargs.pop("data", None)
        super().__init__(
            owner=owner,
            config_manager=config_manager,
            data={},
            **kwargs,
        )
        UnitToShardMixin.__init__(self, data=data, **kwargs)


class SyncSimpleShardSession(SyncMultiEngineShardSession, SimpleToShardMixin):
    def __init__(self, owner=None, config_manager: SQLAlchemyDbConfigManager = None, **kwargs):
        data = kwargs.pop("data", None)
        super().__init__(owner=owner, config_manager=config_manager, **kwargs)
        SimpleToShardMixin.__init__(data=data, **kwargs)


class SyncSimpleSession(SyncMultiEngineSession, SimpleToShardMixin):
    def __init__(self, owner=None, config_manager: SQLAlchemyDbConfigManager = None, **kwargs):
        data = kwargs.pop("data", None)
        super().__init__(owner=owner, config_manager=config_manager, **kwargs)
        SimpleToShardMixin.__init__(data=data, **kwargs)

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
