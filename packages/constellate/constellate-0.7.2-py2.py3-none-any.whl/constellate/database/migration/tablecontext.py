import attr as attr

from constellate.database.migration.standard.table import (
    MigrationR,
    MigrationActivityR,
    MigrationVersionR,
    MigrationLockR,
)


@attr.s(kw_only=True, auto_attribs=True)
class TableContext:
    migration: MigrationR = None
    activity: MigrationActivityR = None
    version: MigrationVersionR = None
    lock: MigrationLockR = None
