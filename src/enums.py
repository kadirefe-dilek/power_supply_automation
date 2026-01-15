# enums.py

from enum import Enum, auto


class SupplyCommand(Enum):
    # Basic control
    OPEN_OUTPUT = auto()
    CLOSE_OUTPUT = auto()
    SET_VOLTAGE = auto()
    SET_CURRENT = auto()
    MEASURE_VOLTAGE = auto()
    MEASURE_CURRENT = auto()
    IDN = auto()

    # E364xA / SCPI extended ops (requested)
    RESET = auto()

    SYSTEM_REMOTE = auto()
    SYSTEM_LOCAL = auto()
    SYSTEM_RWLOCK = auto()

    SET_RANGE_LOW = auto()
    SET_RANGE_HIGH = auto()

    OVP_SET = auto()
    OVP_ENABLE = auto()
    OVP_DISABLE = auto()
    OVP_CLEAR = auto()

    # Test hook
    ECHO_TEST = auto()
