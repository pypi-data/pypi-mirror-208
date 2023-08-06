# CompositeType without auto type registration (to support asyncpg)
# src:
# https://github.com/kvesteri/sqlalchemy-utils/blob/master/sqlalchemy_utils/types/pg_composite.py#L163
"""
CompositeType provides means to interact with
`PostgreSQL composite types`_. Currently this type features:

* Easy attribute access to composite type fields
* Supports SQLAlchemy TypeDecorator types
* Ability to include composite types as part of PostgreSQL arrays
* Type creation and dropping

Installation
^^^^^^^^^^^^

CompositeType automatically attaches `before_create` and `after_drop` DDL
listeners. These listeners create and drop the composite type in the
database. This means it works out of the box in your test environment where
you create the tables on each test run.

When you already have your database set up you should call
:func:`register_composites_asyncpg` after you've set up all models.

::

    await register_composites(conn)



Usage (psycopg2)
^^^^^

::

    from collections import OrderedDict

    import sqlalchemy as sa
    from sqlalchemy_utils import CompositeType, CurrencyType


    class Account(Base):
        __tablename__ = 'account'
        id = sa.Column(sa.Integer, primary_key=True)
        balance = sa.Column(
            CompositeType(
                'money_type',
                [
                    sa.Column('currency', CurrencyType),
                    sa.Column('amount', sa.Integer)
                ]
            )
        )


Usage (psycopg2)
^^^^^

::

    from collections import OrderedDict

    import sqlalchemy as sa
    from sqlalchemy_utils import CompositeType, CurrencyType

    @dataclass
    class Balance:
        amount: int = None
        currency: ... = None

    class Account(Base):
        __tablename__ = 'account'
        id = sa.Column(sa.Integer, primary_key=True)
        balance = sa.Column(
            CompositeType(
                driver=DriverType.ASYNCPG,
                name='money_type',
                columns=[
                    sa.Column('currency', CurrencyType),
                    sa.Column('amount', sa.Integer)
                ],
                result_class=Balance
            )
        )



Creation
~~~~~~~~
When creating CompositeType, you can either pass in:
 - (psycopg2) a tuple or a dictionary
 - (asyncpg) a dataclass.

::
    account1 = Account()
    account1.balance = ('USD', 15)

    account2 = Account()
    account2.balance = {'currency': 'USD', 'amount': 15}

    account3 = Account()
    account3.balance = Balance(currency='USD', amount=15} # asyncpg only

    session.add(account1)
    session.add(account2)
    session.add(account3)
    session.commit()


Accessing fields
^^^^^^^^^^^^^^^^

CompositeType provides attribute access to underlying fields. In the following
example we find all accounts with balance amount more than 5000.


::

    session.query(Account).filter(Account.balance.amount > 5000)


Arrays of composites
^^^^^^^^^^^^^^^^^^^^

::

    from sqlalchemy.dialects.postgresql import ARRAY


    class Account(Base):
        __tablename__ = 'account'
        id = sa.Column(sa.Integer, primary_key=True)
        balances = sa.Column(
            ARRAY(
                CompositeType(
                    'money_type',
                    [
                        sa.Column('currency', CurrencyType),
                        sa.Column('amount', sa.Integer)
                    ]
                ),
                dimensions=1
            )
        )


.. _PostgreSQL composite types:
    http://www.postgresql.org/docs/current/static/rowtypes.html


Related links:

http://schinckel.net/2014/09/24/using-postgres-composite-types-in-django/
"""

from collections import namedtuple
from enum import Enum
from typing import List, Callable, Type, Dict, Union, Tuple

import six
import sqlalchemy as sa
from sqlalchemy import types, Column
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import _CreateDropBase
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.types import (
    SchemaType,
    to_instance,
    TypeDecorator,
    UserDefinedType,
)

# from .. import ImproperlyConfigured

# psycopg2 support
psycopg2 = None
CompositeCaster = None
adapt = None
AsIs = None
register_adapter = None
try:
    import psycopg2
    from psycopg2.extensions import adapt, AsIs, register_adapter
    from psycopg2.extras import CompositeCaster
except ImportError:
    pass

# asyncpg support
asyncpg = None
AsyncPGRecord = None
AsyncPGConnection = None
try:
    import asyncpg
    from asyncpg import Record as AsyncPGRecord
    from asyncpg import Connection as AsyncPGConnection
except ImportError:
    pass


class DriverType(Enum):
    PSYCOPG2 = 'psycopg2'
    ASYNCPG = 'asyncpg'


class CompositeElement(FunctionElement):
    """
    Instances of this class wrap a Postgres composite type.
    """

    def __init__(self, base, field, type_):
        self.name = field
        self.type = to_instance(type_)

        super(CompositeElement, self).__init__(base)


@compiles(CompositeElement)
def _compile_pgelem(expr, compiler, **kw):
    return '(%s).%s' % (compiler.process(expr.clauses, **kw), expr.name)


# TODO: Make the registration work on connection level instead of global level
registered_composites = {
    DriverType.PSYCOPG2: {},
    DriverType.ASYNCPG: {},
}


class CompositeType(types.UserDefinedType):
    # CompositeType without auto type registration (to support asyncpg)
    # src:
    # https://github.com/kvesteri/sqlalchemy-utils/blob/master/sqlalchemy_utils/types/pg_composite.py#L163

    python_type = tuple

    class comparator_factory(UserDefinedType.Comparator):

        def __getattr__(self, key):
            try:
                type_ = self.type.typemap[key]
            except KeyError:
                raise KeyError("Type '%s' doesn't have an attribute: '%s'" %
                               (self.name, key))

            return CompositeElement(self.expr, key, type_)

    def __init__(self,
                 driver: DriverType = DriverType.PSYCOPG2,
                 name: str = None,
                 columns: List[Column] = None,
                 result_class: Union[Callable, Type] = None):
        """
        driver: The driver for which this composite type will be used on
        name: Name must be lower case (since all custom types are lowercase in Postgres internal tables)
        columns: List of columns with their attributes
        result_class: Datatype to be return when reading from the database. result_class.__init__ must accept keyword arguments
        """
        # if driver == DriverType.PSYCOPG2 and psycopg2 is None:
        #     raise ImproperlyConfigured(
        #         "'psycopg2' package is required in order to use CompositeType."
        #     )
        # if driver == DriverType.ASYNCPG and asyncpg is None:
        #     raise ImproperlyConfigured(
        #         "'asyncpg' package is required in order to use CompositeTypeAsyncPG."
        #     )

        SchemaType.__init__(self)
        self.name = name
        self.columns = columns
        self.driver = driver
        self.__result_class = result_class

        def _read_db_record_column_generic(value, key):
            return getattr(value, key)

        def _read_db_record_column_asyncpg(value, key):
            return value[key]

        self.__read_db_record_column = {
            DriverType.ASYNCPG: _read_db_record_column_asyncpg
        }.get(driver, _read_db_record_column_generic)

        def _read_client_record_column_generic(value, column, index):
            return (value.get(column.name)
                    if isinstance(value, dict) else value[index])

        def _read_client_record_column_asyncpg(value, column, index):
            return getattr(value, column.name)

        self.__read_client_record_column = {
            DriverType.ASYNCPG: _read_client_record_column_asyncpg
        }.get(driver, _read_client_record_column_generic)

        def _create_native_record_generic(value, kwargs, class_):
            return value.__class__(**kwargs)

        def _create_native_record_asyncpg(value, kwargs, class_):
            return class_(**kwargs)

        self.__create_native_record = {
            DriverType.ASYNCPG: _create_native_record_asyncpg
        }.get(driver, _create_native_record_generic)

        _register_composite(driver=driver, composite=self)

        class CasterPsycoPG(CompositeCaster):

            def make(obj, values):
                return self.type_cls(*values)

        self.caster = CasterPsycoPG if driver == DriverType.PSYCOPG2 else None

        attach_composite_listeners()

    def get_col_spec(self) -> str:
        return self.name

    def bind_processor(self, dialect: PGDialect) -> Callable:
        # App value to DB value
        def process(value: Dict):
            if value is None:
                return None

            processed_value = []
            for i, column in enumerate(self.columns):
                current_value = self.__read_client_record_column(
                    value, column, i)

                if isinstance(column.type, TypeDecorator):
                    processed_value.append(
                        column.type.process_bind_param(current_value, dialect))
                else:
                    processed_value.append(current_value)
            return self.type_cls(*processed_value)

        return process

    def result_processor(self, dialect: PGDialect, coltype: int) -> Callable:
        # DB value to App value

        def process(value: AsyncPGRecord):
            if value is None:
                return None
            kwargs = {}
            for column in self.columns:
                if isinstance(column.type, TypeDecorator):
                    kwargs[column.name] = column.type.process_result_value(
                        self.__read_db_record_column(value, column.name),
                        dialect)
                else:
                    kwargs[column.name] = self.__read_db_record_column(
                        value, column.name)
            return self.__create_native_record(value, kwargs,
                                               self.__result_class)

        return process


class CompositeTypeAsyncPG(CompositeType):

    # Force key/value access
    python_type = None

    def __init__(self,
                 name: str = None,
                 columns: List[Column] = None,
                 result_class: Union[Callable, Type] = None):
        super(CompositeTypeAsyncPG, self).__init__(driver=DriverType.ASYNCPG,
                                                   name=name,
                                                   columns=columns,
                                                   result_class=result_class)


async def _register_asyncpg_composite(dbapi_connection: AsyncPGConnection,
                                      composite: Type[CompositeType],
                                      schema: str = 'public',
                                      **kwargs):

    def _encode(value: CompositeType) -> Tuple:
        adapted = [
            getattr(value, column.name)
            if not isinstance(column.type, TypeDecorator) else
            column.type.process_bind_param(getattr(value, column.name),
                                           PGDialect_asyncpg())
            for column in value.columns
        ]

        for value in adapted:
            if hasattr(value, 'prepare'):
                value.prepare(dbapi_connection)

        # (col1_value, col2_value, ...)
        return tuple(adapted)

    def _decode(value: Tuple) -> CompositeType:
        kwargs = {
            column.name: value[index]
            for index, column in enumerate(composite.columns)
        }
        return composite(**kwargs)

    await dbapi_connection.set_type_codec(
        composite.name,
        schema=schema,
        encoder=_encode,
        decoder=_decode,
        format='tuple',
    )


async def _register_psycopg2_composite(dbapi_connection, composite, **kwargs):
    psycopg2.extras.register_composite(composite.name,
                                       dbapi_connection,
                                       globally=True,
                                       factory=composite.caster)

    def adapt_composite(value):
        adapted = [
            adapt(
                getattr(value, column.name)
                if not isinstance(column.type, TypeDecorator) else column.type.
                process_bind_param(getattr(value, column.name
                                           ), PGDialect_psycopg2()))
            for column in composite.columns
        ]
        for value in adapted:
            if hasattr(value, 'prepare'):
                value.prepare(dbapi_connection)
        values = [
            value.getquoted().decode(dbapi_connection.encoding)
            if six.PY3 else value.getquoted() for value in adapted
        ]
        return AsIs("(%s)::%s" % (', '.join(values), composite.name))

    register_adapter(composite.type_cls, adapt_composite)


def before_create(target, connection, **kw):
    for name, composite in registered_composites.items():
        composite.create(connection, checkfirst=True)
        _register_psycopg2_composite(connection.connection.connection,
                                     composite)


def after_drop(target, connection, **kw):
    for name, composite in registered_composites.items():
        composite.drop(connection, checkfirst=True)


def _register_composite(driver: DriverType = DriverType.PSYCOPG2,
                        composite: CompositeType = None):
    if composite.name in registered_composites[driver]:
        composite.type_cls = registered_composites[driver][
            composite.name].type_cls
    else:
        composite.type_cls = namedtuple(composite.name,
                                        [c.name for c in composite.columns])
    registered_composites[driver][composite.name] = composite


# async def register_composites(connection: Union[AsyncPGConnection],
#                               driver: DriverType = DriverType.PSYCOPG2,
#                               **kwargs):
#     """
#     Register pre-registered composite types at connection level.
#     """
#
#     register_composite = {
#         DriverType.PSYCOPG2: _register_psycopg2_composite,
#         DriverType.ASYNCPG: _register_asyncpg_composite,
#     }.get(driver, None)
#
#     for name, composite in registered_composites[driver].items():
#         await register_composite(connection, composite, **kwargs)


def attach_composite_listeners():
    listeners = [
        (sa.MetaData, 'before_create', before_create),
        (sa.MetaData, 'after_drop', after_drop),
    ]
    for listener in listeners:
        if not sa.event.contains(*listener):
            sa.event.listen(*listener)


def remove_composite_listeners():
    listeners = [
        (sa.MetaData, 'before_create', before_create),
        (sa.MetaData, 'after_drop', after_drop),
    ]
    for listener in listeners:
        if sa.event.contains(*listener):
            sa.event.remove(*listener)


class CreateCompositeType(_CreateDropBase):
    pass


@compiles(CreateCompositeType)
def _visit_create_composite_type(create, compiler, **kw):
    type_ = create.element
    fields = ', '.join('{name} {type}'.format(
        name=column.name,
        type=compiler.dialect.type_compiler.process(to_instance(column.type)))
                       for column in type_.columns)

    return 'CREATE TYPE {name} AS ({fields})'.format(
        name=compiler.preparer.format_type(type_), fields=fields)


class DropCompositeType(_CreateDropBase):
    pass


@compiles(DropCompositeType)
def _visit_drop_composite_type(drop, compiler, **kw):
    type_ = drop.element

    return 'DROP TYPE {name}'.format(name=compiler.preparer.format_type(type_))
