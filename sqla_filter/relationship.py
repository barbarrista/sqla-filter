import dataclasses
from typing import Any, TypeAlias

from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.roles import OnClauseRole

_OnClauseArgument: TypeAlias = ColumnExpressionArgument[Any] | OnClauseRole


@dataclasses.dataclass(frozen=True, slots=True)
class RelationshipInfo:
    field: InstrumentedAttribute[Any]
    _: dataclasses.KW_ONLY
    onclause: _OnClauseArgument | None = None
    isouter: bool = False
    full: bool = False
