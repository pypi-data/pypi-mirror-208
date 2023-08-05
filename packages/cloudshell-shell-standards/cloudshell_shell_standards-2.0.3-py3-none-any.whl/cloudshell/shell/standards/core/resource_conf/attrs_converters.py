from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import ClassVar

from attrs import define

from cloudshell.shell.standards.core.utils import split_list_of_values
from cloudshell.shell.standards.exceptions import ResourceConfigException


@define
class AttributeConvertError(ResourceConfigException):
    name: str
    str_type: str
    val: str

    def __str__(self) -> str:
        return (
            f"The resource attribute '{self.name}' should be of type "
            f"{self.str_type} but the value '{self.val}' was provided"
        )


class AbsConverter(ABC):
    type_: ClassVar[type]

    def __init__(self, val: str, name: str):
        self.val = val
        self.name = name

    @classmethod
    def get_str_type(cls) -> str:
        return cls.type_.__name__

    @classmethod
    def is_supported_type(cls, str_type: str) -> bool:
        return str_type.lower() == cls.get_str_type()

    @abstractmethod
    def _convert(self) -> type_:
        ...

    def convert(self) -> type_:
        try:
            return self._convert()
        except Exception as e:
            raise AttributeConvertError(self.name, self.get_str_type(), self.val) from e


class AbsCollectionConverter(AbsConverter):
    @classmethod
    def is_supported_type(cls, str_type: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_str_child_type(self, str_type: str) -> str:
        ...

    @property
    @abstractmethod
    def child_values(self) -> Iterator[str]:
        ...


class StrConverter(AbsConverter):
    type_: ClassVar[type] = str

    def _convert(self) -> type_:
        return self.val


class BoolConverter(AbsConverter):
    type_: ClassVar[type] = bool

    def _convert(self) -> bool:
        val = self.val.lower()
        if val in {"true", "yes", "y"}:
            result = True
        elif val in {"false", "no", "n"}:
            result = False
        else:
            raise ValueError
        return result


class IntConverter(AbsConverter):
    type_: ClassVar[type] = int

    def _convert(self) -> int:
        return int(self.val)


class CollectionConverter(AbsCollectionConverter):
    type_: ClassVar[type]

    @classmethod
    def get_collection_pattern(cls):
        return re.compile(rf"^{cls.get_str_type()}\[(\w+)]$", re.I)

    def get_str_child_type(self, str_type: str) -> str:
        pattern = self.get_collection_pattern()
        return pattern.search(str_type).group(1)

    @property
    def child_values(self) -> list[str]:
        return list(split_list_of_values(self.val))

    @classmethod
    def is_supported_type(cls, str_type: str) -> bool:
        pattern = cls.get_collection_pattern()
        return bool(pattern.search(str_type))

    def _convert(self) -> type_:
        return self.type_(self.child_values)


class ListConverter(CollectionConverter):
    type_ = list


class TupleConverter(CollectionConverter):
    type_ = tuple


class SetConverter(CollectionConverter):
    type_ = set
