import contextlib
import dataclasses
from collections.abc import Mapping
from typing import (
    Any,
    ClassVar,
    TypeVar,
    dataclass_transform,
    get_args,
    get_type_hints,
)

from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase

from .filter_ import FilterField, RelationshipInfo, Unset

_TModel = TypeVar("_TModel", bound=DeclarativeBase)


@dataclass_transform(kw_only_default=True)
class BaseFilter:
    __sqla_filter_fields__: ClassVar[Mapping[str, FilterField]]

    def __init_subclass__(cls) -> None:
        wrapped_cls = dataclasses.dataclass(cls)
        class_type_hints = get_type_hints(wrapped_cls, include_extras=True)
        del class_type_hints["__sqla_filter_fields__"]

        filter_fields = {}

        for field_name, raw_type in class_type_hints.items():
            args = get_args(raw_type)
            filter_field = _get_filter_field(args)
            if filter_field is None:
                continue

            filter_fields[field_name] = filter_field

        wrapped_cls.__sqla_filter_fields__ = filter_fields

    def apply(self, stmt: Select[tuple[_TModel]]) -> Select[tuple[_TModel]]:
        for field in dataclasses.fields(self):  # type:ignore[arg-type] # mypy moment
            if (value := getattr(self, field.name)) is Unset.v:
                continue

            filter_ = self.__sqla_filter_fields__[field.name]
            if filter_.relationship:
                stmt = _apply_join(stmt, relationship=filter_.relationship)

            stmt = stmt.where(filter_.operator(filter_.field, value))

        return stmt


def _get_filter_field(
    annotations: tuple[Any, ...],
) -> FilterField | None:
    with contextlib.suppress(IndexError):
        if not isinstance((filter_ := annotations[1]), FilterField):
            return None

        return filter_

    return None


def _apply_join(
    stmt: Select[tuple[_TModel]],
    *,
    relationship: RelationshipInfo,
) -> Select[tuple[_TModel]]:
    return stmt.join(
        relationship.field,
        relationship.onclause,
        isouter=relationship.isouter,
        full=relationship.full,
    )
