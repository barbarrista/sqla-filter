from typing import Any, TypeVar

from sqlalchemy import Select

SelectClause = TypeVar("SelectClause", bound=Select[Any])
