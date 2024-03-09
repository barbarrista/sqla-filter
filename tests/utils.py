from typing import TypeVar

from sqlalchemy import Select
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.compiler import SQLCompiler

_T = TypeVar("_T")


def compile_stmt(stmt: Select[tuple[_T]]) -> SQLCompiler:
    return stmt.compile(
        dialect=postgresql.dialect(),  # type:ignore[no-untyped-call]
        compile_kwargs={"literal_binds": True},
    )
