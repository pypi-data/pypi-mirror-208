from enum import Enum


class NewScriptKind(str, Enum):
    SCRIPT = "script"
    FAILURE = "failure"
    TRIGGER = "trigger"
    COMMAND = "command"
    APPROVAL = "approval"

    def __str__(self) -> str:
        return str(self.value)
