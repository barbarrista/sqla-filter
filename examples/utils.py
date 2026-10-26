from sqla_filter.types_ import SelectClause


def print_stmt(stmt: SelectClause) -> None:
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
