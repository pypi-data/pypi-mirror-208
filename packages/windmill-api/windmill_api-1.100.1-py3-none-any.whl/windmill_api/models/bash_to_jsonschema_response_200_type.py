from enum import Enum


class BashToJsonschemaResponse200Type(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"

    def __str__(self) -> str:
        return str(self.value)
