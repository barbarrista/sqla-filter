# SQLAlchemy Filter

## Package for convenient filtering functionality in SQLAlchemy

Quite often, optional filtering functionality is required. To facilitate the implementation of filtering functionality, this package was written

### Filter example

```python
# db/models.py
class Review(Base):
    __tablename__ = "review"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str]
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))


class Author(Base):
    __tablename__ = "author"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class BookAuthor(Base):
    __tablename__ = "book__author"

    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.id"), primary_key=True)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("author.id"),
        primary_key=True,
    )


class Book(Base):
    __tablename__ = "book"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    authors: Mapped[list[Author]] = relationship(secondary=BookAuthor.__table__)
    reviews: Mapped[list[Review]] = relationship()
    created_at: Mapped[datetime]
```

This is how it was before:

```python
# core/domain/book/dto.py
@dataclass(frozen=True, slots=True)
class BookFilter:
    ident: UUID | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None

    author_ids: Sequence[UUID] | None = None
    review_ids: Sequence[UUID] | None = None

    review_content_contains: str | None = None


# core/domain/book/repository.py
class BookRepository:
    ...

    async def get_list(self, filter_: BookFilter) -> Sequence[Book]:
        stmt = select(Book)

        if filter_.ident is not None:
            stmt = stmt.where(Book.id == filter_.ident)
        if filter_.created_at_from is not None:
            stmt = stmt.where(Book.created_at >= filter_.created_at_from)
        if filter_.created_at_to is not None:
            stmt = stmt.where(Book.created_at <= filter_.created_at_to)
        if filter_.author_ids is not None:
            stmt = stmt.join(Book.authors).where(Author.id.in_(filter_.author_ids))
        if filter_.review_ids is not None:
            stmt = stmt.join(Book.reviews).where(Review.id.in_(filter_.review_ids))

        return (await self._session.scalars(stmt)).all()

```

And here's how after using the package:

```python
# core/domain/book/dto.py
from sqlalchemy.sql.operators import eq, ge, icontains_op, in_op, le
from sqla_filter import (
    BaseFilter,
    Unset,
    UNSET,
    FilterField,
    RelationshipInfo,
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


# core/domain/book/repository.py
class BookRepository:
    ...

    async def get_list(self, filter_: BookFilter) -> Sequence[Book]:
        stmt = select(Book)
        stmt = filter_.apply(stmt)
        return (await self._session.scalars(stmt)).all()

```

### Or filter example

```python
from sqla_filter import (
    UNSET,
    FilterField,
    SupportsOrFilter,
    Unset,
)

class BookOrFilter(SupportsOrFilter):
    ident: Annotated[UUID | Unset, FilterField(Book.id, operator=eq)] = UNSET


def main() -> None:
    stmt = select(Book)

    filter_ = BookOrFilter(
        ident=UUID("11111111-1111-1111-1111-111111111111"),
        or_=BookOrFilter(ident=UUID("00000000-0000-0000-0000-000000000001")),
    )

    stmt = filter_.apply(stmt)
```

### Manual filter example

```python
# manual_filter.py
from typing import TYPE_CHECKING, final

from sqlalchemy import Select, exists, not_, select

from examples.models import Contract, ContractJob, Job
from sqla_filter.filter_ import ManualFilter
from sqla_filter.unset import define

if TYPE_CHECKING:
    from manual_filter_example import ContractFilter


@final
class HasUrgentJobFilter(ManualFilter[tuple[Contract], "ContractFilter"]):
    def apply(
        self,
        stmt: Select[tuple[Contract]],
        *,
        value: bool,
        filter_: "ContractFilter",
    ) -> Select[tuple[Contract]]:
        urgent_specs_exists = exists(
            select(1)
            .select_from(ContractJob)
            .join(
                Job,
                ContractJob.job_id == Job.id,
            )
            .where(
                ContractJob.contract_id == define(filter_.ident),
                Job.is_urgent.is_(other=True),
            ),
        )

        condition = urgent_specs_exists if define(value) else not_(urgent_specs_exists)
        return stmt.where(condition)


# manual_filter_example.py
import uuid
from operator import eq
from typing import Annotated
from uuid import UUID

from sqlalchemy import select

from examples.models import Contract
from examples.utils import print_stmt
from sqla_filter.base import BaseFilter
from sqla_filter.filter_ import FilterField
from sqla_filter.unset import UNSET, Unset

from .manual_filter import HasUrgentJobFilter


class ContractFilter(BaseFilter):
    ident: Annotated[UUID | Unset, FilterField(Contract.id, operator=eq)] = UNSET
    has_urgent_job: Annotated[bool | Unset, HasUrgentJobFilter()] = UNSET


def main() -> None:
    stmt = select(Contract)
    filter_ = ContractFilter(
        ident=uuid.uuid4(),
        has_urgent_job=True,
    )
    stmt = filter_.apply(stmt)
```

### Ordering example

```python
from typing import Annotated, Any

from sqlalchemy import Select, select

from examples.models import Author, Book, User
from sqla_filter import (
    UNSET,
    BaseSorter,
    OrderingEnum,
    OrderingField,
    RelationshipInfo,
    Unset,
)
from sqla_filter.ordering import build_priorities


class BookSorter(BaseSorter):
    created_at: Annotated[OrderingEnum | Unset, OrderingField(Book.created_at)] = UNSET
    author_user_first_name: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.first_name,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET
    author_user_last_name: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.last_name,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET
    author_user_last_name_nulls_last: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.last_name,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
        nulls="last",
    ] = UNSET
    author_user_is_deleted: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.is_deleted,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET


def main() -> None:
    stmt = select(Book)
    print_stmt(stmt)

    sorter = BookSorter(
        author_user_last_name=OrderingEnum.desc,
        created_at=OrderingEnum.desc,
        author_user_is_deleted=OrderingEnum.desc,
    )

    stmt = sorter.apply(
        stmt,
        fields_priority=build_priorities(
            BookSorter.author_user_is_deleted,
            BookSorter.author_user_last_name,
        ),
    )
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

```

Important note: Only pass fields of a class that extends the BaseSorter class to `build_priorities`.

If the field is set to "NOT_SET", the filter will not be applied.

[All examples are available at the following link](https://gitlab.com/n.one.k/opensource/sqla-filter/-/blob/main/examples)
