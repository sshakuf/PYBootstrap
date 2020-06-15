import struct
import sys
import time

if sys.platform == 'linux':
    from smbus2 import SMBus, i2c_msg
from Modules.Helpers.eNums import *
from Modules.LowLevel.LowLevelBase import *


def low_level_locked_i2c_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface_i2c is None or not self.is_dev_i2c_open:
            raise NiArtException(f"LowLevel hw_interface is not open")
        else:
            try:
                self._hw_interface_i2c_lock.acquire()
                res = function(self, *args, **kwargs)
                self._hw_interface_i2c_lock.release()
            except Exception as e:
                line = f"LowLevel hw_interface exception: {str(e)}"
                self.logger.error(line)
                raise NiArtException(line)
            return res

    return wrapper


def low_level_i2c_call(function):
    def wrapper(self, *args, **kwargs):
        if self._hw_interface_i2c is None or not self.is_dev_i2c_open:
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


class LowLevelI2C(LowLevelBase):
    if sys.platform != 'linux':
        print("Cannot use I2C interface under Windows")
        # raise NiArtException("Cannot use I2C interface under Windows")
    _hw_interface_i2c = None
    _hw_interface_i2c_lock: threading.Lock = threading.Lock()
    _using_count = 0

    @classmethod
    def connect_i2c(cls):
        # Open I2C channel #2
        usb_port = 0
        if cls._hw_interface_i2c is None:
            cls._hw_interface_i2c = SMBus(2)
            logger.debug("Going on I2C bus\n\n")
            # cls._hw_interface_i2c.busOn()
            cls._using_count += 1

    @classmethod
    def disconnect_i2c(cls):
        if cls._hw_interface_i2c is not None:
            if cls._using_count <= 1:
                cls._hw_interface_i2c.close()
                cls._hw_interface_i2c = None
                cls._using_count = 1
        cls._using_count -= 1

    def __init__(self):
        super().__init__()
        self.is_dev_i2c_open = False
        self.I2C_base_address = 0x21  # constant I2C bus address

    # @low_level_locked_i2c_call
    def connect(self, hw_interface_type: HWInterfaceType, i2c_unit_id: CanBusUnitID):
        super().connect(hw_interface_type, i2c_unit_id)
        logger.debug(f"Opening I2C channel")
        self.connect_i2c()
        self.is_dev_i2c_open = True

    # @low_level_locked_i2c_call
    def disconnect(self):
        self.is_dev_i2c_open = False
        self.disconnect_i2c()
        self._hw_interface_i2c = None
        super().disconnect()

    # @low_level_locked_i2c_call
    @low_level_i2c_call
    def read_reg(self, block: Enum, address: int, expected_res: ExpResType):
        super().read_reg(block, address, expected_res)
        payload = struct.pack(">bi", block.value, address)
        unit_id = 0x0200 + self.can_bus_unit_id.value  # i2c_unit_id is identical to can_bus_unit_id
        unit_id_h = (unit_id & 0xff00) >> 8
        unit_id_l = (unit_id & 0xff)
        dlc = 5
        send_frame = bytes([0x00, unit_id_h, unit_id_l, dlc]) + payload + bytes([0, 0, 0, 0, 0])
        send_frame_reset = bytes([0x00, unit_id_h, unit_id_l, dlc]) + payload + bytes([0, 0, 0, 0, 255])
        self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame)
        time.sleep(0.01)
        res = -1
        for retry in range(5):
            try:
                response = self._hw_interface_i2c.read_i2c_block_data(self.I2C_base_address, 0, 32)
                len = 256 * response[16] + response[17]
                if len == 2:
                    res = int(response[18]) << 8 | int(response[19])
                    break
                else:
                    time.sleep(0.01)
                    self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame_reset)

            except Exception as ex:
                res = -1
                time.sleep(0.01)
        return np.int16(res)

    # @low_level_locked_i2c_call
    @low_level_i2c_call
    def write_reg(self, block: Enum, address: int, value: int):
        super().write_reg(block, address, value)
        if value > 32767:
            payload = struct.pack(">biH", block.value, address, value)
        else:
            payload = struct.pack(">bih", block.value, address, value)

        unit_id = 0x0100 + self.can_bus_unit_id.value  # i2c_unit_id is identical to can_bus_unit_id
        unit_id_h = (unit_id & 0xff00) >> 8
        unit_id_l = (unit_id & 0xff)
        dlc = 7
        send_frame = bytes([0x00, unit_id_h, unit_id_l, dlc]) + payload + bytes([0x00, 0x00, 0x00])  # 14 bytes
        self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame)

    # @low_level_locked_i2c_call
    @low_level_i2c_call  # works fine. compared with Octave results
    def read_block(self, block: Enum, address: int, length: int):
        # length of int16 samples
        super().read_block(block, address, length)
        if length % 4 != 0:
            length = (length // 4 + 1) * 4

        packet_len = 256
        out = np.zeros([length, ], dtype=np.int16)
        unit_id = 0x0400 + self.can_bus_unit_id.value  # i2c_unit_id is identical to can_bus_unit_id
        unit_id_h = (unit_id & 0xff00) >> 8
        unit_id_l = (unit_id & 0xff)
        dlc = 7

        offset = 0
        remaining = length
        while remaining > 0:
            if remaining > packet_len:
                words2read = packet_len
            else:
                words2read = remaining

            payload = struct.pack(">bih", block.value, address + offset, words2read)
            send_frame = bytes([0x00, unit_id_h, unit_id_l, dlc]) + payload + bytes([0x00, 0x00, 0x00])  # 14 bytes
            self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame)

            time.sleep(0.01)
            msg = i2c_msg.read(self.I2C_base_address, 6 + words2read * 2)
            self._hw_interface_i2c.i2c_rdwr(msg)

            data16 = np.frombuffer(bytes(msg)[6:], dtype=np.dtype(np.int16).newbyteorder('<'))
            out[offset:offset+words2read] = data16
            offset += words2read
            remaining -= words2read

        return out

    # @low_level_locked_i2c_call
    @low_level_i2c_call
    def write_block(self, block: Enum, address: int, block_data: np.ndarray):
        super().write_block(block, address, block_data)
        length = len(block_data)
        unit_id = 0x0300 + self.can_bus_unit_id.value  # i2c_unit_id is identical to can_bus_unit_id
        unit_id_h = (unit_id & 0xff00) >> 8
        unit_id_l = (unit_id & 0xff)
        dlc = 7
        if length > 32767:
            payload = struct.pack(">biH", block.value, address, length)
        else:
            payload = struct.pack(">bih", block.value, address, length)

        send_frame = bytes([0x00, unit_id_h, unit_id_l, dlc]) + payload + bytes([0x00, 0x00, 0x00])  # 14 bytes
        self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame)
        time.sleep(0.01)

        start_offset = 0
        while start_offset < length:
            msg_rd = self._hw_interface_i2c.read_i2c_block_data(self.I2C_base_address, 0, 12)
            while msg_rd[11] == 0:
                # time.sleep(0.01)
                msg_rd = self._hw_interface_i2c.read_i2c_block_data(self.I2C_base_address, 0, 12)

            data = block_data[start_offset:start_offset + 4]
            wr_data = np.array(data, '>i2')
            wr_data_bytes = wr_data.tobytes()
            # offsets for command are in int indexes
            dlc = 8
            send_frame = bytes([0x00, unit_id_h, unit_id_l, dlc]) + wr_data_bytes + bytes([0x00, 0x00])  # 14 bytes
            self._hw_interface_i2c.write_i2c_block_data(self.I2C_base_address, 0, send_frame)
            start_offset += len(data)
            # if start_offset % (64 * 8) == 0:
            #     time.sleep(0.05)

