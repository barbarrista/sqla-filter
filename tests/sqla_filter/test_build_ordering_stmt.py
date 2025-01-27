from typing import Annotated, assert_never

import pytest
from sqlalchemy import select

from sqla_filter.base import BaseSorter
from sqla_filter.ordering import OrderingEnum, OrderingField, build_priorities
from sqla_filter.unset import UNSET, Unset
from tests.sqla_filter.common.models import Author, Book, User
from tests.sqla_filter.common.ordering import BookSorter
from tests.utils import compile_stmt


@pytest.mark.parametrize("nulls", ["first", "last", None])
def test_build_simple_stmt(nulls: str | None) -> None:
    field = Book.created_at
    stmt = select(Book)

    expected_stmt = select(Book)
    match nulls:
        case "first":
            sorter = BookSorter(created_at_nulls_first=OrderingEnum.desc)
            expected_stmt = expected_stmt.order_by(field.desc().nulls_first())
        case "last":
            sorter = BookSorter(created_at_nulls_last=OrderingEnum.desc)
            expected_stmt = expected_stmt.order_by(field.desc().nulls_last())
        case None:
            sorter = BookSorter(created_at=OrderingEnum.desc)
            expected_stmt = expected_stmt.order_by(field.desc())
        case _ as never:
            raise assert_never(never)  # type: ignore[arg-type]

    stmt = sorter.apply(stmt)

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_build_stmt_with_join() -> None:
    stmt = select(Book)
    sorter = BookSorter(
        author_user_first_name=OrderingEnum.desc,
        author_user_is_deleted=OrderingEnum.asc,
    )
    stmt = sorter.apply(
        stmt,
        fields_priority=build_priorities(
            BookSorter.author_user_is_deleted,
            BookSorter.author_user_last_name,
        ),
    )

    expected_stmt = (
        select(Book)
        .join(Book.authors)
        .join(Author.user)
        .order_by(
            User.is_deleted.asc(),
            User.first_name.desc(),
        )
    )

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_build_stmt_with_single_join() -> None:
    stmt = select(Book)
    sorter = BookSorter(author_alias=OrderingEnum.desc)
    stmt = sorter.apply(stmt)

    expected_stmt = select(Book).join(Book.authors).order_by(Author.alias.desc())
    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_sorter_raises() -> None:
    with pytest.raises(TypeError):

        class Sorter(BaseSorter):  # pyright:ignore[reportUnusedClass]
            created_at: Annotated[int | Unset, OrderingField(Book.created_at)] = UNSET
