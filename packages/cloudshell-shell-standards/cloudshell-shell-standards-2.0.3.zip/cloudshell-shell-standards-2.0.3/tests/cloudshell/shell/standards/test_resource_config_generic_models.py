from cloudshell.shell.core.driver_context import AutoLoadCommandContext

from cloudshell.shell.standards import attribute_names as attr_name
from cloudshell.shell.standards.resource_config_generic_models import (
    CliConnectionType,
    GenericCLIConfig,
)


def test_cli_config(api, context_creator):
    r_name = "resource name"
    r_model = "resource model"
    r_family = "resource family"
    r_address = "resource address"
    user = "user"
    password = "password"
    enable_password = "enable password"
    vrf_management_name = "vrf name"
    cli_connection_type = CliConnectionType.SSH
    cli_tcp_port = 22
    session_concurrency_limit = 2
    access_key = "access key"

    r_attributes = {
        attr_name.USER: user,
        attr_name.PASSWORD: password,
        attr_name.ENABLE_PASSWORD: enable_password,
        attr_name.CLI_CONNECTION_TYPE: cli_connection_type.value,
        attr_name.CLI_TCP_PORT: cli_tcp_port,
        attr_name.SESSION_CONCURRENCY_LIMIT: session_concurrency_limit,
        attr_name.VRF_MANAGEMENT_NAME: vrf_management_name,
    }
    r_attributes = {f"{r_model}.{k}": v for k, v in r_attributes.items()}
    context = context_creator(
        r_name, r_model, r_family, r_address, r_attributes, access_key
    )

    conf = GenericCLIConfig.from_context(context, api)

    assert conf.user == user
    assert conf.password == password
    assert conf.enable_password == enable_password
    assert conf.cli_connection_type == cli_connection_type
    assert conf.cli_tcp_port == cli_tcp_port
    assert conf.sessions_concurrency_limit == session_concurrency_limit
    assert conf.access_key == access_key


def test_cli_config_with_autoload_context(api, context_creator):
    r_name = "resource name"
    r_model = "resource model"
    r_family = "resource family"
    r_address = "resource address"
    user = "user"
    password = "password"
    enable_password = "enable password"
    vrf_management_name = "vrf name"
    cli_connection_type = CliConnectionType.SSH
    cli_tcp_port = 22
    session_concurrency_limit = 2
    access_key = "access key"

    r_attributes = {
        attr_name.USER: user,
        attr_name.PASSWORD: password,
        attr_name.ENABLE_PASSWORD: enable_password,
        attr_name.CLI_CONNECTION_TYPE: cli_connection_type.value,
        attr_name.CLI_TCP_PORT: cli_tcp_port,
        attr_name.SESSION_CONCURRENCY_LIMIT: session_concurrency_limit,
        attr_name.VRF_MANAGEMENT_NAME: vrf_management_name,
    }
    r_attributes = {f"{r_model}.{k}": v for k, v in r_attributes.items()}
    context = context_creator(
        r_name, r_model, r_family, r_address, r_attributes, access_key
    )
    context = AutoLoadCommandContext(
        context.connectivity,
        context.resource,
    )

    conf = GenericCLIConfig.from_context(context, api)

    assert conf.user == user
    assert conf.password == password
    assert conf.enable_password == enable_password
    assert conf.cli_connection_type == cli_connection_type
    assert conf.cli_tcp_port == cli_tcp_port
    assert conf.sessions_concurrency_limit == session_concurrency_limit
    assert conf.access_key == ""
