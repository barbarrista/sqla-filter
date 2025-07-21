from typing import Any

from sqlalchemy import Select


def print_stmt(stmt: Select[tuple[Any, ...]]) -> None:
    from sqlalchemy.dialects import postgresql

    print(  # noqa: T201
        stmt.compile(
            dialect=postgresql.dialect(),  # type: ignore[no-untyped-call]
            compile_kwargs={
                "literal_binds": True,
            },
        ),
        "\n",
    )
