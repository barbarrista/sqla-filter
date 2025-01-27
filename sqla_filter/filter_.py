import dataclasses
from collections.abc import Sequence
from typing import Any, Protocol

from sqlalchemy import ColumnElement
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.operators import OperatorType

from .relationship import RelationshipInfo


class OperatorProtocol(Protocol):  # pragma: no cover
    def __call__(
        self,
        field: InstrumentedAttribute[Any],
        value: Any,  # noqa: ANN401
    ) -> ColumnElement[bool]: ...


@dataclasses.dataclass(slots=True)
class FilterField:
    _name: str = dataclasses.field(init=False, repr=False, hash=True)

    field: InstrumentedAttribute[Any]
    _: dataclasses.KW_ONLY
    operator: OperatorType | OperatorProtocol
    relationship: RelationshipInfo | None = None
    """For filter by relationship field"""

    relationships: Sequence[RelationshipInfo] | None = None
    """For filter by nested relationship field"""

    @property
    def name(self) -> str:  # pragma: no cover
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
