# Manual Filter

Sometimes you need some filtering. For this there is `sqla_filter.filter_.ManualFilter`.

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

```

```python
# manual_filter_example.py

import uuid
from operator import eq
from typing import Annotated
from uuid import UUID

from sqlalchemy import select

from sqla_filter.base import BaseFilter
from sqla_filter.filter_ import FilterField
from sqla_filter.unset import UNSET, Unset

from .manual_filter import HasUrgentJobFilter


class ContractFilter(BaseFilter):
    ident: Annotated[UUID | Unset, FilterField(Contract.id, operator=eq)] = UNSET
    has_urgent_job: Annotated[bool | Unset, HasUrgentJobFilter()] = UNSET
```

You may not want the filter to be automatically applied. To do this, you must not apply `Annotated`

```python
class SomeFilter(BaseFilter):
    ident: Annotated[UUID | Unset, FilterField(SomeModel.id, operator=eq)] = UNSET
    other_id: UUID | None = None


class Repository:
    ...

    async def get(self, filter_: SomeFilter) -> SomeModel | None:
        stmt = select(SomeModel)
        stmt = filter_.apply(stmt)

        if (other_id := filter_.other_id) is not None:
            stmt = stmt.where(SomeModel.other_id == other_id)
        ...
```
