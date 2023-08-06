from typing import List, Union

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.base import Executable


class TruncateTable(Executable, ClauseElement):
    def __init__(
        self,
        element: Union[object, List[object]] = None,
        restart_identity: bool = False,
        cascade: bool = False,
    ):
        self.table = element
        self._option_restart_identity = restart_identity
        self._option_cascade = cascade


@compiles(TruncateTable)
def _visit_truncate(element, compiler, **kw):
    raise NotImplementedError()


@compiles(TruncateTable, "postgresql")
def _visit_truncate(element, compiler, **kw):
    options = " ".join(
        filter(
            lambda x: x is not None,
            [
                "RESTART IDENTITY" if element._option_restart_identity else None,
                "CASCADE" if element._option_cascade else None,
            ],
        )
    )
    tables = ", ".join([compiler.process(t.__table__, asfrom=True, **kw) for t in element.table])
    return "TRUNCATE %s %s" % (tables, options)
