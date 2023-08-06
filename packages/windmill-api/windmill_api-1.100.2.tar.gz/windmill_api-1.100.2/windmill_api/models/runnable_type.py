from enum import Enum


class RunnableType(str, Enum):
    SCRIPTHASH = "ScriptHash"
    SCRIPTPATH = "ScriptPath"
    FLOWPATH = "FlowPath"

    def __str__(self) -> str:
        return str(self.value)
