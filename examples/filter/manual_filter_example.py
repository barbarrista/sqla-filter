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
    print_stmt(stmt)

    filter_ = ContractFilter(
        ident=uuid.uuid4(),
        has_urgent_job=True,
    )

    stmt = filter_.apply(stmt)
    print_stmt(stmt)


if __name__ == "__main__":
    main()
