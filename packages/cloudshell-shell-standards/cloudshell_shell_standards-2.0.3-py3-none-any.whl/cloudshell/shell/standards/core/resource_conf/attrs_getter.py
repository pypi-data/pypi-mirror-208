from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar, Union

from attrs import Attribute, AttrsInstance, fields

from cloudshell.shell.core.driver_context import (
    AutoLoadCommandContext,
    InitCommandContext,
    ResourceCommandContext,
    ResourceRemoteCommandContext,
    UnreservedResourceCommandContext,
)

from cloudshell.shell.standards.core.namespace_type import NameSpaceType
from cloudshell.shell.standards.core.resource_conf.resource_attr import (
    RAISE,
    AttrMeta,
    WithoutMeta,
    get_str_type,
)

RESOURCE_CONTEXT_TYPES = Union[
    ResourceCommandContext,
    InitCommandContext,
    AutoLoadCommandContext,
    UnreservedResourceCommandContext,
    ResourceRemoteCommandContext,
]


MODEL = TypeVar("MODEL", bound=AttrsInstance)


class AbsAttrsGetter(ABC):
    """Extract attributes from CS object and return them as kwargs for the config."""

    def __init__(self, model_cls: type[MODEL], decrypt_password: Callable[[str], str]):
        self.model_cls = model_cls
        self._decrypt_password = decrypt_password

    def get_attrs(self) -> dict[str, Any]:
        kwargs = {}
        for f in fields(self.model_cls):
            try:
                meta = AttrMeta.from_field(f)
            except WithoutMeta:
                continue
            else:
                kwargs[f.name] = self._get_val(f, meta)
        return kwargs

    @abstractmethod
    def _extract_attr_val(self, f: Attribute, meta: AttrMeta) -> str:
        raise NotImplementedError

    def _get_val(self, f: Attribute, meta: AttrMeta) -> Any:
        try:
            val = self._extract_attr_val(f, meta)
        except KeyError:
            val = self._get_default(f, meta, attr_present=False)
        else:
            if val == "":
                val = self._get_default(f, meta, attr_present=True)
            else:
                if meta.is_password:
                    val = self._decrypt_password(val)
        return val

    @staticmethod
    def _get_default(f: Attribute, meta: AttrMeta, attr_present: bool) -> Any:
        str_type = get_str_type(f)
        error = ValueError(f"Resource attribute {meta.name} is missing")
        default = f.default

        if default is RAISE:
            if not attr_present:
                raise error
            elif str_type != "str":
                # empty string is not valid value for non-str types
                raise error
            else:
                # empty string is valid value for str types
                default = ""

        return default


class ResourceContextAttrsGetter(AbsAttrsGetter):
    def __init__(
        self,
        model_cls: type[MODEL],
        decrypt_password: Callable[[str], str],
        context: RESOURCE_CONTEXT_TYPES,
    ):
        super().__init__(model_cls, decrypt_password)
        self.context = context
        self.shell_name = self.context.resource.model
        self.family_name = self.context.resource.family

    def _extract_attr_val(self, f: Attribute, meta: AttrMeta) -> str:
        key = self._get_key(meta)
        return self.context.resource.attributes[key]

    def _get_key(self, meta: AttrMeta) -> str:
        namespace = self._get_namespace(meta.namespace_type)
        return f"{namespace}.{meta.name}"

    def _get_namespace(self, namespace_type: NameSpaceType) -> str:
        if namespace_type is NameSpaceType.SHELL_NAME:
            namespace = self.shell_name
        elif namespace_type is NameSpaceType.FAMILY_NAME:
            namespace = self.family_name
        else:
            raise ValueError(f"Unknown namespace: {namespace_type}")
        return namespace
