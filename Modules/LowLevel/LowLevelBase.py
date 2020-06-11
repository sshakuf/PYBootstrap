import threading

import numpy as np
from Modules.Helpers.eNums import *
import logging
# from Core.Enums import HWInterfaceType, NiArtException
# from HWModules.RX.RxEnums import *
# from Core.BaseNiArtObject import BaseNiArtObject


logger = logging.getLogger(__name__)


def low_level_locked_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface is None or not self.is_dev_open:
            raise NiArtException(f"LowLevel hw_interface is not open")
        else:
            try:
                self._hw_interface_lock.acquire()
                res = function(self, *args, **kwargs)
                self._hw_interface_lock.release()
            except Exception as e:
                line = f"LowLevel hw_interface exception: {str(e)}"
                self.logger.error(line)
                raise NiArtException(line)
            return res
    return wrapper


def low_level_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface is None or not self.is_dev_open:
            raise NiArtException(f"LowLevel hw_interface is not open")
        else:
            try:
                res = function(self, *args, **kwargs)
            except Exception as e:
                line = f"LowLevel hw_interface exception: {str(e)}"
                self.logger.error(line)
                raise NiArtException(line)
            return res
    return wrapper


class LowLevelBase:
    def __init__(self):
        super().__init__()
        self.is_verbose = False
        self._hw_interface = None
        self.is_verbose = True
        # self.port = None
        # self.baud_rate = None
        self.can_bus_unit_id: CanBusUnitID = CanBusUnitID.NotUsed
        self.is_dev_open = False
        self._hw_interface_lock: threading.Lock = threading.Lock()

    def init(self, is_verbose):
        self.is_verbose = is_verbose

    def cleanup(self):
        self.disconnect()

    def connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        self.can_bus_unit_id = can_bus_unit_id

    def disconnect(self):
        pass

    def read_reg(self, block: Enum, address: int, expected_res: ExpResType):
        pass

    def write_reg(self, block: Enum, address: int, value: int):
        pass

    def write_block(self, block: Enum, address: int, block_data: np.ndarray):
        pass

    def read_block(self, block: Enum, address: int, length: int):
        pass

