# Simple Usage

```python
# models.py
class Review(Base):
    __tablename__ = "review"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str]
```

Define filter class

```python
# filters.py

from operator import eq
from sqla_filter import (
    BaseFilter,
    Unset,
    UNSET,
    FilterField,
)

from db.models import Review

class ReviewFilter(BaseFilter):
    ident: Annotated[UUID | Unset, FilterField(Review.id, operator=eq)] = UNSET
    content: Annotated[
        str | Unset,
        FilterField(Review.content, operator=eq),
    ] = UNSET
```

Use a filter in the repository (or elsewhere)

```python
# repository.py

class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, filter_: ReviewFilter) -> Review | None:
        stmt = select(ReviewFilter)
        stmt = filter_.apply(stmt)
        return (await self._session.scalars()).one_or_none()
```

Use repository method

```python
# command.py

class UpdateReviewCommand:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    async def execute(self, ident: UUID, content: str) -> Review:
        review = await self._repository.get(
            filter_=ReviewFilter(ident=ident)
        )
        ...
```
