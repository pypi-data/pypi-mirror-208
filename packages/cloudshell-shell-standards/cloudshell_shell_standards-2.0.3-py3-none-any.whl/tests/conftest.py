from __future__ import annotations

from unittest.mock import Mock

import pytest

from cloudshell.shell.core.driver_context import (
    ReservationContextDetails,
    ResourceCommandContext,
    ResourceContextDetails,
)


@pytest.fixture()
def api():
    return Mock(
        DecryptPassword=lambda x: Mock(Value=x),
        GetResourceDetails=lambda x: Mock(
            UniqueIdentifier="uniq id", ChildResources=[]
        ),
    )


@pytest.fixture()
def context_creator():
    def create_context(
        r_name: str,
        r_model: str,
        r_family: str,
        r_address: str,
        attributes: dict[str, str],
        access_key="",
    ):
        return ResourceCommandContext(
            connectivity=None,
            reservation=ReservationContextDetails(
                environment_name="env",
                environment_path="env",
                domain="Global",
                description="desc",
                owner_user="user",
                owner_email="email",
                reservation_id="id",
                saved_sandbox_name="sandbox",
                saved_sandbox_id="id",
                running_user="user",
                cloud_info_access_key=access_key,
            ),
            connectors=[],
            resource=ResourceContextDetails(
                id=f"id-{r_name}",
                name=r_name,
                fullname=r_name,
                type="Resource",
                address=r_address,
                model=r_model,
                family=r_family,
                description="",
                attributes=attributes,
                app_context=None,
                networks_info=None,
                shell_standard=None,
                shell_standard_version=None,
            ),
        )

    return create_context
