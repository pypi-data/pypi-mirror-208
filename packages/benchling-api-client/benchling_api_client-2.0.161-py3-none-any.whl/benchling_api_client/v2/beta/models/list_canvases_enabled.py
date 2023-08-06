from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListCanvasesEnabled(Enums.KnownString):
    TRUE = "true"
    FALSE = "false"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListCanvasesEnabled":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListCanvasesEnabled must be a string (encountered: {val})")
        newcls = Enum("ListCanvasesEnabled", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListCanvasesEnabled, getattr(newcls, "_UNKNOWN"))
