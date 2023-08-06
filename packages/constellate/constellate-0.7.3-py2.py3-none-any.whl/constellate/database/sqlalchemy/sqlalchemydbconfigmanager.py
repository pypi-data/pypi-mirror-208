from typing import Optional, Callable, Iterable, Any

from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig, DBConfigType


class SQLAlchemyDbConfigManager:
    def __init__(self) -> None:
        self._instances = {}

    def update(self, instance: SQLAlchemyDBConfig = None) -> None:
        self._instances.update({instance.identifier: instance})

    def pop(self, identifier: str = None) -> None:
        self._instances.pop(identifier)

    def __iter__(self):
        return self._instances.items().__iter__()

    def get(self, identifier: str = None, default_value=None):
        return self._instances.get(identifier, default_value)

    def find(
        self, type: DBConfigType = DBConfigType.INSTANCE, identifier: str = None, **kwargs
    ) -> Optional[SQLAlchemyDBConfig]:
        """Find a SQLAlchemyDBConfig by identifier, type and other application provided settings

        :param type: DBConfigType:  (Default value = DBConfigType.INSTANCE)
        :param identifier: str:  (Default value = None)
        :param **kwargs:

        """
        return next(
            filter(
                lambda config: config.type == type and config.identifier == identifier,
                self._instances.values(),
            ),
            None,
        )

    def filter(
        self, key: Callable[[Any, SQLAlchemyDBConfig], bool] = None
    ) -> Iterable[SQLAlchemyDBConfig]:
        return [v for k, v in filter(key, list(self))]
