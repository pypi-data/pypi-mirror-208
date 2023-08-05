from __future__ import annotations

import functools
import re
from collections.abc import Iterator

from attrs import define

from cloudshell.shell.standards.exceptions import BaseStandardException

COLLECTION_SEPARATOR_PATTERN = re.compile(r"[,;]")

CS_MAX_NAME_LENGTH = 100
SPECIAL_SYMBOLS = re.escape(".-|_[]")
CS_ALLOWED_STR_PATTERN = re.compile(rf"^[a-zA-Z\d\s{SPECIAL_SYMBOLS}]+$")


@define
class InvalidStrValue(BaseStandardException):
    value: str


class TooLongStrValue(InvalidStrValue):
    def __str__(self):
        return f"Value '{self.value}' is too long. Max length is {CS_MAX_NAME_LENGTH}"


class NotSupportedSymbols(InvalidStrValue):
    def __str__(self):
        return (
            f"Value '{self.value}' contains invalid symbols."
            f" Allowed symbols are: ASCII letters, digits, spaces, and .-|_[]"
        )


def attr_length_validator(max_length: int):
    def decorator_func(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            nargs = []
            for arg in args:
                if isinstance(arg, str):
                    nargs.append(arg[:max_length])
                else:
                    nargs.append(arg)

            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = value[:max_length]

            return func(*nargs, **kwargs)

        return inner

    return decorator_func


def split_list_of_values(string: str) -> Iterator[str, None, None]:
    return filter(bool, map(str.strip, COLLECTION_SEPARATOR_PATTERN.split(string)))


def validate_str_for_cs(value: str) -> None:
    if len(value) > CS_MAX_NAME_LENGTH:
        raise TooLongStrValue(value)
    if CS_ALLOWED_STR_PATTERN.match(value) is None:
        raise NotSupportedSymbols(value)
