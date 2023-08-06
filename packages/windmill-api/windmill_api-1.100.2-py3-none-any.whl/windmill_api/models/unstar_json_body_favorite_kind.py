from enum import Enum


class UnstarJsonBodyFavoriteKind(str, Enum):
    FLOW = "flow"
    APP = "app"
    SCRIPT = "script"
    RAW_APP = "raw_app"

    def __str__(self) -> str:
        return str(self.value)
