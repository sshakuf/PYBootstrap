import logging
from Modules.LowLevel import LowLevelBase, LowLevelI2C, LowLevelSerial
from Modules.LowLevel.LowLevelCanBus import LowLevelCanBus
from Modules.Helpers.Node import Node
from Modules.Helpers.TxParams import *
from Modules.Helpers.Enums.TxEnums import *
from tools.DataStore import *
from Modules.LowLevel import LowLevelBase, LowLevelCanBus, LowLevelI2C, LowLevelSerial
from Modules.Helpers.eNums import *
from Modules.Helpers.Constants import GlobalConstants


logger = logging.getLogger(__name__)


class TxNode(Node):
    def __init__(self):
        super().__init__()
        logger.debug("init")
        self.tx_param = TxLocalParams()
        self.status = TxStatus()
        self.version = NodeVersion()
        # Doron's part #
        self.radar_low_level: LowLevelBase = LowLevelCanBus()
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False

    def onBeforeInitialized(self):
        self.can_bus_id = BoardType.TX.value * 16 + int(self.id)
        self.prop_handler = {
            # "frequency": self.,
            # "new_dbf_ready": self.act_on_dbf,
            # "frame_len_usec": self.config_frame,
            # "number_of_beams:": self.act_on_num_beams,
            # "bandwidth": ,
            # "chirp_duration": self.func,
            # "decimation_ratio": self.act_on_decimation_ratio,
            # "debug_output_interface": self.,
            # "num_samples_out": self.config_decimator,
            # "num_adc_samples": self.act_on_adc_samples,
            # "data_out_type": self.act_on_data_out,
            # "run_mode": self.act_on_run_mode,
            # "beam_spacing": self.func,
            # "beam_stack_center": self.func,
            # "record_on":self.func,
        }

        return True

    def before_connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        self.hw_interface_type = hw_interface_type
        self.can_bus_unit_id = can_bus_unit_id
        if hw_interface_type == HWInterfaceType.CanBus:
            self.radar_low_level = LowLevelCanBus()
        elif hw_interface_type == HWInterfaceType.I2C:
            self.radar_low_level = LowLevelI2C.LowLevelI2C()
        elif hw_interface_type == HWInterfaceType.Serial:
            self.radar_low_level = LowLevelSerial.LowLevelSerial()
        self.radar_low_level.connect(self.hw_interface_type, self.can_bus_unit_id)

    def before_disconnect(self):
        self.radar_low_level.disconnect()
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False


    def onAfterInitialized(self):
        pass

    def onBeforeStart(self):
        return True

    def onAfterStart(self):
        pass

    def onBeforeRun(self):
        return True

    def onAfterRun(self):
        pass

    def onBeforeStop(self):
        return True

    def onAfterStop(self):
        pass

    def get_version(self):
        tx = self.radar_low_level
        fpga_version = tx.read_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.FpgaVersion.value, ExpResType.Int)
        board_type = tx.read_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.BoardType.value, ExpResType.Int)
        serial_num = tx.read_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.SerialNum.value, ExpResType.Int)

        primary_version = fpga_version // 256
        secondary_version = fpga_version % 256
        try:
            board_type_enum = BoardType(board_type)
        except IndexError:
            board_type_enum = BoardType.Undef
        result = {
            'tx_fpga_version': f"{primary_version:02x}.{secondary_version:02x}",
            'tx_board_type': board_type_enum.name,
            'tx_serial_num': f"{serial_num:05d}",
        }
        for key, val in result.items():
            # self.values[key][1] = val
            logger.debug(f"{key}: {val}")
        self.version.fpga_version = fpga_version
        self.version.board_type_enum = board_type_enum
        self.version.serial_num = serial_num
        return self.version

    def update_dac_bias(self):
        res = self.radar_low_level.read_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.CmdReg.value, ExpResType.Int)
        if res & TxCpuCmdRegBits.ConfigDone.value == 0:
            logger.debug("Set bias voltages")
            biases = (
                3050,   # multiplier Vg 1&2, -0.8V OK
                3000,   # LO Amp #2, max. Gain OK --> optimize 77GHz output
                3000,   # LO Amp #1, max. Gain OK --> output 10dBm with 5dBm input
                450,    # Multiplier Vg 3, -0.2V  OK
                2100,   # TX 1st driver, -2.0V max, -3.0V min, VCC nur 3.2V OK
                3500,   # TX Mixer G, -2.2V OK
                2900,   # TX Mixer GX, -2.0V OK
                1200,   # PA G3   % typisch: alle bei 1350
                1500,   # PA G2  -1.0V pinch off
                900,    # PA G1  60/120/240/300mA
                1300,   # PA G4
            )
            for index, bias in enumerate(biases):
                self.radar_low_level.write_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.DacBiasStart.value+index, bias)

            self.radar_low_level.write_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.CmdReg.value,
                                           TxCpuCmdRegBits.InitTxDac.value)

    def init_modulator(self, dac_i_offset: int = 2047, dac_q_offset: int = 2047):
        logger.debug("Init Tx modulator")
        # Switch modulator timing OFF
        self.radar_low_level.write_reg(TXBlock.TxModulator, TxModulatorBlockAddr.CmdReg.value,
                                       TxModulatorCmdRegBits.TurnOff.value)
        # set offset values (instead of setting the full memory to DC bias)
        self.radar_low_level.write_reg(TXBlock.TxModulator, TxModulatorBlockAddr.DacQOffset.value, dac_i_offset)
        self.radar_low_level.write_reg(TXBlock.TxModulator, TxModulatorBlockAddr.DacIOffset.value, dac_q_offset)

        # Switch modulator timing ON
        self.radar_low_level.write_reg(TXBlock.TxModulator, TxModulatorBlockAddr.CmdReg.value,
                                       TxModulatorCmdRegBits.ExtSync.value)

    def init_frame_generator(self):
        logger.debug("Init frame generator")
        # switch off frame generator
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.CmdReg.value,
                                       TxFrameGenCmdRegBits.TurnOff.value)
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SampleNumH.value, 0)
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SampleNumL.value, 17000)
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.FrameLenH.value, 0)
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.FrameLenL.value, 20000)

    def get_board_status(self):
        logger.debug("Get board status")
        fpga_temp = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.FPGATemp.value, ExpResType.Int)
        temp_sinsirion = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.TempSinsirion.value, ExpResType.Int) / 100
        humidity = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.Humidity.value, ExpResType.Int) / 100
        acc_x = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.AccX.value, ExpResType.Int) / 100
        acc_y = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.AccY.value, ExpResType.Int) / 100
        acc_z = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.AccZ.value, ExpResType.Int) / 100
        accelerometer = (acc_x, acc_y, acc_z)
        pout_val = self.radar_low_level.read_reg(
            TXBlock.CpuRegisters, TxCpuBlockAddr.OutPower.value, ExpResType.Int)
        result = {
            'tx_fpga_temp': fpga_temp, 'tx_temp_sinsirion': temp_sinsirion, 'tx_humidity': humidity,
            'tx_out_power': pout_val,
            'tx_AccelerometerX': accelerometer[0],
            'tx_AccelerometerY': accelerometer[1],
            'tx_AccelerometerZ': accelerometer[2],
        }
        for key, val in result.items():
            # self.values[key][1] = val
            logger.debug(f"{key}: {val}")

    def set_high_speed_debug_mem(self, test_data: np.dtype('complex')):
        tx = self.radar_low_level
        test_data_I = np.int16(test_data_I)
        test_data_Q = np.int16(test_data_Q)

        if len(test_data_I) > 8192:
            test_data_I = test_data_I[0:8192]
        if len(test_data_Q) > 8192:
            test_data_Q = test_data_Q[0:8192]

        tx.write_block(TXBlock.TxMipiBlock, TxMipiBlockAddr.SimMemBase_I.value, test_data_I)
        tx.write_block(TXBlock.TxMipiBlock, TxMipiBlockAddr.SimMemBase_Q.value, test_data_Q)

    def get_high_speed_debug_mem(self):
        tx = self.radar_low_level

        test_data_I = tx.read_block(TXBlock.TxMipiBlock, TxMipiBlockAddr.SimMemBase_I.value, 8192)
        test_data_Q = tx.read_block(TXBlock.TxMipiBlock, TxMipiBlockAddr.SimMemBase_Q.value, 8192)

        return test_data_I, test_data_Q

    def select_data_out(self, data_out: MipiDataOutType, frame_format: MipiDataFormat):
        val = (frame_format.value << TxMipiControlRegBits.MipiDataFormat) + data_out.value
        self.radar_low_level.write_reg(TXBlock.TxMipiBlock, TxMipiBlockAddr.ControlReg.value, val)

    def set_run_mode(self, run_mode: TxTriggerMode):
        super().set_run_mode(run_mode)
        self.radar_low_level.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.CmdReg.value, run_mode.value)
        # self.TxConfig.tx_TriggerMode = run_mode

    def config_frame(self, num_samples: int = None, frame_len: int = None, sync_delay: int = 0):
        logger.info(" Init Frame Generator")
        tx = self.radar_low_level

        # turn off frame generator
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.CmdReg.value, TxTriggerMode.Stop.value)

        # of samples
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SampleNumH.value,
                     num_samples // 65536)  # Upper 16bits
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SampleNumL.value,
                     num_samples & 65535)  # Lower 16bits

        # Frame Rep
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.FrameLenH.value,
                     frame_len // 65536)  # Upper 16bits
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.FrameLenL.value,
                     frame_len % 65535)  # Lower 16bits

        # Sync delay (cable length compensation)
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SyncDelayH.value,
                     sync_delay // 65536)  # Upper 16bits
        tx.write_reg(TXBlock.FrameGen, TxFrameGenBlockAddr.SyncDelayL.value,
                     sync_delay % 65535)  # Lower 16bits

    def read_status_reg(self):
        val = self.radar_low_level.read_reg(TXBlock.CpuRegisters, TxCpuBlockAddr.StatusReg.value, ExpResType.Int)
        print(f"Status reg: 0x{val:04x}")
        return val

    def modulator_bank_select(self, bank_id):
        self.radar_low_level.write_reg(TXBlock.TxModulator, TxModulatorBlockAddr.CmdReg.value,
                                       TxModulatorCmdRegBits.BankSelect.value * bank_id +
                                       TxModulatorCmdRegBits.ExtSync.value)

    def set_modulator(self, freq_MHz: float = 0, amp: float = 1, num_samples: int = 32768):
        logger.info("Init TX modulator memory")
        tx = self.radar_low_level

        if freq_MHz == 0:
            # set I and Q offset values
            self.init_modulator(dac_i_offset=2047, dac_q_offset=2047)
        else:
            tt = np.linspace(0, (num_samples - 1) / GlobalConstants.fs, num_samples)
            vect = amp * np.exp(-1j * 2.0 * np.pi * freq_MHz * 1e6 * tt)

            act_len = len(vect)
            real_vect = vect.real
            imag_vect = vect.imag
            real_vect = real_vect * 2047.0
            imag_vect = imag_vect * 2047.0

            upload_data = np.zeros([8192 * 2, ], dtype=np.int16)
            bank_id = 0

            remaining = act_len
            offset = 0
            while remaining > 0:
                self.modulator_bank_select(bank_id)
                upload_data[0::2, ] = np.floor(real_vect[offset:offset+8192])
                upload_data[1::2, ] = np.floor(imag_vect[offset:offset+8192])
                tx.write_block(TXBlock.TxModulator, TxModulatorBlockAddr.ModuISampPntStart.value, upload_data)
                offset += 8192
                bank_id += 1
                remaining -= 8192
