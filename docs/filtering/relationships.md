# Relationships

## Models example

```python
class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class Author(Base):
    __tablename__ = "author"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    last_name: Mapped[str]
    first_name: Mapped[str]
    user: Mapped[User] = relationship()


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
    created_at: Mapped[datetime]
```

## Relationship

Don't worry if you specify more than one of the same relationship field. If you use join via relationship, the join will only happen once.

```python
class BookFilter(BaseFilter):
    author_last_name_contains: Annotated[
        list[UUID] | Unset,
        FilterField(
            Author.last_name,
            operator=icontains_op,
            relationship=RelationshipInfo(field=Book.authors),
        ),
    ] = UNSET
    author_first_name_contains: Annotated[
        list[UUID] | Unset,
        FilterField(
            Author.first_name,
            operator=icontains_op,
            relationship=RelationshipInfo(field=Book.authors),
        ),
    ] = UNSET

```

## Nested relationships

If you have a deeper join, you can use the `relationships` parameter

```python
class BookFilter(BaseFilter):
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
```
