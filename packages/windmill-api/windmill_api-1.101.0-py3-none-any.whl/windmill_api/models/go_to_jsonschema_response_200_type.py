from enum import Enum


class GoToJsonschemaResponse200Type(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"

    def __str__(self) -> str:
        return str(self.value)
