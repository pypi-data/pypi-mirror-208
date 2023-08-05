from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Sequence, TypeVar, Union

from attrs import field, frozen, setters
from typing_extensions import Self

from cloudshell.shell.standards.core.namespace_type import NameSpaceType
from cloudshell.shell.standards.exceptions import ResourceConfigException

if TYPE_CHECKING:
    # used for TypeVar
    from attrs import Attribute  # noqa: F401

    from cloudshell.shell.standards.core.resource_conf import BaseConfig  # noqa: F401


CONFIG_TYPE = TypeVar("CONFIG_TYPE", bound="BaseConfig")
VALUE_TYPE = TypeVar("VALUE_TYPE")
VALIDATOR_TYPE = Callable[[CONFIG_TYPE, "Attribute[VALUE_TYPE]", VALUE_TYPE], None]
VALIDATOR_ARG = Union[VALIDATOR_TYPE, Sequence[VALIDATOR_TYPE]]


class WithoutMeta(ResourceConfigException):
    pass


class _Raise(enum.Enum):
    RAISE = enum.auto()


RAISE = _Raise.RAISE


@frozen
class AttrMeta:
    DICT_KEY: ClassVar[str] = "_standard"
    name: str
    namespace_type: NameSpaceType
    is_password: bool

    @classmethod
    def from_field(cls, f: Attribute) -> Self:
        meta = f.metadata.get(cls.DICT_KEY)
        if not meta:
            raise WithoutMeta
        return meta


def attr(
    name: str,
    namespace: NameSpaceType = NameSpaceType.SHELL_NAME,
    is_password: bool = False,
    default: Any = RAISE,
    converter: Callable[[Any], Any] | None = None,
    validator: VALIDATOR_ARG | None = None,
) -> Any:
    return field(
        metadata={AttrMeta.DICT_KEY: AttrMeta(name, namespace, is_password)},
        default=default,
        kw_only=True,
        on_setattr=setters.frozen,
        converter=converter,
        validator=validator,
        repr=not is_password,
    )


def get_str_type(f: Attribute) -> str:
    return f.type if isinstance(f.type, str) else f.type.__name__
