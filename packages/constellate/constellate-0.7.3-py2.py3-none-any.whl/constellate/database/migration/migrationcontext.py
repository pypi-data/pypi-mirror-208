from enum import auto, Enum
from pathlib import Path
from typing import Tuple, List, Union, Callable, Any

import attr as attr
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from typing import AsyncContextManager

from constellate.database.common.databasetype import DatabaseType
from constellate.database.migration.constant import (
    ScriptType,
    MigrationKind,
    MigrationCompatibility,
    Mark,
    MigrationAction,
)


@attr.s(kw_only=True, auto_attribs=True)
class MigrationStepFile:
    kind: MigrationKind = None
    file: Path = None
    transactional: bool = None
    parent: Union[str, "MigrationStepFile"] = None
    schema: Union[str, List[str]] = None
    py_module: Any = None
    mark_behaviour: Mark = None

    @property
    def type(self) -> ScriptType:
        return {".sql": ScriptType.SQL, ".py": ScriptType.PYTHON}.get(
            self.file.suffix, ScriptType.UNKNOWN
        )


@attr.s(kw_only=True, auto_attribs=True)
class MigrationStepContext:
    kind: MigrationKind = None
    schema: Tuple[str, List[str]] = None
    step_files: List[MigrationStepFile] = None


class ConnectionResolution(Enum):
    SESSION_CREATE = auto()
    SESSION = auto()
    ENGINE = auto()
    CONNECTION_URL = auto()


@attr.s(kw_only=True, auto_attribs=True)
class ConnectionContext:
    connection_url: str = None
    engine: AsyncEngine = None
    session: AsyncSession = None
    session_create: Callable[[AsyncEngine], AsyncContextManager[AsyncSession]] = None
    # Order in which the migration tool will try to acquire a session or create one
    resolution: List[ConnectionResolution] = [
        ConnectionResolution.SESSION_CREATE,
        ConnectionResolution.SESSION,
        ConnectionResolution.ENGINE,
        ConnectionResolution.CONNECTION_URL,
    ]


@attr.s(kw_only=True, auto_attribs=True)
class MigrationLimitedRun:
    # Create library migration tables. False not to create them
    table_created: bool = True
    # Populate library migration tables. False not to fill them
    table_populated: bool = True
    # Populate migration table up to a particular script is executed (included)
    # None = No limit
    table_populated_up_to_file: Path = None
    # Check migration files to run next logically follow the ones already migrated
    # True: allow any migration file to be run next
    # False: enforce logical check
    skip_migration_continuity_check: bool = False
    # Execute python/sql script
    # False: execute scripts
    # True: don't execute scripts
    skip_executing_script: bool = False


@attr.s(kw_only=True, auto_attribs=True)
class MigrationContext:
    database_type: DatabaseType = None
    compatibility: MigrationCompatibility = MigrationCompatibility.V0
    action: MigrationAction = None
    # Directory/Module containing various folders named 0001... 0002....
    root_pkg_name: object = None
    directory: str = None
    connection_context: ConnectionContext = None
    # Each folder named 0001 ... 0002... has multiple migration steps
    steps: List[MigrationStepContext] = attr.ib(default=attr.Factory(list))
    migration_context_step_name: str = None
    # List of schema:
    # - 'schema1'
    # - OR ['schema1', 'public']
    schema: Tuple[str, List[str]] = None
    kind: MigrationKind = None
    dry: MigrationLimitedRun = MigrationLimitedRun(
        table_created=True, table_populated=True, table_populated_up_to_file=None
    )
