from typing import cast

from sqla_filter.types_ import SelectClause
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.compiler import SQLCompiler


def compile_stmt(stmt: SelectClause) -> SQLCompiler:
    return cast(
        "SQLCompiler",
        stmt.compile(
            dialect=postgresql.dialect(),  # type:ignore[no-untyped-call]
            compile_kwargs={"literal_binds": True},
        ),
    )
