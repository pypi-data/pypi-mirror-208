from sqlalchemy import Column, String, Integer

from constellate.database.migration.constant import MigrationKind, MigrationAction
from constellate.database.migration.standard.base import Base
from constellate.database.sqlalchemy.typedecorator.enumstring import EnumString
from constellate.database.sqlalchemy.typedecorator.timestamptz import TimestampTZ


# Abstract SQLAlchemy tables for unit test to override __table__args for instance


class _MigrationR(Base):
    __abstract__ = True
    __tablename__ = "_migration"

    migration_hash = Column(String, primary_key=True)
    migration_id = Column(String)
    action = Column(EnumString(enum_type=MigrationAction))
    kind = Column(EnumString(enum_type=MigrationKind))
    applied_at = Column(TimestampTZ)
    parent_hash = Column(String)


class _MigrationVersionR(Base):
    __abstract__ = True
    __tablename__ = "_migration_version"

    version = Column(Integer, primary_key=True)
    created_at = Column(TimestampTZ)


class _MigrationVersionR(_MigrationVersionR):
    __abstract__ = True
    __tablename__ = _MigrationVersionR.__tablename__

    version = Column(Integer, primary_key=True)
    created_at = Column(TimestampTZ)


class _MigrationActivityR(Base):
    __abstract__ = True
    __tablename__ = "_migration_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    migration_hash = Column(String)
    migration_id = Column(String)
    action = Column(EnumString(enum_type=MigrationAction))
    username = Column(String)
    hostname = Column(String)
    created_at = Column(TimestampTZ)
    kind = Column(EnumString(enum_type=MigrationKind))


class _MigrationLockR(Base):
    __abstract__ = True
    __tablename__ = "_migration_lock"

    id = Column(Integer, primary_key=True, autoincrement=False)


# Default concrete SQLAlchemy tables for library users


class MigrationR(_MigrationR):
    __tablename__ = _MigrationR.__tablename__
    __table_args__ = {"schema": "per_unit"}


class MigrationVersionR(_MigrationVersionR):
    __tablename__ = _MigrationVersionR.__tablename__
    __table_args__ = {"schema": "per_unit"}


class MigrationActivityR(_MigrationActivityR):
    __tablename__ = _MigrationActivityR.__tablename__
    __table_args__ = {"schema": "per_unit"}


class MigrationLockR(_MigrationLockR):
    __tablename__ = _MigrationLockR.__tablename__
    __table_args__ = {"schema": "per_unit"}


_MIGRATION_TABLES = [MigrationR, MigrationActivityR, MigrationVersionR, MigrationLockR]
