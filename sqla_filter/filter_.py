import dataclasses
import enum
from typing import Any, Protocol, TypeAlias, TypeVar

from sqlalchemy import ColumnExpressionArgument, Select
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute
from sqlalchemy.sql.operators import OperatorType
from sqlalchemy.sql.roles import OnClauseRole

_OnClauseArgument: TypeAlias = ColumnExpressionArgument[Any] | OnClauseRole


class Unset(enum.Enum):
    v = enum.auto()


UNSET = Unset.v

_T = TypeVar("_T", bound=DeclarativeBase)


class OnApplyHandler(Protocol):
    def __call__(self, stmt: Select[tuple[_T]], *, value: Any) -> Select[tuple[_T]]: ...


@dataclasses.dataclass(frozen=True, slots=True)
class RelationshipInfo:
    field: InstrumentedAttribute[Any]
    _: dataclasses.KW_ONLY
    onclause: _OnClauseArgument | None = None
    isouter: bool = False
    full: bool = False


@dataclasses.dataclass(frozen=True, slots=True)
class FilterField:
    field: InstrumentedAttribute[Any]
    _: dataclasses.KW_ONLY
    operator: OperatorType
    relationship: RelationshipInfo | None = None
    on_apply: OnApplyHandler | None = None
