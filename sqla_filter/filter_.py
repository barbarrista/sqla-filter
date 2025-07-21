import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
)

from sqlalchemy import ColumnElement, Select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.operators import OperatorType

from .relationship import RelationshipInfo

if TYPE_CHECKING:
    from .base import BaseFilter

_TFilter = TypeVar("_TFilter", bound="BaseFilter")


class OperatorProtocol(Protocol):  # pragma: no cover
    def __call__(
        self,
        field: InstrumentedAttribute[Any],
        value: Any,  # noqa: ANN401
    ) -> ColumnElement[bool]: ...


class ManualFilter(ABC, Generic[_TFilter]):
    _name: str

    @abstractmethod
    def apply(
        self,
        stmt: Select[tuple[Any, ...]],
        *,
        value: Any,  # noqa: ANN401
        filter_: _TFilter,
    ) -> Select[tuple[Any, ...]]:
        raise NotImplementedError

    @property
    def name(self) -> str:  # pragma: no cover
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


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
