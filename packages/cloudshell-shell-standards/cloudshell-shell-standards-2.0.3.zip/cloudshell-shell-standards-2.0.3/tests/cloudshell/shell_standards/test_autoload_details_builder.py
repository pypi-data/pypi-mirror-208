import uuid
from unittest.mock import Mock

import pytest

from cloudshell.shell.core.driver_context import AutoLoadDetails

from cloudshell.shell.standards.autoload_generic_models import (
    GenericChassis,
    GenericModule,
    GenericPort,
    GenericResourceModel,
    GenericSubModule,
)
from cloudshell.shell.standards.core.autoload.existed_resource_info import (
    ExistedResourceInfo,
)
from cloudshell.shell.standards.core.autoload.utils import AutoloadDetailsBuilder


class TestNetworkingResourceModel(GenericResourceModel):
    SUPPORTED_FAMILY_NAMES = ["CS_Switch"]

    @property
    def entities(self):
        class _NetworkingEntities:
            Chassis = GenericChassis
            Module = GenericModule
            SubModule = GenericSubModule
            Port = GenericPort

        return _NetworkingEntities


def _create_resource(api):
    """Creates a resource.

    Resource structure:
    Chassis1 Module1  Sub Module1-1  Port1-1-1
                      Sub Module1-2  Port1-2-1
                                     Port1-2-2
                      Port 1-3
             Module2  Sub Module2-1
                      Sub Module2-2
                      Port 2-3
             Module3  Sub Module3-1
             Module4
    """
    port_1_1_1 = GenericPort("1-1-1")
    port_1_2_1 = GenericPort("1-2-1")
    port_1_2_1.model_name = "port-1-2-1"
    port_1_2_2 = GenericPort("1-2-2")
    port_1_2_2.model_name = "port-1-2-2"
    port_1_3 = GenericPort("1-3")
    port_1_3.model_name = "port-1-3"
    port_2_3 = GenericPort("2-3")
    port_2_3.model_name = "port-2-3"

    sub_module1_1 = GenericSubModule("1")
    sub_module1_1.model = "submodule1-1 model"
    sub_module1_1.connect_port(port_1_1_1)

    sub_module1_2 = GenericSubModule("2")
    sub_module1_2.model = "submodule1-2 model"
    sub_module1_2.connect_port(port_1_2_1)
    sub_module1_2.connect_port(port_1_2_2)

    sub_module2_1 = GenericSubModule("1")
    sub_module2_1.model = "submodule2-1 model"

    sub_module2_2 = GenericSubModule("2")
    sub_module2_2.model = "submodule2-2 model"

    sub_module3_1 = GenericSubModule("1")
    sub_module3_1.model = "submodule3-1 model"

    module1 = GenericModule("1")
    module1.model = "module1 model"
    module1.connect_sub_module(sub_module1_1)
    module1.connect_sub_module(sub_module1_2)
    module1.connect_port(port_1_3)

    module2 = GenericModule("2")
    module2.model = "module2 model"
    module2.connect_sub_module(sub_module2_1)
    module2.connect_sub_module(sub_module2_2)
    module2.connect_port(port_2_3)

    module3 = GenericModule("3")
    module3.model = "module3 model"
    module3.connect_sub_module(sub_module3_1)

    module4 = GenericModule("4")
    module4.model = "module4 model"

    chassis = GenericChassis("1")
    chassis.connect_module(module1)
    chassis.connect_module(module2)
    chassis.connect_module(module3)
    chassis.connect_module(module4)

    resource = TestNetworkingResourceModel(
        "resource name", "shell name", "CS_Switch", api
    )
    resource.connect_chassis(chassis)
    return resource


@pytest.fixture()
def resource(api):
    return _create_resource(api)


def test_filtering_empty_modules(resource):
    expected_resource_names = {
        "Chassis 1",
        "Module 1",
        "SubModule 1",
        "Port 1-1-1",
        "SubModule 2",
        "Port 1-2-1",
        "Port 1-2-2",
        "Port 1-3",
        "Module 2",
        "Port 2-3",
    }

    details = resource.build()
    resource_names = {resource.name for resource in details.resources}
    assert resource_names == expected_resource_names


def test_autoload_details_builder_with_cs_id(resource):
    cs_resource_id = uuid.uuid4()
    resource.cs_resource_id = cs_resource_id
    structure = resource.build()

    unique_ids = [resource.unique_identifier for resource in structure.resources]
    assert len(set(unique_ids)) == len(unique_ids), "Not all unique ids are unique"


def test_build_details_with_no_sub_resources(resource, api):
    # Arrange
    resource_model = TestNetworkingResourceModel(
        "resource name", "shell name", "CS_Switch", api
    )
    resource_model.contact_name = "contact name"
    resource_model.os_version = "os version"
    resource_model.location = "location"
    resource_model.model = "model"
    resource_model.model_name = "model"
    resource_model.vendor = "vendor"
    resource_model.system_name = "system name"
    existed_resource_info = ExistedResourceInfo("TestResource", api)
    existed_resource_info.load_data()
    builder = AutoloadDetailsBuilder(resource_model, existed_resource_info)

    # Act
    result = builder.build_details()

    # Assert
    assert isinstance(result, AutoLoadDetails)
    assert len(result.resources) == 0
    assert len(result.attributes) == 7


def test_get_relative_address_with_updated_address(resource):
    # Check that newly autoloaded resource with the same address as existed
    # will get new address.
    # Arrange
    ex_res = resource._existed_resource_info
    ex_res.wait_until_loaded()
    module_full_name = "123/Chassis 1/Module M1"
    module_uniq_id = "123123123"
    module_addr = "CH1/M1"
    ex_res._full_name_to_uniq_id = {module_full_name: module_uniq_id}
    ex_res._uniq_id_to_full_name = {module_uniq_id: module_full_name}
    ex_res._full_name_to_address = {module_full_name: module_addr}
    ex_res._address_to_full_name = {module_addr: module_full_name}

    # Act
    result = resource.build()

    # Assert
    updated_module = next(x for x in result.resources if x.name == "Module 1")
    assert updated_module.relative_address == "CH1/M1-0"
    updated_sub_module = next(x for x in result.resources if x.name == "SubModule 1")
    assert updated_sub_module.relative_address == "CH1/M1-0/SM1"


def test_get_relative_address_with_updated_rel_path_map_re_autoload(resource):
    # Arrange
    resource._existed_resource_info = ExistedResourceInfo("TestResource", resource._api)
    resource._existed_resource_info.load_data()
    _ = resource._existed_resource_info.uniq_id
    module_1_uniq_id = next(
        (
            x
            for x in resource._child_resources[0]._child_resources
            if x.name == "Module 1"
        ),
        None,
    ).unique_identifier
    resource._existed_resource_info._full_name_to_uniq_id = {
        "resource name/Chassis 1/Module M1": "123123123",
        "resource name/Chassis 1/Module 1": module_1_uniq_id,
    }
    resource._existed_resource_info._uniq_id_to_full_name = {
        "123123123": "resource name/Chassis 1/Module M1",
        module_1_uniq_id: "resource name/Chassis 1/Module 1",
    }
    resource._existed_resource_info._full_name_to_address = {
        "resource name/Chassis 1/Module M1": "1.1.1.1/CH1/M1",
        "resource name/Chassis 1/Module 1": "1.1.1.1/CH1/M1-0",
    }
    resource._existed_resource_info._full_address_to_name = {
        "CH1/M1": "resource name/Chassis 1/Module M1",
        "CH1/M1-0": "resource name/Chassis 1/Module 1",
    }

    resource._api.GetResourceDetails = lambda x: Mock(
        UniqueIdentifier="uniq id", ChildResources=[]
    )

    # Act
    result = resource.build()

    # Assert
    duplicate_rel_path_module = next(
        (x for x in result.resources if x.name.endswith("Module 1")), None
    )
    assert duplicate_rel_path_module.relative_address.endswith("CH1/M1-0")
    assert duplicate_rel_path_module.unique_identifier == module_1_uniq_id
    assert (
        next(
            (
                x
                for x in result.resources
                if x.relative_address.endswith("CH1/M1-0/SM1")
            ),
            None,
        )
        is not None
    )
    assert (
        next(
            (
                x
                for x in result.resources
                if x.relative_address.endswith("CH1/M1-0-0/SM1")
            ),
            None,
        )
        is None
    )


def test_get_address_from_cs(resource):
    ex_res = resource._existed_resource_info
    ex_res.wait_until_loaded()
    cs_module_addr = "CH1/Module2"
    ex_res._full_name_to_address = {
        f"{resource.name}/Chassis 1/Module 2": cs_module_addr
    }

    result = resource.build()

    module = next(x for x in result.resources if x.name == "Module 2")
    assert module.relative_address == cs_module_addr
    port = next(x for x in result.resources if x.name == "Port 2-3")
    assert port.relative_address == f"{cs_module_addr}/P2-3"
