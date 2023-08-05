from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from typing_extensions import Self

from cloudshell.api.cloudshell_api import CloudShellAPISession

import cloudshell.shell.standards.attribute_names as attribute_names
from cloudshell.shell.standards.core.autoload.existed_resource_info import (
    ExistedResourceInfo,
)
from cloudshell.shell.standards.core.autoload.resource_model import (
    AbstractResource,
    ResourceAttribute,
)
from cloudshell.shell.standards.core.autoload.utils import AutoloadDetailsBuilder
from cloudshell.shell.standards.core.namespace_type import NameSpaceType
from cloudshell.shell.standards.exceptions import ResourceModelException

if TYPE_CHECKING:
    from cloudshell.shell.core.driver_context import AutoLoadDetails

    from cloudshell.shell.standards.core.resource_conf import BaseConfig


class GenericResourceModel(AbstractResource):
    _RESOURCE_MODEL = "GenericResource"
    SUPPORTED_FAMILY_NAMES = []

    # Attributes
    contact_name = ResourceAttribute(
        attribute_names.CONTACT_NAME, NameSpaceType.FAMILY_NAME
    )
    system_name = ResourceAttribute(
        attribute_names.SYSTEM_NAME, NameSpaceType.FAMILY_NAME
    )
    location = ResourceAttribute(attribute_names.LOCATION, NameSpaceType.FAMILY_NAME)
    model = ResourceAttribute(attribute_names.MODEL, NameSpaceType.FAMILY_NAME)
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )
    os_version = ResourceAttribute(
        attribute_names.OS_VERSION, NameSpaceType.FAMILY_NAME
    )
    vendor = ResourceAttribute(attribute_names.VENDOR, NameSpaceType.FAMILY_NAME)

    def __init__(
        self,
        resource_name: str,
        shell_name: str,
        family_name: str,
        api: CloudShellAPISession,
    ):
        if family_name not in self.SUPPORTED_FAMILY_NAMES:
            families = ", ".join(self.SUPPORTED_FAMILY_NAMES)
            raise ResourceModelException(
                f"Not supported family name {family_name}. "
                f"Family name should be one of: {families}"
            )
        super().__init__(None, shell_name, name=resource_name, family_name=family_name)
        self._api = api
        self._existed_resource_info = ExistedResourceInfo(resource_name, api)
        self._existed_resource_info.load_data()

    @property
    @abstractmethod
    def entities(self):
        pass

    def connect_chassis(self, chassis: GenericChassis) -> None:
        """Connect chassis sub resource."""
        self._add_sub_resource_with_type_restrictions(chassis, [GenericChassis])

    def connect_port_channel(self, port_channel: GenericPortChannel) -> None:
        """Connect port channel sub resource."""
        self._add_sub_resource_with_type_restrictions(
            port_channel, [GenericPortChannel]
        )

    @classmethod
    def from_resource_config(cls, resource_config: BaseConfig) -> Self:
        return cls(
            resource_config.name,
            resource_config.shell_name,
            resource_config.family_name,
            api=resource_config.api,
        )

    def build(self) -> AutoLoadDetails:
        return AutoloadDetailsBuilder(self, self._existed_resource_info).build_details()


class GenericChassis(AbstractResource):
    _RELATIVE_ADDRESS_PREFIX = "CH"
    _NAME_TEMPLATE = "Chassis {}"
    _FAMILY_NAME = "CS_Chassis"
    _RESOURCE_MODEL = "GenericChassis"

    # Attributes
    model = ResourceAttribute(attribute_names.MODEL)
    serial_number = ResourceAttribute(attribute_names.SERIAL_NUMBER)
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )

    def connect_module(self, module: GenericModule) -> None:
        """Connect module sub resource."""
        self._add_sub_resource_with_type_restrictions(module, [GenericModule])

    def connect_power_port(self, power_port: GenericPowerPort) -> None:
        """Connect power_port sub resource."""
        self._add_sub_resource_with_type_restrictions(power_port, [GenericPowerPort])

    def connect_port(self, port: GenericPort) -> None:
        """Connect port sub resource."""
        self._add_sub_resource_with_type_restrictions(port, [GenericPort])


class GenericModule(AbstractResource):
    _RELATIVE_ADDRESS_PREFIX = "M"
    _NAME_TEMPLATE = "Module {}"
    _FAMILY_NAME = "CS_Module"
    _RESOURCE_MODEL = "GenericModule"

    # Attributes
    model = ResourceAttribute(attribute_names.MODEL)
    version = ResourceAttribute(attribute_names.VERSION)
    serial_number = ResourceAttribute(attribute_names.SERIAL_NUMBER)
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )

    def connect_sub_module(self, sub_module: GenericSubModule) -> None:
        """Connect sub_module sub resource."""
        self._add_sub_resource_with_type_restrictions(sub_module, [GenericSubModule])

    def connect_port(self, port: GenericPort) -> None:
        """Connect port sub resource."""
        self._add_sub_resource_with_type_restrictions(port, [GenericPort])


class GenericSubModule(AbstractResource):
    _RELATIVE_ADDRESS_PREFIX = "SM"
    _NAME_TEMPLATE = "SubModule {}"
    _FAMILY_NAME = "CS_SubModule"
    _RESOURCE_MODEL = "GenericSubModule"

    # Attributes
    model = ResourceAttribute(attribute_names.MODEL)
    version = ResourceAttribute(attribute_names.VERSION)
    serial_number = ResourceAttribute(attribute_names.SERIAL_NUMBER)
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )

    def connect_port(self, port: BasePort) -> None:
        """Connect port sub resource."""
        self._add_sub_resource_with_type_restrictions(port, [BasePort])


class BasePort(AbstractResource):
    _RELATIVE_ADDRESS_PREFIX = "P"
    _NAME_TEMPLATE = "Port {}"
    _FAMILY_NAME = "CS_Port"
    _RESOURCE_MODEL = "GenericPort"

    # Attributes
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )
    ipv4_address = ResourceAttribute(attribute_names.IPV4_ADDRESS)
    ipv6_address = ResourceAttribute(attribute_names.IPV6_ADDRESS)
    mac_address = ResourceAttribute(attribute_names.MAC_ADDRESS)


class ResourcePort(BasePort):
    port_speed = ResourceAttribute(attribute_names.PORT_SPEED, default_value=0)


class GenericPort(BasePort):
    # Attributes
    port_description = ResourceAttribute(attribute_names.PORT_DESCRIPTION)
    auto_negotiation = ResourceAttribute(attribute_names.AUTO_NEGOTIATION)
    bandwidth = ResourceAttribute(attribute_names.BANDWIDTH, default_value=0)
    duplex = ResourceAttribute(attribute_names.DUPLEX, default_value="Half")
    l2_protocol_type = ResourceAttribute(attribute_names.L2_PROTOCOL_TYPE)
    mtu = ResourceAttribute(attribute_names.MTU, default_value=0)
    adjacent = ResourceAttribute(attribute_names.ADJACENT)


class GenericPowerPort(AbstractResource):
    _RESOURCE_MODEL = "GenericPowerPort"
    _RELATIVE_ADDRESS_PREFIX = "PP"
    _NAME_TEMPLATE = "Power Port {}"
    _FAMILY_NAME = "CS_PowerPort"

    # Attributes
    model = ResourceAttribute(attribute_names.MODEL)
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )
    port_description = ResourceAttribute(attribute_names.PORT_DESCRIPTION)
    serial_number = ResourceAttribute(attribute_names.SERIAL_NUMBER)
    version = ResourceAttribute(attribute_names.VERSION)


class GenericPortChannel(AbstractResource):
    _RESOURCE_MODEL = "GenericPortChannel"
    _RELATIVE_ADDRESS_PREFIX = "PC"
    _NAME_TEMPLATE = "Port Channel{}"
    _FAMILY_NAME = "CS_PortChannel"

    # Attributes
    model_name = ResourceAttribute(
        attribute_names.MODEL_NAME, NameSpaceType.FAMILY_NAME
    )
    associated_ports = ResourceAttribute(attribute_names.ASSOCIATED_PORTS)
    ipv4_address = ResourceAttribute(attribute_names.IPV4_ADDRESS)
    ipv6_address = ResourceAttribute(attribute_names.IPV6_ADDRESS)
    port_description = ResourceAttribute(attribute_names.PORT_DESCRIPTION)
