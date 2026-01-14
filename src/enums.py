# enums.py

from enum import Enum, auto

class SupplyCommand(Enum):
    OPEN_OUTPUT = auto()
    CLOSE_OUTPUT = auto()
    MEASURE_VOLTAGE = auto()
    MEASURE_CURRENT = auto()
    SET_VOLTAGE = auto()
    SET_CURRENT = auto()
    IDN = auto()
    ECHO_TEST = auto()

class ProtocolFlavor(Enum):
    """
    İleride vendor-specific format eklersin.
    Şimdilik SCPI default.
    """
    SCPI = auto()
