
import time
import serial
import numpy as np
from Modules.LowLevel.LowLevelBase import *


class LowLevelSerial(LowLevelBase):
    def __init__(self):
        super().__init__()

    @low_level_locked_call
    def connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        super().connect(hw_interface_type, can_bus_unit_id)
        if self._hw_interface is not None:
            self._hw_interface.close()
        # self._hw_interface = serial.Serial(self.port, baudrate=self.baud_rate, timeout=0.050, inter_byte_timeout=0.01)
        self.is_dev_open = True

    @low_level_locked_call
    def disconnect(self):
        self.is_dev_open = False
        if self._hw_interface is not None:
            self._hw_interface.close()
        self._hw_interface = None
        super().disconnect()

    def get_response(self, expected_res: ExpResType, exp_len: int = 4):
        res = -1 if expected_res == ExpResType.Int else "-----"
        for retry in range(30):
            if self._hw_interface.in_waiting >= exp_len:
                break
            time.sleep(0.01)
        if self._hw_interface.in_waiting >= exp_len:
            response = self._hw_interface.read_line()
            resp_len = len(response)
            if response is not None and resp_len >= exp_len:
                res = self.process_line(response, expected_res)
            else:
                line = "get_response: timeout on read"
                raise NiArtException(line)
            # clear input rx
            in_wait = self._hw_interface.in_waiting
            if in_wait > 0:
                rem_chars = self._hw_interface.read(in_wait)
                if expected_res != ExpResType.Int:
                    logger.error(f"After rx resp, remaining {in_wait}: '{rem_chars}'")
        else:
            line = "get_response: timeout on read"
            raise NiArtException(line)
        return res

    def get_binary_blob(self, exp_len: int):
        for retry in range(1000):
            if self._hw_interface.in_waiting >= exp_len:
                break
            time.sleep(0.05)
        if self._hw_interface.in_waiting >= exp_len:
            response = self._hw_interface.read(exp_len)
            resp_len = len(response)
            if response is None or resp_len < exp_len:
                line = "get_response: timeout on read"
                raise NiArtException(line)
            else:
                if self._hw_interface.in_waiting > 0:
                    junk = self._hw_interface.read_all()
                    self.logger.warning(f"get_binary_blob got junk: '{junk}'")
        else:
            line = "get_response: timeout on read"
            raise NiArtException(line)
        return response

    def process_line(self, response: bytes, expected_res: ExpResType):
        try:
            response = response.decode('ascii')
            if response[-2:] == '\r\n':
                response = response[:-2]  # strip '\r\n'
            if self.is_verbose:
                self.logger.debug(f"Response: '{response}'")
            if expected_res == ExpResType.Int:
                res = int(response[0:4], 16)
            elif expected_res == ExpResType.Str:
                res = response
            else:
                raise(NiArtException(f"process_line: Wrong expected"))
        except Exception as e:
            line = f"process_line Exception: {str(e)}"
            self.logger.error(line)
            raise NiArtException(line)
        return res

    def send_command_and_get_response(self, command: str, expected_res: ExpResType):
        try:
            if self._hw_interface.in_waiting > 0:
                junk = self._hw_interface.read_all()
                self.logger.warning(f"send_command_and_get_response found data in serial, '{junk}'")
            self._hw_interface.write(command.encode('ascii'))
            res = self.get_response(expected_res)
            # if expected_res == ExpResType.Int:
            if self._hw_interface.in_waiting > 0:
                # ok_resp = self.get_response(ExpResType.Str)
                junk = self._hw_interface.read_all()
                self.logger.warning(f"send_command_and_get_response remain data, '{junk}'")
            time.sleep(0.01)
        except Exception as e:
            line = f"send_command_and_get_response Exception on cmd {command}: {str(e)}"
            self.logger.error(line)
            raise NiArtException(line)
        return res

    def send_command_and_binary_data(self, command: str, bin_data: bytes, expected_res: ExpResType):
        res = None
        try:
            if self._hw_interface.in_waiting > 0:
                junk = self._hw_interface.read_all()
                self.logger.warning(f"send_command_and_binary_data found data in serial, '{junk}'")
            self._hw_interface.write(command.encode('ascii'))
            self._hw_interface.write(bin_data)
        except Exception as e:
            line = f"send_command_and_get_response on {command} Exception: {str(e)}"
            self.logger.error(line)
            raise NiArtException(line)
        return res

    def send_command_and_read_binary_data(self, command: str, length: int):
        try:
            if self._hw_interface.in_waiting > 0:
                junk = self._hw_interface.read_all()
                self.logger.warning(f"send_command_and_read_binary_data found data in serial, '{junk}'")
            # res = self.send_command_and_get_response(command, ExpResType.Str)
            self._hw_interface.write(command.encode('ascii'))
            # res = self.get_response(ExpResType.Str)
            res = self.get_binary_blob(length)
        except Exception as e:
            line = f"send_command_and_read_binary_data Exception: {str(e)}"
            self.logger.error(line)
            raise NiArtException(line)
        return res

    @low_level_locked_call
    @low_level_call
    def read_reg(self, block: Enum, address: int, expected_res: ExpResType):
        command = f"r{block.value:02x},{address:05x},0000\r"
        res = self.send_command_and_get_response(command, expected_res)
        return res

    @low_level_locked_call
    @low_level_call
    def write_reg(self, block: Enum, address: int, value: int):
        command = f"w{block.value:02x},{address:05x},{value:04x}\r"
        res = self.send_command_and_get_response(command, ExpResType.Str)
        return 1 if str(res).find("OK") else 0

    @low_level_locked_call
    @low_level_call
    def write_block(self, block: Enum, address: int, block_data: np.ndarray):
        length = len(block_data)
        start_offset = 0
        while start_offset < length:
            data = block_data[start_offset:start_offset + 500]
            # data_endian = data.astype(dtype=np.dtype(block_data.dtype).newbyteorder('<'))
            # data_as_bytes = data_endian.tobytes()
            wr_data = np.array(data, '<i2')
            wr_data_bytes = wr_data.tobytes()

            # offsets for command are in int indexes
            command = f"u{block.value:02x},{address + start_offset:05x},{len(data):04x}\r"
            self.send_command_and_binary_data(command, wr_data_bytes, ExpResType.Str)
            start_offset += len(data)

    @low_level_locked_call
    @low_level_call
    def read_block(self, block: Enum, address: int, length: int):
        result_block = bytearray(length*2)
        start_offset = 0
        while start_offset < length:
            remain = length - start_offset
            read_count = min(500, remain)
            # offsets for command are in int indexes
            command = f"b{block.value:02x},{(address + start_offset):05x},{read_count:04x}\r"
            res = self.send_command_and_read_binary_data(command, read_count*2)
            result_block[start_offset*2:(start_offset+read_count)*2] = res
            start_offset += read_count
        result = np.frombuffer(result_block, dtype=np.dtype(np.int16).newbyteorder('<'))
        return result

