import pytest

from sqla_filter.unset import UNSET, Unset, or_unset


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (888, 888),
        ("888", "888"),
        (None, UNSET),
    ],
)
def test_or_unset(value: int | str | None, expected: int | str | Unset) -> None:
    assert or_unset(value) == expected
