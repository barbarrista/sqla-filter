from datetime import datetime
from typing import TYPE_CHECKING, final

from sqlalchemy import Select

from sqla_filter.filter_ import ManualFilter
from tests.sqla_filter.common.models import Book

if TYPE_CHECKING:
    from examples.filter.example import BookFilter


@final
class BookManualFilter(ManualFilter[tuple[Book], "BookFilter"]):
    def apply(
        self,
        stmt: Select[tuple[Book]],
        *,
        value: bool,
        filter_: "BookFilter",  # noqa: ARG002
    ) -> Select[tuple[Book]]:
        if not value:
            return stmt

        return stmt.where(Book.created_at != datetime.min)
