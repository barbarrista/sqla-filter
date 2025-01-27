import enum
from typing import TypeVar

_T = TypeVar("_T")


class Unset(enum.Enum):
    v = enum.auto()


UNSET = Unset.v


def or_unset(value: _T | None) -> _T | Unset:
    if value is None:
        return UNSET

    return value
