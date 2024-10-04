import dataclasses
import enum
from collections.abc import Sequence
from typing import Any, Protocol, TypeAlias

from sqlalchemy import ColumnElement, ColumnExpressionArgument
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.operators import OperatorType
from sqlalchemy.sql.roles import OnClauseRole

_OnClauseArgument: TypeAlias = ColumnExpressionArgument[Any] | OnClauseRole


class OperatorProtocol(Protocol):  # pragma: no cover
    def __call__(
        self,
        field: InstrumentedAttribute[Any],
        value: Any,  # noqa: ANN401
    ) -> ColumnElement[bool]: ...


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
    operator: OperatorType | OperatorProtocol
    relationship: RelationshipInfo | None = None
    """For filter by relationship field"""

    relationships: Sequence[RelationshipInfo] | None = None
    """For filter by nested relationship field"""
