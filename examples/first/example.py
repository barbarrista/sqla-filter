import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.sql.operators import eq, ge, icontains_op, in_op, le

from examples.models import Author, Book, Review
from sqla_filter.base import BaseFilter
from sqla_filter.filter_ import (
    UNSET,
    FilterField,
    RelationshipInfo,
    Unset,
)


class BookFilter(BaseFilter):
    ident: Annotated[UUID | Unset, FilterField(Book.id, operator=eq)] = UNSET
    created_at_from: Annotated[
        datetime | Unset,
        FilterField(Book.created_at, operator=ge),
    ] = UNSET
    created_at_to: Annotated[
        datetime | Unset,
        FilterField(Book.created_at, operator=le),
    ] = UNSET
    something: Annotated[
        datetime | Unset,
        FilterField(Book.created_at, operator=lambda field, value: field.in_(value)),
    ] = UNSET

    author_ids: Annotated[
        Sequence[UUID] | Unset,
        FilterField(
            Author.id,
            operator=in_op,
            relationship=RelationshipInfo(field=Book.authors),
        ),
    ] = UNSET
    review_ids: Annotated[
        list[UUID] | Unset,
        FilterField(
            Review.id,
            operator=in_op,
            relationship=RelationshipInfo(field=Book.reviews),
        ),
    ] = UNSET
    review_content_contains: Annotated[
        str | Unset,
        FilterField(
            Review.content,
            operator=icontains_op,
            relationship=RelationshipInfo(field=Book.reviews),
        ),
    ] = UNSET


def main() -> None:
    stmt = select(Book)
    print_stmt(stmt)

    now = datetime.now(tz=UTC)
    filter_ = BookFilter(
        ident=uuid.uuid4(),
        author_ids=[uuid.uuid4()],
        review_content_contains="Review Content",
        created_at_from=now,
        created_at_to=now + timedelta(days=1),
    )

    stmt = filter_.apply(stmt)
    print_stmt(stmt)


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


if __name__ == "__main__":
    main()
