from __future__ import annotations

from collections import defaultdict
from typing import Any

from cloudshell.shell.standards.core.utils import attr_length_validator


class AttributeContainer:
    """Contains Attributes."""

    def __init__(self):
        self.attributes: dict[AttributeName, Any] = {}


class AttributeName:
    def __init__(
        self, attribute_model: AttributeModel, attribute_container: AttributeContainer
    ):
        self._attribute_model = attribute_model
        self._attribute_container = attribute_container

    def to_string(self) -> str:
        return self._attribute_model.attribute_name(self._attribute_container)

    def __str__(self) -> str:
        return self.to_string()

    def __hash__(self):
        return hash(self._attribute_model)

    def __eq__(self, other: AttributeName) -> bool:
        return self._attribute_model == other._attribute_model


class AttributeModel:
    """Attribute descriptor."""

    MAX_LENGTH = 2000

    def __init__(self, name: str, default_value: Any = None):
        self.name = name
        self.default_value = default_value

    def attribute_name(self, instance):
        return self.name

    def __get__(self, instance: AttributeContainer, owner) -> Any:
        if instance is None:
            return self

        return instance.attributes.get(
            AttributeName(self, instance), self.default_value
        )

    @attr_length_validator(MAX_LENGTH)
    def __set__(self, instance: AttributeContainer, value: Any) -> None:
        value = value or self.default_value
        instance.attributes[AttributeName(self, instance)] = value

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: AttributeModel) -> bool:
        return self.name == other.name


class InstanceAttribute:
    """Validates instance attribute."""

    def __init__(self):
        self.value_container = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return self.value_container.get(instance, None)

    @attr_length_validator(AttributeModel.MAX_LENGTH)
    def __set__(self, instance, value):
        self.value_container[instance] = value


class RelativeAddress:
    ADDRESS_SEPARATOR = "/"

    class IndexValidator:
        """Validate registered indexes."""

        def __init__(self):
            self._address_dict = defaultdict(lambda: defaultdict(list))

        @staticmethod
        def _generate_index(index: str, position: int) -> str:
            """Generate index if needed."""
            return f"{index}-{position}"

        def get_valid(self, node: RelativeAddress) -> str:
            instance_list = self._address_dict.get(node._prefix, {}).get(
                node.native_index, []
            )
            if node in instance_list and len(instance_list) > 1:
                return self._generate_index(
                    node.native_index, instance_list.index(node)
                )
            else:
                return node.native_index

        def register(self, node: RelativeAddress) -> None:
            self._address_dict[node._prefix][node.native_index].append(node)

    def __init__(
        self,
        index: str | None,
        prefix: str = "",
        parent_node: RelativeAddress | None = None,
    ):
        self.__parent_node = None
        self.__index_validator = RelativeAddress.IndexValidator()

        self.native_index = index
        self._prefix = prefix
        self.parent_node = parent_node

    @property
    def index(self) -> str | None:
        """Validated index."""
        if self.parent_node and self.parent_node.__index_validator:
            return self.parent_node.__index_validator.get_valid(self)
        else:
            return self.native_index

    @index.setter
    def index(self, value: str) -> None:
        self.native_index = value

    @property
    def _full_address(self) -> str:
        if self.parent_node and self.parent_node._full_address:
            return (
                f"{self.parent_node._full_address}"
                f"{self.ADDRESS_SEPARATOR}"
                f"{self._local_address}"
            )
        elif self.index:
            return self._local_address
        else:
            return ""

    @property
    def parent_node(self) -> RelativeAddress | None:
        return self.__parent_node

    @parent_node.setter
    def parent_node(self, node: RelativeAddress | None) -> None:
        if node:
            self.__parent_node = node
            node.__index_validator.register(self)

    @property
    def _local_address(self) -> str:
        """Generates local relative address."""
        local_address = f"{self._prefix or ''}{self.index or ''}"
        return local_address

    def to_string(self) -> str:
        return self._full_address

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return self.__str__()
