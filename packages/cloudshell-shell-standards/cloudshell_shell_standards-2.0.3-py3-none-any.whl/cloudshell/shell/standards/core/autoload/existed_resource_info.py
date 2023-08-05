from __future__ import annotations

from functools import wraps
from threading import Event, Thread
from typing import TypeVar

from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceInfo

from cloudshell.shell.standards.exceptions import BaseStandardException

T = TypeVar("T")


def _wait_until_loaded(fn: T) -> T:
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        self.wait_until_loaded()
        return fn(self, *args, **kwargs)

    return wrapped


class ExistedResourceInfo:
    """Collects information about existed resource from the CloudShell.

    full_name it's a name of the resource with all parents names separated by "/"
        example: "Cisco/Chassis 1/Module 1/Port 1"
    address it's a relative address of the resource with all parents but
        without root address
        example: "CH1/M1/P1"
    """

    def __init__(self, name: str, api: CloudShellAPISession):
        self.name = name
        self._api = api
        self._started = Event()
        self._loaded = Event()
        self._uniq_id = None
        self._full_name_to_uniq_id: dict[str, str] | None = None
        self._uniq_id_to_full_name: dict[str, str] | None = None
        self._full_name_to_address: dict[str, str] | None = None
        self._address_to_full_name: dict[str, str] | None = None

    @property
    @_wait_until_loaded
    def uniq_id(self) -> str:
        return self._uniq_id

    @_wait_until_loaded
    def get_uniq_id(self, full_name: str) -> str | None:
        return self._full_name_to_uniq_id.get(full_name)

    @_wait_until_loaded
    def get_address(self, full_name: str) -> str | None:
        return self._full_name_to_address.get(full_name)

    @_wait_until_loaded
    def is_address_exists(self, relative_address: str) -> bool:
        try:
            self._address_to_full_name[relative_address]
        except KeyError:
            result = False
        else:
            result = True
        return result

    @_wait_until_loaded
    def get_full_name_by_unique_id(self, unique_id: str) -> str | None:
        return self._uniq_id_to_full_name.get(unique_id)

    def load_data(self) -> None:
        self._started.set()
        Thread(target=self._load_data).start()

    def wait_until_loaded(self) -> None:
        if not self._started.is_set():
            raise BaseStandardException("You have to start loading first")
        self._loaded.wait()

    def _load_data(self):
        r_info = self._api.GetResourceDetails(self.name)
        self._uniq_id = r_info.UniqeIdentifier
        self._full_name_to_uniq_id = {}
        self._uniq_id_to_full_name = {}
        self._full_name_to_address = {}
        self._address_to_full_name = {}

        for child in r_info.ChildResources:
            # Root resource contains invalid uniq id for children but newly loaded child
            # info contains valid uniq id for itself and its children
            updated_child = self._api.GetResourceDetails(child.Name)
            self._build_maps_for_resource(updated_child)

        self._loaded.set()

    def _build_maps_for_resource(self, r_info: ResourceInfo) -> None:
        # CS returns full address with root address - 192.168.1.3/chassis1/module1
        address = r_info.FullAddress.split("/", 1)[-1]

        self._full_name_to_uniq_id[r_info.Name] = r_info.UniqeIdentifier
        self._uniq_id_to_full_name[r_info.UniqeIdentifier] = r_info.Name
        self._full_name_to_address[r_info.Name] = address
        self._address_to_full_name[address] = r_info.Name
        for child_info in r_info.ChildResources:
            self._build_maps_for_resource(child_info)
