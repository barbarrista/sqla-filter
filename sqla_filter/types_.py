from typing import Any, Protocol, Self, TypeVar

from sqlalchemy import ColumnElement, Select
from sqlalchemy.sql._typing import _ColumnExpressionArgument


class SupportsWhere(Protocol):
    @property
    def whereclause(self) -> ColumnElement[Any] | None: ...

    def where(self, *whereclause: _ColumnExpressionArgument[bool]) -> Self: ...

    def compile(self, *args: Any, **kwargs: Any) -> Any: ...  # noqa: ANN401


# Select | Update | Delete (and any statement with WHERE)
SelectClause = TypeVar("SelectClause", bound=SupportsWhere)

# Select-only (order_by / join-heavy APIs)
SelectStatement = TypeVar("SelectStatement", bound=Select[Any])
