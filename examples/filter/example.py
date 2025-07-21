import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.sql.operators import eq, ge, icontains_op, in_op, le

from examples.models import Author, Book, Review, User
from examples.utils import print_stmt
from sqla_filter import (
    UNSET,
    BaseFilter,
    FilterField,
    RelationshipInfo,
    SupportsOrFilter,
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
    author_user_id: Annotated[
        UUID | Unset,
        FilterField(
            User.id,
            operator=eq,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
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


class BookOrFilter(SupportsOrFilter):
    ident: Annotated[UUID | Unset, FilterField(Book.id, operator=eq)] = UNSET


def main_or() -> None:
    stmt = select(Book)
    print_stmt(stmt)

    filter_ = BookOrFilter(
        ident=uuid.uuid4(),
        or_=BookOrFilter(ident=UUID("00000000-0000-0000-0000-000000000001")),
    )

    stmt = filter_.apply(stmt)
    print_stmt(stmt)


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


if __name__ == "__main__":
    main()
