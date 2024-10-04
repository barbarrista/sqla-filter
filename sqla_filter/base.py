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

from .filter_ import FilterField, RelationshipInfo, Unset

_SelectClause = TypeVar("_SelectClause", bound=tuple[Any, ...])


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

    def apply(self, stmt: Select[_SelectClause]) -> Select[_SelectClause]:
        for field_name, filter_ in self.__sqla_filter_fields__.items():
            value = getattr(self, field_name)

            if value is Unset.v:
                continue

            if filter_.relationship:
                stmt = _apply_join(stmt, relationship=filter_.relationship)

            for relationship in filter_.relationships or ():
                stmt = _apply_join(stmt, relationship=relationship)

            stmt = stmt.where(
                filter_.operator(
                    filter_.field,
                    value,
                ),  # pyright:ignore[reportArgumentType]
            )

        return stmt


def _get_filter_field(
    annotations: tuple[Any, ...],
) -> FilterField | None:
    for annotation in annotations:
        if isinstance(annotation, FilterField):
            return annotation

    return None


def _apply_join(
    stmt: Select[_SelectClause],
    *,
    relationship: RelationshipInfo,
) -> Select[_SelectClause]:
    return stmt.join(
        relationship.field,
        relationship.onclause,
        isouter=relationship.isouter,
        full=relationship.full,
    )
