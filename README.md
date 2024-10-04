# SQLAlchemy Filter

## Package for convenient filtering functionality in SQLAlchemy

Quite often, optional filtering functionality is required. To facilitate the implementation of filtering functionality, this package was written

Example:

```py
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

```py
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

```py
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

If the field is set to "NOT_SET", the filter will not be applied.

[The entire example is available at this link](https://gitlab.com/n.one.k/opensource/sqlalchemy-filter/-/blob/main/examples/first/example.py)
