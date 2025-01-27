from typing import Annotated

from sqla_filter.base import BaseSorter
from sqla_filter.ordering import OrderingEnum, OrderingField
from sqla_filter.relationship import RelationshipInfo
from sqla_filter.unset import UNSET, Unset

from .models import Author, Book, User


class BookSorter(BaseSorter):
    created_at: Annotated[OrderingEnum | Unset, OrderingField(Book.created_at)] = UNSET
    created_at_nulls_last: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            Book.created_at,
            nulls="last",
        ),
    ] = UNSET
    created_at_nulls_first: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            Book.created_at,
            nulls="first",
        ),
    ] = UNSET
    author_user_first_name: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.first_name,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET
    author_alias: Annotated[
        OrderingEnum | Unset,
        OrderingField(Author.alias, relationship=RelationshipInfo(field=Book.authors)),
    ] = UNSET
    author_user_last_name: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.last_name,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET
    author_user_is_deleted: Annotated[
        OrderingEnum | Unset,
        OrderingField(
            User.is_deleted,
            relationships=[
                RelationshipInfo(field=Book.authors),
                RelationshipInfo(field=Author.user),
            ],
        ),
    ] = UNSET
