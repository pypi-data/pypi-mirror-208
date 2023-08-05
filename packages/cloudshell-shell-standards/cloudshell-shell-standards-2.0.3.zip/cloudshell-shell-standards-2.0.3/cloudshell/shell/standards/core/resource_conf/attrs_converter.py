from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from importlib import import_module
from itertools import chain
from typing import Any, Collection, TypeVar

from attr import AttrsInstance
from attrs import Attribute, define, fields_dict

from cloudshell.shell.standards.core.resource_conf.attrs_converters import (
    AbsCollectionConverter,
    AbsConverter,
    BoolConverter,
    IntConverter,
    ListConverter,
    SetConverter,
    StrConverter,
    TupleConverter,
)
from cloudshell.shell.standards.core.resource_conf.resource_attr import (
    AttrMeta,
    WithoutMeta,
    get_str_type,
)
from cloudshell.shell.standards.exceptions import ResourceConfigException

MODEL = TypeVar("MODEL", bound=AttrsInstance)


@define
class InitializeClassError(ResourceConfigException):
    name: str
    type_: type
    val: str

    def __str__(self) -> str:
        msg = f"'{self.name}' receive not valid value '{self.val}'"
        if issubclass(self.type_, Enum):
            values = ", ".join([f"'{v.value}'" for v in self.type_])
            msg += f". Possible values are: {values}"
        return msg


class AbsModelAttrsConverter(ABC):
    def __init__(self, model_cls: type[MODEL], attrs: dict[str, Any]):
        self.model_cls = model_cls
        self.attrs = attrs

    @abstractmethod
    def convert(self) -> dict[str, Any]:
        ...


@define
class ModelAttrsConverter(AbsModelAttrsConverter):
    model_cls: type[MODEL]
    attrs: dict[str, Any]
    _collection_converters: Collection[type[AbsCollectionConverter]] = (
        ListConverter,
        TupleConverter,
        SetConverter,
    )
    _converters: Collection[type[AbsConverter]] = (
        StrConverter,
        BoolConverter,
        IntConverter,
    )

    def convert(self) -> dict[str, Any]:
        converted_attrs = {}
        fields_map = fields_dict(self.model_cls)
        for k, v in self.attrs.items():
            f = fields_map[k]
            converted_attrs[k] = self._convert_attr(v, f)
        return converted_attrs

    def _convert_attr(self, val: Any, f: Attribute) -> Any:
        str_type = get_str_type(f)
        if f.converter is None and str_type != type(val).__name__:
            name = self._get_attr_name(f)
            val = self._convert_by_type(val, str_type, name)
        return val

    @staticmethod
    def _get_attr_name(f: Attribute) -> str:
        try:
            meta = AttrMeta.from_field(f)
        except WithoutMeta:
            name = f.name
        else:
            name = meta.name
        return name

    def _convert_by_type(self, val: str, str_type: str, name: str) -> Any:
        for converter_cls in chain(self._collection_converters, self._converters):
            if converter_cls.is_supported_type(str_type):
                if issubclass(converter_cls, AbsCollectionConverter):
                    new = self._convert_collection(converter_cls, val, str_type, name)
                else:
                    new = self._convert_single(converter_cls, val, str_type, name)
                break
        else:
            new = self._initialize_class(val, str_type, name)
        return new

    def _convert_collection(
        self,
        converter_cls: type[AbsCollectionConverter],
        val: str,
        str_type: str,
        name: str,
    ) -> Any:
        converter = converter_cls(val, name)
        collection_type = converter.type_
        child_str_type = converter.get_str_child_type(str_type)
        child_values = converter.child_values

        converted_val = collection_type(
            self._convert_by_type(child_val, child_str_type, name)
            for child_val in child_values
        )
        return converted_val

    @staticmethod
    def _convert_single(
        converter_cls: type[AbsConverter], val: str, str_type: str, name: str
    ) -> Any:
        converter = converter_cls(val, name)
        return converter.convert()

    def _initialize_class(self, val: str, str_type: str, name: str):
        type_ = self._import_type(str_type)
        try:
            converted_val = type_(val)
        except Exception:
            raise InitializeClassError(name, type_, val)
        return converted_val

    def _import_type(self, type_name: str) -> type:
        for cls in self.model_cls.mro():
            module = import_module(cls.__module__)
            type_ = getattr(module, type_name, None)
            if type_ is not None:
                return type_
        raise TypeError(f"Can't find type {type_name}")
