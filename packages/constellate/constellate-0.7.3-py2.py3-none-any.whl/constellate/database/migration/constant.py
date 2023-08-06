from enum import Enum, auto, Flag

DEFAULT_CONTEXT_STEP_FILE_NAME = "__init__.py"
DEFAULT_POST_APPLY_FILE_NAMES = ["post-apply.sql", "post-apply.py"]
INVALID_MIGRATION_SCRIPT_FILE_NAMES = [f for f in [DEFAULT_CONTEXT_STEP_FILE_NAME]]
INVALID_MIGRATION_DIRECTORY_NAMES = ["__pycache__"]


class ScriptType(Enum):
    UNKNOWN = auto()
    SQL = auto()
    PYTHON = auto()


class MigrationKind(Enum):
    UNKNOWN = "unknown"
    SCHEMA = "schema"
    DATA = "data"


class MigrationCompatibility(Enum):
    V0 = "v0"


class Mark(Flag):
    MARK_ACTIVITY = auto()
    MARK_MIGRATION = auto()


class MigrationAction(Enum):
    UNKNOWN = "unknown"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
