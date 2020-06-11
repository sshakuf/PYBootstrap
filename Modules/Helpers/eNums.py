from enum import Enum


class HWInterfaceType(Enum):
    NoInterface = 0
    Serial = 1
    CanBus = 2
    I2C = 3


class NiArtException(Exception):
    pass


class MipiDataFormat(Enum):
    FMT_8192_32 = 0
    FMT_8192_64 = 1
    FMT_8192_128 = 2
    FMT_8192_256 = 3


class SysConstants:
    RxCount = 4


class _SysConfigConstant(type):
    _BoardClock: int = 100e6
    _CarrierFreq: int = 76.0e9
    _fs: int = _BoardClock // 2
    _force_init: bool = False
    _interface_type = "I2C"


# class SysConfig(object, metaclass=_SysConfig):
#     pass


class VarType(Enum):
    Simple = 1
    List = 2
    Radio = 3
    CheckBox = 4


class ExpResType(Enum):
    Int = 1
    Str = 2
    Array = 3


class BoardType(Enum):
    Undef = -1
    RX = 0
    TX = 1
    Synt = 2


class CanBusUnitID(Enum):
    NotUsed = -2
    RX1 = 0
    RX2 = 1
    RX3 = 2
    RX4 = 3
    TX = 0x010
    SYNT = 0x020


class RuningState(Enum):
    NOTINITIALIZED = 0
    INITIALIZED = 1
    STARTED = 2
    RUNNING = 3
    STOPPED = 4
    CONNECTED = 5



