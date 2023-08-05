from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define
from attrs.validators import ge

from cloudshell.shell.standards import attribute_names as attr_name
from cloudshell.shell.standards.core.resource_conf import BaseConfig, attr
from cloudshell.shell.standards.core.resource_conf.enum import EnumCaseInsensitive

if TYPE_CHECKING:
    from typing_extensions import Self

    from cloudshell.api.cloudshell_api import CloudShellAPISession

    from cloudshell.shell.standards.core.resource_conf.attrs_converter import (
        RESOURCE_CONTEXT_TYPES,
    )


class SnmpVersion(EnumCaseInsensitive):
    V1 = "v1"
    V2C = "v2c"
    V3 = "v3"


class SnmpV3AuthProtocol(EnumCaseInsensitive):
    NO_AUTHENTICATION_PROTOCOL = "No Authentication Protocol"
    MD5 = "MD5"
    SHA = "SHA"


class SnmpV3PrivProtocol(EnumCaseInsensitive):
    NO_PRIVACY_PROTOCOL = "No Privacy Protocol"
    DES = "DES"
    DES3 = "3DES-EDE"
    AES128 = "AES-128"
    AES192 = "AES-192"
    AES256 = "AES-256"


@define(slots=False, str=False)
class GenericSnmpConfig(BaseConfig):
    snmp_read_community: str = attr(attr_name.SNMP_READ_COMMUNITY, is_password=True)
    snmp_write_community: str = attr(attr_name.SNMP_WRITE_COMMUNITY, is_password=True)
    snmp_v3_user: str = attr(attr_name.SNMP_V3_USER)
    snmp_v3_password: str = attr(attr_name.SNMP_V3_PASSWORD, is_password=True)
    snmp_v3_private_key: str = attr(attr_name.SNMP_V3_PRIVATE_KEY)
    snmp_v3_auth_protocol: SnmpV3AuthProtocol = attr(attr_name.SNMP_V3_AUTH_PROTOCOL)
    snmp_v3_priv_protocol: SnmpV3PrivProtocol = attr(attr_name.SNMP_V3_PRIVACY_PROTOCOL)
    snmp_version: SnmpVersion = attr(attr_name.SNMP_VERSION, default=SnmpVersion.V2C)
    enable_snmp: bool = attr(attr_name.ENABLE_SNMP)
    disable_snmp: bool = attr(attr_name.DISABLE_SNMP)


class CliConnectionType(EnumCaseInsensitive):
    AUTO = "Auto"
    CONSOLE = "Console"
    SSH = "SSH"
    TELNET = "Telnet"
    TCP = "TCP"


@define(slots=False, str=False)
class GenericCLIConfig(BaseConfig):
    user: str = attr(attr_name.USER)
    password: str = attr(attr_name.PASSWORD, is_password=True)
    enable_password: str = attr(attr_name.ENABLE_PASSWORD, is_password=True)
    cli_connection_type: CliConnectionType = attr(attr_name.CLI_CONNECTION_TYPE)
    cli_tcp_port: int = attr(attr_name.CLI_TCP_PORT, validator=ge(0))
    sessions_concurrency_limit: int = attr(
        attr_name.SESSION_CONCURRENCY_LIMIT, validator=ge(1)
    )
    vrf_management_name: str = attr(attr_name.VRF_MANAGEMENT_NAME)
    access_key: str = ""
    access_key_passphrase: str = ""

    @classmethod
    def from_context(
        cls, context: RESOURCE_CONTEXT_TYPES, api: CloudShellAPISession
    ) -> Self:
        self = super().from_context(context, api)
        self.access_key = cls._get_access_key(context)
        return self

    @staticmethod
    def _get_access_key(context: RESOURCE_CONTEXT_TYPES) -> str:
        try:
            # reservation context not present in Autoload context
            # cloud_info_access_key appears in CS 2021.1
            key = context.reservation.cloud_info_access_key
        except AttributeError:
            key = ""
        return key


@define(slots=False, str=False)
class GenericConsoleServerConfig(BaseConfig):
    console_server_ip_address: str = attr(attr_name.CONSOLE_SERVER_IP_ADDRESS)
    console_user: str = attr(attr_name.CONSOLE_USER)
    console_port: int = attr(attr_name.CONSOLE_PORT, validator=ge(0))
    console_password: str = attr(attr_name.CONSOLE_PASSWORD, is_password=True)


class BackupType(EnumCaseInsensitive):
    FILE_SYSTEM = "File System"
    FTP = "FTP"
    TFTP = "TFTP"
    SCP = "SCP"


@define(slots=False, str=False)
class GenericBackupConfig(BaseConfig):
    backup_location: str = attr(attr_name.BACKUP_LOCATION)
    backup_type: BackupType = attr(attr_name.BACKUP_TYPE)
    backup_user: str = attr(attr_name.BACKUP_USER)
    backup_password: str = attr(attr_name.BACKUP_PASSWORD, is_password=True)
