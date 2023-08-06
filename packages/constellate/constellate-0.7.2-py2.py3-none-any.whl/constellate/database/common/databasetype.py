from enum import Enum, auto


class DatabaseType(Enum):
    UNKNOWN = auto()
    POSTGRESQL = auto()
    SQLITE = auto()
