from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateSchema as SQACreateSchema
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler


class CreateSchema(SQACreateSchema):
    """Create a schema. This is an improved version of sqlalchemy.sql.ddl.CreateSchema"""

    def __init__(
        self,
        name: str,
        quote: None = None,
        if_not_exists: bool = False,
        authorization: str = None,
        **kw,
    ) -> None:
        if quote is not None:
            kw.update({"quote": quote})
        super().__init__(name, **kw)
        self._option_if_not_exists = if_not_exists
        self._option_authorization = authorization


@compiles(CreateSchema)
def _visit_create_schema(element: CreateSchema, compiler: PGDDLCompiler, **kw) -> str:
    raise NotImplementedError()


@compiles(CreateSchema, "postgresql")
def _visit_create_schema(element: CreateSchema, compiler: PGDDLCompiler, **kw) -> str:
    pre_options = " ".join(
        filter(
            lambda x: x is not None, ["IF NOT EXISTS" if element._option_if_not_exists else None]
        )
    )

    post_options = " ".join(
        filter(
            lambda x: x is not None,
            [
                f"AUTHORIZATION {element._option_authorization}"
                if element._option_authorization
                else None
            ],
        )
    )

    return f"CREATE SCHEMA {pre_options} {element.element} {post_options}"
