from enum import Enum
from typing import Any


class EnumCaseInsensitive(Enum):
    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value.casefold() == value.casefold():
                    return member
        return None
