import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from tests.sqla_filter.common.filter import BookFilter, DateTimeInterval
from tests.sqla_filter.common.models import Author, Book, Review, User
from tests.utils import compile_stmt


def test_build_simple_stmt() -> None:
    ident = uuid.uuid4()

    stmt = select(Book)
    filter_ = BookFilter(ident=ident)
    stmt = filter_.apply(stmt)

    expected_stmt = select(Book).where(Book.id == ident)

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_build_stmt_with_lambda() -> None:
    now = datetime.now(tz=UTC)
    tomorrow = now + timedelta(days=1)

    stmt = select(Book)
    filter_ = BookFilter(created_at_between=DateTimeInterval(from_=now, to=tomorrow))
    stmt = filter_.apply(stmt)

    expected_stmt = select(Book).where(Book.created_at.between(now, tomorrow))

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_build_stmt_with_join() -> None:
    ident = uuid.uuid4()
    author_ids = [uuid.uuid4() for _ in range(3)]
    review_ids = [uuid.uuid4() for _ in range(3)]

    stmt = select(Book)
    filter_ = BookFilter(ident=ident, author_ids=author_ids, review_ids=review_ids)
    stmt = filter_.apply(stmt)

    expected_stmt = (
        select(Book)
        .where(
            Book.id == ident,
            Author.id.in_(author_ids),
            Review.id.in_(review_ids),
        )
        .join(Book.authors)
        .join(Book.reviews)
    )

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string


def test_build_stmt_with_multiple_join() -> None:
    user_id = uuid.uuid4()

    stmt = select(Book)
    filter_ = BookFilter(author_user_id=user_id)
    stmt = filter_.apply(stmt)

    expected_stmt = (
        select(Book).where(User.id == user_id).join(Book.authors).join(Author.user)
    )

    compiled_stmt = compile_stmt(stmt)
    compiled_expected_stmt = compile_stmt(expected_stmt)

    assert compiled_stmt.string == compiled_expected_stmt.string
