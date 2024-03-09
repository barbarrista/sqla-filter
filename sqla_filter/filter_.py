import dataclasses
import enum
from typing import Any, TypeAlias

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.operators import OperatorType
from sqlalchemy.sql.roles import OnClauseRole

_OnClauseArgument: TypeAlias = ColumnExpressionArgument[Any] | OnClauseRole


class Unset(enum.Enum):
    v = enum.auto()


UNSET = Unset.v


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
