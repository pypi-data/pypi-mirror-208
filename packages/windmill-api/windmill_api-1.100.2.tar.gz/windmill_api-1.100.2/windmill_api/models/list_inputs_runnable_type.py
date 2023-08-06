from enum import Enum


class ListInputsRunnableType(str, Enum):
    SCRIPTHASH = "ScriptHash"
    SCRIPTPATH = "ScriptPath"
    FLOWPATH = "FlowPath"

    def __str__(self) -> str:
        return str(self.value)
