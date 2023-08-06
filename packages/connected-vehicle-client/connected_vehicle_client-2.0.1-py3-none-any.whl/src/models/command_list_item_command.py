from enum import Enum


class CommandListItemCommand(str, Enum):
    CLIMATIZATION_START = "CLIMATIZATION_START"
    CLIMATIZATION_STOP = "CLIMATIZATION_STOP"
    ENGINE_START = "ENGINE_START"
    ENGINE_STOP = "ENGINE_STOP"
    FLASH = "FLASH"
    HONK = "HONK"
    HONK_AND_FLASH = "HONK_AND_FLASH"
    LOCK = "LOCK"
    LOCK_REDUCED_GUARD = "LOCK_REDUCED_GUARD"
    SEND_NAVI_POI = "SEND_NAVI_POI"
    UNLOCK = "UNLOCK"

    def __str__(self) -> str:
        return str(self.value)
