# Or Filter

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