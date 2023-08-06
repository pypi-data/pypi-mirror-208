import logging
from enum import IntEnum, auto
from typing import Dict

import attr
from sqlalchemy.orm import sessionmaker

from constellate.database.sqlalchemy.sqlalchemyengineconfig import _EngineConfig
from constellate.database.sqlalchemy.sqlalchemymigrationconfig import _MigrationConfig


class DBConfigType(IntEnum):
    INSTANCE = auto()
    TEMPLATE = auto()


@attr.s(kw_only=True, frozen=False, eq=True, auto_attribs=True)
class SQLAlchemyDBConfig:
    # Generic Identification
    type: DBConfigType = None
    identifier: str = None
    # Engine conf
    engine_config: _EngineConfig = None
    # Session conf
    session_maker: sessionmaker = None
    # Logging conf
    logger: logging.Logger = None
    # Migration
    migration: _MigrationConfig = None
    # Misc conf
    options: Dict = None
