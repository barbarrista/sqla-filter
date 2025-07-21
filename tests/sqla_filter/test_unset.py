import pytest

from sqla_filter.unset import UNSET, Unset, define, or_unset


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


def test_define() -> None:
    expected = 888
    assert define(888) == expected


def test_define_raises() -> None:
    with pytest.raises(TypeError, match='Got "Unset" type'):
        define(Unset.v)
