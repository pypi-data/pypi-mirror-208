from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, TypeVar

from cloudshell.shell.standards.core.autoload.core_entities import (
    AttributeContainer,
    AttributeModel,
    InstanceAttribute,
    RelativeAddress,
)
from cloudshell.shell.standards.core.namespace_type import NameSpaceType
from cloudshell.shell.standards.core.utils import validate_str_for_cs
from cloudshell.shell.standards.exceptions import ResourceModelException

SUB_RESOURCE_TYPE = TypeVar("SUB_RESOURCE_TYPE", bound="ResourceNode")


class ResourceNode(ABC):
    _name = InstanceAttribute()
    _unique_identifier = InstanceAttribute()

    def __init__(
        self,
        index: str | None,
        prefix: str,
        name: str | None = None,
        unique_id: str | None = None,
    ):
        self.relative_address = RelativeAddress(index, prefix)

        self.parent = None
        self._name = name
        self._unique_identifier = unique_id
        self._child_resources: list[SUB_RESOURCE_TYPE] = []

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        else:
            return self._gen_name()

    @property
    def full_name(self) -> str:
        """Returns full resource name with all parents and the root resource name also.

        Example: "Cisco/Chassis 1/Module 1/Port 1"
        """
        if self.parent:
            return f"{self.parent.full_name}/{self.name}"
        return self.name

    @abstractmethod
    def _gen_name(self) -> str:
        """Generates resource name."""
        raise NotImplementedError

    @property
    def unique_identifier(self) -> str:
        if self._unique_identifier:
            return self._unique_identifier
        return self._gen_unique_id()

    def _gen_unique_id(self) -> str:
        return str(hash(f"{self.relative_address}+{self.name}"))

    def _add_sub_resource(self, sub_resource: SUB_RESOURCE_TYPE) -> None:
        sub_resource.relative_address.parent_node = self.relative_address
        sub_resource.parent = self
        self._child_resources.append(sub_resource)

    def extract_sub_resources(self) -> tuple[SUB_RESOURCE_TYPE, ...]:
        return tuple(self._child_resources)


class NamespaceAttributeContainer(AttributeContainer):
    _RESOURCE_MODEL = ""

    def __init__(
        self, shell_name: str, family_name: str, resource_model: str | None = None
    ):
        """Attribute container with defined attr levels used by ResourceAttribute."""
        super().__init__()
        self.family_name = family_name
        self.shell_name = shell_name
        self.resource_model = resource_model or self._RESOURCE_MODEL


class ResourceAttribute(AttributeModel):
    _RESOURCE_MODEL_ATTR = "resource_model"

    def __init__(
        self,
        name: str,
        namespace_attribute: NameSpaceType = NameSpaceType.SHELL_NAME,
        default_value: Any = None,
    ):
        super().__init__(name, default_value)
        self.namespace_attribute = namespace_attribute

    def attribute_name(self, instance: NamespaceAttributeContainer) -> str:
        """Generate attribute name for the specified prefix."""
        namespace = getattr(instance, self.namespace_attribute.value)
        if self.namespace_attribute is NameSpaceType.SHELL_NAME and namespace:
            resource_model = getattr(instance, self._RESOURCE_MODEL_ATTR)
            if resource_model:
                namespace = ".".join((namespace, resource_model))

        return ".".join((namespace, self.name)) if namespace else self.name


class AbstractResource(ResourceNode, NamespaceAttributeContainer):
    _RELATIVE_ADDRESS_PREFIX = ""
    _NAME_TEMPLATE = ""
    _FAMILY_NAME = ""

    def __init__(
        self,
        index: str | None,
        shell_name: str | None = None,
        family_name: str | None = None,
        name: str | None = None,
        unique_id: str | None = None,
    ):
        if name:
            validate_str_for_cs(name)
        ResourceNode.__init__(
            self, index, self._RELATIVE_ADDRESS_PREFIX, name, unique_id
        )
        NamespaceAttributeContainer.__init__(
            self, shell_name, family_name or self._FAMILY_NAME
        )

    def _add_sub_resource(self, sub_resource: AbstractResource) -> None:
        super()._add_sub_resource(sub_resource)

    def extract_sub_resources(self: AbstractResource) -> tuple[AbstractResource, ...]:
        return super().extract_sub_resources()

    def _gen_name(self) -> str:
        """Generate resource name."""
        if self._NAME_TEMPLATE:
            return self._NAME_TEMPLATE.format(self.relative_address.index)
        raise ResourceModelException("NAME_TEMPLATE is empty")

    def _add_sub_resource_with_type_restrictions(
        self, sub_resource: AbstractResource, allowed_types: Iterable[type]
    ) -> None:
        """Register child resource which in the list of allowed types."""
        if isinstance(sub_resource, tuple(allowed_types)):
            self._add_sub_resource(sub_resource)
        else:
            cls_name = type(self).__name__
            sub_resource_cls_name = type(sub_resource).__name__
            raise ResourceModelException(
                f"Class {sub_resource_cls_name} not allowed to connect to {cls_name}"
            )

    @property
    def cloudshell_model_name(self) -> str:
        """Return the name of the CloudShell model."""
        if self.shell_name:
            return f"{self.shell_name}.{self.resource_model.replace(' ', '')}"
        else:
            return self.resource_model
