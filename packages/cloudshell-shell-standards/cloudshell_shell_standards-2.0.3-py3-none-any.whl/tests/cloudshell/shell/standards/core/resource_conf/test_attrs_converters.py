from __future__ import annotations

import pytest

from cloudshell.shell.standards.core.namespace_type import NameSpaceType
from cloudshell.shell.standards.core.resource_conf.attrs_converters import (
    AbsConverter,
    AttributeConvertError,
    BoolConverter,
    CollectionConverter,
)
from cloudshell.shell.standards.core.resource_conf.resource_attr import AttrMeta


@pytest.fixture
def meta():
    return AttrMeta("test_attr", NameSpaceType.SHELL_NAME, False)


class TestAbsConverter:
    @pytest.mark.parametrize(
        "conv_type, str_type",
        [(str, "str"), (int, "int")],
    )
    def test_get_str_type(self, conv_type, str_type):
        class Converter(AbsConverter):
            type_ = conv_type

            def _convert(self) -> int:
                return int(self.val)

        assert Converter.get_str_type() == str_type

    def test_is_supported_type(self):
        class StrConverter(AbsConverter):
            type_ = str

            def _convert(self) -> str:
                return str(self.val)

        assert StrConverter.is_supported_type("str") is True

    def test_convert_failed(self, meta):
        class BoolConverter(AbsConverter):
            type_ = bool

            def _convert(self) -> bool:
                return 1 / 0

        converter = BoolConverter("", meta)
        with pytest.raises(AttributeConvertError):
            converter.convert()

    def test_convert_invalid_value(self, meta):
        class IntConverter(AbsConverter):
            type_ = int

            def _convert(self) -> int:
                return int(self.val)

        converter = IntConverter("abc", meta)
        with pytest.raises(AttributeConvertError):
            converter.convert()

    def test_convert_error_handling(self):
        class FloatConverter(AbsConverter):
            type_ = float

            def _convert(self) -> float:
                return float(self.val)

        attr_name = "test_attr"
        converter = FloatConverter("abc", attr_name)
        with pytest.raises(AttributeConvertError) as exc_info:
            converter.convert()
        assert exc_info.value.name == "test_attr"
        assert exc_info.value.str_type == "float"
        assert exc_info.value.val == "abc"
        assert f"attribute '{attr_name}' should be of type float" in str(exc_info.value)

    def test_is_supported_type_invalid(self):
        class IntConverter(AbsConverter):
            type_ = int

            def _convert(self) -> int:
                return int(self.val)

        assert IntConverter.is_supported_type("str") is False

    def test_convert_does_nothing(self, meta):
        class TestConverter(AbsConverter):
            type_ = str

            def _convert(self) -> str:
                return super()._convert()

        conv = TestConverter("abc", meta)

        assert conv.convert() is None


@pytest.mark.parametrize(
    "val, bool_val",
    [
        ("true", True),
        ("True", True),
        ("false", False),
        ("False", False),
        ("yes", True),
        ("Yes", True),
        ("no", False),
        ("No", False),
        ("y", True),
        ("n", False),
    ],
)
def test_bool_converter(val, bool_val, meta):
    conv = BoolConverter(val, meta)

    assert conv.convert() is bool_val


def test_invalid_bool(meta):
    conv = BoolConverter("abc", meta)

    with pytest.raises(AttributeConvertError):
        conv.convert()


def test_collection_converter(meta):
    class TestCollectionConverter(CollectionConverter):
        type_ = list

    conv = TestCollectionConverter("a,b;c", meta)

    assert conv.convert() == ["a", "b", "c"]
    assert conv.get_str_child_type("list[str]") == "str"
