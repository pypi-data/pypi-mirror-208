from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy_mixins.repr import ReprMixin

m = MetaData()
SQABase = declarative_base()


class Base(SQABase, ReprMixin):
    __abstract__ = True
    __repr__ = ReprMixin.__repr__

    # Multi tenant db:
    # https://docs.sqlalchemy.org/en/14/changelog/migration_11.html#multi-tenancy-schema-translation-for-table-objects
    __table_args__ = {"schema": "per_unit"}
