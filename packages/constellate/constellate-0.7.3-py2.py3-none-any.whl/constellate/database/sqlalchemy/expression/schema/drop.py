from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropSchema as SQADropSchema
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler


class DropSchema(SQADropSchema):
    """Drop a schema. This is an improved version of sqlalchemy.sql.ddl.DropSchema"""

    def __init__(
        self, name: str, quote: None = None, if_exists: bool = False, cascade: bool = False, **kw
    ) -> None:
        if quote is not None:
            kw.update({"quote": quote})
        super().__init__(name, **kw)
        self._option_if_exists = if_exists
        self._option_cascade = cascade


@compiles(DropSchema)
def _visit_drop_schema(element: DropSchema, compiler: PGDDLCompiler, **kw) -> str:
    raise NotImplementedError()


@compiles(DropSchema, "postgresql")
def _visit_drop_schema(element: DropSchema, compiler: PGDDLCompiler, **kw) -> str:
    pre_options = " ".join(
        filter(lambda x: x is not None, ["IF EXISTS" if element._option_if_exists else None])
    )

    post_options = " ".join(
        filter(
            lambda x: x is not None,
            [f"CASCADE" if element._option_cascade else None],
        )
    )

    return f"DROP SCHEMA {pre_options} {element.element} {post_options}"
