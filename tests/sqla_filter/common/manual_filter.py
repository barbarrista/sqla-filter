from datetime import datetime
from typing import TYPE_CHECKING, final

from sqla_filter.filter_ import ManualFilter
from sqlalchemy import Select

from tests.sqla_filter.common.models import Book

if TYPE_CHECKING:
    from examples.filter.example import BookFilter


@final
class BookManualFilter(ManualFilter[Select[Book], "BookFilter"]):
    def apply(
        self,
        stmt: Select[Book],
        *,
        value: bool,
        filter_: "BookFilter",  # noqa: ARG002
    ) -> Select[Book]:
        if not value:
            return stmt

        return stmt.where(Book.created_at != datetime.min)  # noqa: DTZ901
