import pytest

from cloudshell.shell.standards.core.resource_conf.enum import EnumCaseInsensitive


class SnmpVersion(EnumCaseInsensitive):
    V1 = "v1"
    V2C = "v2c"
    V3 = "v3"


@pytest.mark.parametrize(
    ("str_version",),
    (
        ("v2c",),
        ("V2C",),
        ("v2C",),
    ),
)
def test_case_insensitive(str_version):
    version = SnmpVersion(str_version)
    assert version == SnmpVersion.V2C


def test_missed_value():
    with pytest.raises(ValueError):
        SnmpVersion("v4")
