from typing import Dict, Callable

from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig, DBConfigType
from constellate.database.sqlalchemy.sqlalchemydbconfigmanager import SQLAlchemyDbConfigManager


class UnitToShardMixin:
    def __init__(
        self,
        config_manager: SQLAlchemyDbConfigManager = None,
        get_shard_id_for_unit: Callable[[Dict], str] = None,
        *args,
        **kwargs
    ):
        """
        Can be used to set a static table to map between an application defined unit and a shard
        """
        self._config_manager = config_manager
        self._fn_get_shard_id_for_unit = get_shard_id_for_unit

    def get_config_for_unit(self, **kwargs) -> SQLAlchemyDBConfig:
        """Get SQLAlchemyDBConfig for an application defined unit

        :param **kwargs:

        """
        if self._fn_get_shard_id_for_unit is not None:
            shard_id = self._fn_get_shard_id_for_unit(**kwargs)
        else:
            shard_id = self._get_shard_id_for_unit(**kwargs)
        return self.get_instance_config(identifier=shard_id)

    def get_instance_config(
        self, type: DBConfigType = DBConfigType.INSTANCE, identifier: str = None, **kwargs
    ) -> SQLAlchemyDBConfig:
        """Get the SQLALchemyConfig with identifier specified

        :param kwargs: Application defined settings to restrict the search for a suitable config
        :param type: DBConfigType:  (Default value = DBConfigType.INSTANCE)
        :param identifier: str:  (Default value = None)
        :param **kwargs:

        """
        return self._config_manager.find(type=type, identifier=identifier, **kwargs)

    def _get_shard_id_for_unit(self, **kwargs) -> str:
        """Get shard id for an application defined unit

        :param kwargs: Application defined settings to restrict the search for a suitable config
        :param **kwargs:
        :raises s: NotImplementedError if no shard can be found

        """
        # Sample implementation:
        # shard_id = self._data.get(kwargs['something])
        raise NotImplementedError()
