from enum import Enum


class CreateDraftJsonBodyTyp(str, Enum):
    FLOW = "flow"
    SCRIPT = "script"
    APP = "app"

    def __str__(self) -> str:
        return str(self.value)
