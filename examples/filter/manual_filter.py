from typing import TYPE_CHECKING, final

from sqlalchemy import Select, exists, not_, select

from examples.models import Contract, ContractJob, Job
from sqla_filter.filter_ import ManualFilter
from sqla_filter.unset import define

if TYPE_CHECKING:
    from manual_filter_example import ContractFilter


@final
class HasUrgentJobFilter(ManualFilter[Contract, "ContractFilter"]):
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
