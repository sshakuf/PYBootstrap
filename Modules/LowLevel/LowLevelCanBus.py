import struct
import time
import numpy as np
from Modules.LowLevel.LowLevelBase import *


def low_level_locked_can_bus_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface_can_bus is None or not self.is_dev_can_bus_open:
            raise NiArtException(f"LowLevel hw_interface is not open")
        else:
            try:
                self._hw_interface_can_bus_lock.acquire()
                res = function(self, *args, **kwargs)
                self._hw_interface_can_bus_lock.release()
            except Exception as e:
                line = f"LowLevel hw_interface exception: {str(e)}"
                self.logger.error(line)
                raise NiArtException(line)
            return res

    return wrapper


def low_level_can_bus_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface_can_bus is None or not self.is_dev_can_bus_open:
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


class LowLevelCanBus(LowLevelBase):
    _hw_interface_can_bus = None
    _hw_interface_can_bus_lock: threading.Lock = threading.Lock()
    _using_count = 0

    @classmethod
    def connect_can_bus(cls):
        # Open CAN channel, virtual channels are considered ok to use
        # Todo: put usb port in config
        usb_port = 0
        if cls._hw_interface_can_bus is None:
            cls._hw_interface_can_bus = canlib.openChannel(usb_port, canlib.canOPEN_ACCEPT_VIRTUAL)
            cls.logger.debug("Setting bit rate to 1000 kb/s")
            cls._hw_interface_can_bus.setBusParams(canlib.canBITRATE_1M)
            cls.logger.debug("Going on bus\n\n")
            cls._hw_interface_can_bus.busOn()
            cls._using_count += 1

    @classmethod
    def diconnect_can_bus(cls):
        if cls._hw_interface_can_bus is not None:
            if cls._using_count <= 1:
                cls._hw_interface_can_bus.close()
                cls._hw_interface_can_bus = None
                cls._using_count = 1
        cls._using_count -= 1

    def __init__(self):
        super().__init__()

    # @low_level_locked_can_bus_call
    def connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        super().connect(hw_interface_type, can_bus_unit_id)
        self.logger.debug(f"Opening channel {self.can_bus_unit_id}")
        self.connect_can_bus()
        self.is_dev_can_bus_open = True

    # @low_level_locked_can_bus_call
    def disconnect(self):
        self.is_dev_can_bus_open = False
        self.diconnect_can_bus()
        self._hw_interface_can_bus = None
        super().disconnect()

    # @low_level_locked_can_bus_call
    @low_level_can_bus_call
    def read_reg(self, block: Enum, address: int, expected_res: ExpResType):
        super().read_reg(block, address, expected_res)
        payload = struct.pack(">bi", block.value, address)
        send_frame = Frame(id_=0x0200 + self.can_bus_unit_id.value, data=payload, dlc=len(payload), flags=0)
        self._hw_interface_can_bus.write(send_frame)
        time.sleep(0.1)  # time.sleep(0.01)  # this delay (0.1) is necessary when using long cable (?)
        res = -1
        for retry in range(5):
            try:
                response = self._hw_interface_can_bus.read()
                if response.id == 0x0280 + self.can_bus_unit_id.value and response.dlc == 2:
                    res = int(response.data[0]) << 8 | int(response.data[1])
                    break
                else:
                    time.sleep(0.01)
            except Exception as ex:
                res = -1
                time.sleep(0.01)
        return np.int16(res)

    # @low_level_locked_can_bus_call
    @low_level_can_bus_call
    def write_reg(self, block: Enum, address: int, value: int):
        super().write_reg(block, address, value)
        if value > 32767:
            payload = struct.pack(">biH", block.value, address, value)
        else:
            payload = struct.pack(">bih", block.value, address, value)

        send_frame = Frame(id_=0x0100 + self.can_bus_unit_id.value, data=payload, dlc=len(payload), flags=0)
        self._hw_interface_can_bus.write(send_frame)

    # @low_level_locked_can_bus_call
    @low_level_can_bus_call
    def read_block(self, block: Enum, address: int, length: int):
        # length of int16 samples
        super().read_block(block, address, length)
        if length % 4 != 0:
            length = (length // 4 + 1) * 4
        # payload = block.to_bytes(1, 'big') + address.to_bytes(4, 'big') + length.to_bytes(2, 'big')
        payload = struct.pack(">biH", block.value, address, length)
        send_frame = Frame(id_=0x0400 + self.can_bus_unit_id.value, data=payload, dlc=len(payload), flags=0)
        self._hw_interface_can_bus.write(send_frame)

        sleep_time = length * 8 * 10 / 1e6
        time.sleep(sleep_time)
        result = bytearray(length)
        read_count = 0
        while read_count < length*2:
            message = self._hw_interface_can_bus.read()
            if message.id == 0x0480 + self.can_bus_unit_id.value and message.dlc == 8:
                result[read_count:read_count+8] = message.data
                read_count += 8
            else:
                time.sleep(0.1)
        return np.frombuffer(bytes(result), dtype=np.dtype(np.int16).newbyteorder('<'))

    # @low_level_locked_can_bus_call
    @low_level_can_bus_call
    def write_block(self, block: Enum, address: int, block_data: np.ndarray):
        super().write_block(block, address, block_data)
        length = len(block_data)
        payload = struct.pack(">biH", block.value, address, length)
        send_frame = Frame(id_=0x0300 + self.can_bus_unit_id.value, data=payload, dlc=len(payload), flags=0)
        self._hw_interface_can_bus.write(send_frame)
        time.sleep(0.01)

        start_offset = 0
        while start_offset < length:
            data = block_data[start_offset:start_offset + 4]
            wr_data = np.array(data, '>i2')
            wr_data_bytes = wr_data.tobytes()
            # offsets for command are in int indexes
            send_frame = Frame(id_=0x0300 + self.can_bus_unit_id.value, data=wr_data_bytes, dlc=8, flags=0)
            self._hw_interface_can_bus.write(send_frame)
            start_offset += len(data)
            if start_offset % (64 * 8) == 0:
                time.sleep(0.05)

    # # @low_level_locked_can_bus_call
    # @low_level_can_bus_call
    # def read_block(self, block: Enum, address: int, length: int):
    #     # length of int16 samples
    #     super().read_block(block, address, length)
    #     if length % 4 != 0:
    #         length = (length // 4 + 1) * 4
    #
    #     read_count = 0
    #     offset = 0
    #     result = bytearray(length)
    #
    #     packetsize = 512
    #
    #     while read_count < length * 2:
    #         # send request:
    #         len2read = min(length - int(read_count / 2), packetsize)  # in 16bit words
    #         payload = struct.pack(">biH", block.value, address + offset, len2read)
    #         send_frame = Frame(id_=0x0400 + self.can_bus_unit_id.value, data=payload, dlc=len(payload), flags=0)
    #         self._hw_interface_can_bus.write(send_frame)
    #
    #         # wait for buffer to fill
    #         time.sleep(packetsize*10/1e6)
    #
    #         # read response
    #         read_count_inner = 0
    #         while read_count_inner < len2read * 2:
    #             message = self._hw_interface_can_bus.read()
    #             if message.id == 0x0480 + self.can_bus_unit_id.value and message.dlc == 8:
    #                 result[read_count:read_count + 8] = message.data
    #                 read_count_inner += 8
    #                 read_count += 8
    #             else:
    #                 time.sleep(0.05)
    #
    #         offset += len2read
    #
    #     return np.frombuffer(bytes(result), dtype=np.dtype(np.int16).newbyteorder('<'))
