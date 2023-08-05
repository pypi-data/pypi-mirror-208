from __future__ import annotations

import pytest

from cloudshell.shell.standards.core.utils import (
    InvalidStrValue,
    split_list_of_values,
    validate_str_for_cs,
)


@pytest.mark.parametrize(
    "string_list, expected_result",
    [
        ("a,b,c", ["a", "b", "c"]),
        ("a;b;c", ["a", "b", "c"]),
        ("a;b,c", ["a", "b", "c"]),
        ("a; ,c", ["a", "c"]),
        (" a  ; , c ", ["a", "c"]),
        ("", []),
        (" ", []),
        (";", []),
        (",", []),
    ],
)
def test_split_list_of_values(string_list, expected_result):
    assert list(split_list_of_values(string_list)) == expected_result


@pytest.mark.parametrize(
    "str_value",
    [
        "a" * 100,
        "a",
        "abDF45|.[]-",
    ],
)
def test_validate_str_for_cs_valid(str_value):
    validate_str_for_cs(str_value)


@pytest.mark.parametrize(
    "str_value",
    [
        "a" * 101,
        "",
        "привіт",
        "ch/m1/p1",
        "'module 1'",
        '"module 1"',
    ],
)
def test_validate_str_for_cs_invalid(str_value):
    with pytest.raises(InvalidStrValue) as exc_info:
        validate_str_for_cs(str_value)
    assert f"'{str_value}'" in str(exc_info.value)
