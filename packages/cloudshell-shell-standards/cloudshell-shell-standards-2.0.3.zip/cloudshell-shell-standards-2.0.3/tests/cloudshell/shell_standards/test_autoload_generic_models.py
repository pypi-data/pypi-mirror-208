from cloudshell.shell.standards.autoload_generic_models import (
    GenericResourceModel,
    ResourcePort,
)


class ResourceModel(GenericResourceModel):
    SUPPORTED_FAMILY_NAMES = ["Family Name"]

    @property
    def entities(self):
        class _ResourceEntities:
            Port = ResourcePort

        return _ResourceEntities


def test_resource_model(api):
    resource_name = "resource name"
    shell_name = "shell name"
    family_name = "Family Name"

    resource = ResourceModel(resource_name, shell_name, family_name, api)

    assert family_name == resource.family_name
    assert shell_name == resource.shell_name
    assert resource_name == resource.name
    assert "" == resource.relative_address.__repr__()
    assert "GenericResource" == resource.resource_model
    assert f"{shell_name}.{resource.resource_model}" == resource.cloudshell_model_name
    assert ResourcePort == resource.entities.Port
    assert isinstance(resource.unique_identifier, str)
    assert bool(resource.unique_identifier)


def test_resource_build(api):
    resource_name = "resource name"
    shell_name = "shell name"
    family_name = "Family Name"
    contact_name = "contact name"
    system_name = "system name"
    location = "location"
    model = "model"
    model_name = "model name"
    os_version = "os version"
    vendor = "vendor"

    resource = ResourceModel(resource_name, shell_name, family_name, api)

    resource.contact_name = contact_name
    resource.system_name = system_name
    resource.location = location
    resource.model = model
    resource.model_name = model_name
    resource.os_version = os_version
    resource.vendor = vendor

    autoload_detail = resource.build()
    resource_attributes = {
        attr.attribute_name: attr.attribute_value for attr in autoload_detail.attributes
    }
    expected_attributes = {
        "Contact Name": contact_name,
        "Location": location,
        "Model": model,
        "Model Name": model_name,
        "OS Version": os_version,
        "System Name": system_name,
        "Vendor": vendor,
    }
    expected_attributes = {
        f"{family_name}.{k}": v for k, v in expected_attributes.items()
    }

    assert expected_attributes == resource_attributes
