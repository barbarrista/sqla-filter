from typing import Annotated
from uuid import UUID

from sqlalchemy.sql.operators import eq

from sqla_filter import UNSET, BaseFilter, FilterField, Unset
from tests.sqla_filter.common.models import Book


def test_base_filter() -> None:
    class Filter(BaseFilter):
        second_manually_filter: list[UUID]
        first_manually_filter: UUID | None = None
        manually_filter_field: UUID | None = None
        ident: Annotated[UUID | Unset, FilterField(Book.id, operator=eq)] = UNSET

    filter_ = Filter(second_manually_filter=[])

    assert filter_.ident is UNSET
    assert filter_.second_manually_filter == []
    assert filter_.first_manually_filter is None
