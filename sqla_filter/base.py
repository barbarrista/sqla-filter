import dataclasses
from collections.abc import Iterable, Mapping
from typing import (
    Any,
    ClassVar,
    Literal,
    TypeVar,
    dataclass_transform,
    get_args,
    get_type_hints,
)

from sqlalchemy import Select, UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.functions import coalesce

from .filter_ import FilterField, RelationshipInfo
from .ordering import OrderingEnum, OrderingField
from .unset import Unset

_SelectClause = TypeVar("_SelectClause", bound=tuple[Any, ...])


@dataclass_transform(kw_only_default=True)
class BaseFilter:
    __sqla_filter_fields__: ClassVar[Mapping[str, FilterField]]

    def __init_subclass__(cls) -> None:
        _init_subclass(cls)

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


@dataclass_transform(kw_only_default=True)
class BaseSorter:
    __sqla_filter_fields__: ClassVar[Mapping[str, OrderingField]]

    def __init_subclass__(cls) -> None:
        _init_subclass(cls)

    def apply(
        self,
        stmt: Select[_SelectClause],
        fields_priority: Iterable[OrderingField] | None = None,
    ) -> Select[_SelectClause]:
        all_fields = self.__sqla_filter_fields__
        if fields_priority:
            sorted_fields = {
                field.name: all_fields[field.name]
                for field in fields_priority
                if field.name in all_fields
            }
            remaining_fields = {
                field.name: all_fields[field.name]
                for field in all_fields.values()
                if field not in fields_priority
            }
            sorted_fields.update(remaining_fields)
            all_fields = sorted_fields

        for field_name, sorter in all_fields.items():
            value = getattr(self, field_name)

            if value is Unset.v:
                continue

            if sorter.relationship:
                stmt = _apply_join(stmt, relationship=sorter.relationship)

            for relationship in sorter.relationships or ():
                stmt = _apply_join(stmt, relationship=relationship)

            expr = _get_ordering_method(
                sorter.field,
                ordering=value,
                nulls=sorter.nulls,
            )
            stmt = stmt.order_by(expr)

        return stmt


def _init_subclass(cls: type[Any]) -> None:
    wrapped_cls = dataclasses.dataclass(cls)
    class_type_hints = get_type_hints(wrapped_cls, include_extras=True)
    del class_type_hints["__sqla_filter_fields__"]

    filter_fields = {}

    for field_name, raw_type in class_type_hints.items():
        args = get_args(raw_type)
        if not args:  # pragma: no cover
            continue

        sqla_filter_field = _get_sqla_filter_field(args)
        if sqla_filter_field is None:
            continue

        sqla_filter_field.name = field_name
        filter_fields[field_name] = sqla_filter_field
        setattr(wrapped_cls, field_name, sqla_filter_field)

    wrapped_cls.__sqla_filter_fields__ = filter_fields


def _get_sqla_filter_field(
    annotations: tuple[Any, ...],
) -> FilterField | OrderingField | None:
    main, *other = annotations

    for annotation in other:
        if isinstance(annotation, FilterField):
            return annotation

        if isinstance(annotation, OrderingField):
            if set(get_args(main)) != {OrderingEnum, Unset}:
                msg = "Annotate ordering field as Annotated[OrderingEnum | Unset]"
                raise TypeError(msg)

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


def _get_ordering_method(
    model_field: InstrumentedAttribute[Any] | coalesce[Any],
    *,
    ordering: OrderingEnum,
    nulls: Literal["first", "last"] | None = None,
) -> UnaryExpression[Any]:
    expr = model_field.asc() if ordering is OrderingEnum.asc else model_field.desc()

    match nulls:
        case "first":
            expr = expr.nulls_first()
        case "last":
            expr = expr.nulls_last()
        case _:
            pass

    return expr
