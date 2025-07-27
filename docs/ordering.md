# Ordering

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
```

## Important note

**Only pass fields of a class that extends the BaseSorter class to `build_priorities`.**
