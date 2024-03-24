from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy.sql.operators import eq, ge, icontains_op, in_op, le

from sqla_filter import UNSET, BaseFilter, FilterField, RelationshipInfo, Unset

from .models import Author, Book, Review


@dataclass(frozen=True, slots=True)
class DateTimeInterval:
    from_: datetime
    to: datetime


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

    created_at_between: Annotated[
        DateTimeInterval | Unset,
        FilterField(
            Book.created_at,
            operator=lambda field, value: field.between(value.from_, value.to),
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
        Sequence[UUID] | Unset,
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
    process_manually_field: str | Unset = UNSET
