from enum import Enum


class CreateInputRunnableType(str, Enum):
    SCRIPTHASH = "ScriptHash"
    SCRIPTPATH = "ScriptPath"
    FLOWPATH = "FlowPath"

    def __str__(self) -> str:
        return str(self.value)
