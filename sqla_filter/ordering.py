import dataclasses
import enum
from collections.abc import Iterable, Sequence
from typing import Any, Literal, cast

from sqlalchemy.orm import InstrumentedAttribute

from .relationship import RelationshipInfo


class OrderingEnum(enum.StrEnum):
    asc = enum.auto()
    desc = enum.auto()


@dataclasses.dataclass(slots=True)
class OrderingField:
    _name: str = dataclasses.field(init=False, repr=False, hash=True)

    field: InstrumentedAttribute[Any]
    _: dataclasses.KW_ONLY
    relationship: RelationshipInfo | None = None
    """For ordering by relationship field"""

    relationships: Sequence[RelationshipInfo] | None = None
    """For ordering by nested relationship field"""

    nulls: Literal["first", "last"] | None = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


def build_priorities(*fields: Any) -> Iterable[OrderingField]:  # noqa: ANN401
    """
    Hack for pyright

    Pass only `OrderingField`
    """
    return cast("Iterable[OrderingField]", fields)
