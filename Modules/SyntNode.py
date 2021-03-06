import logging
from Modules.Helpers.Node import Node
from Modules.Helpers.TxParams import *
from Modules.Helpers.Constants import *
from Modules.Helpers.Enums.SyntEnums import *
from tools.DataStore import *
from Modules.Helpers.SyntParams import *
from Modules.LowLevel import LowLevelBase, LowLevelCanBus, LowLevelI2C, LowLevelSerial
from Modules.LowLevel.LowLevelCanBus import *

logger = logging.getLogger(__name__)


class SyntNode(Node):
    def __init__(self):
        super().__init__()
        logger.debug("init")
        self.local_params = SyntLocalParam()
        self.status = SyntStatus()
        self.version = NodeVersion()

        # Doron's part #
        self.radar_low_level: LowLevelBase = LowLevelCanBus()

    def onBeforeInitialized(self):
        logger.info("SyntNode initializing")
        self.radar_low_level.init(self.is_verbose)
        self.can_bus_id = BoardType.Synt.value * 16 + 0
        self.engine.eventBroker.subscribeEvent("PropertyChanged", self.property_changed)
        # self.engine.eventBroker.subscribeEvent("PropertyBeforeChange", self.property_before_changed)
        return True

    def property_changed(self, prop):
        try:
            func = self.prop_handler[prop["Name"]]
            # print(func)
            func()
        except:
            logger.error("Synt: Property %s is not supported or failed to set." % prop["Name"])

    def onAfterInitialized(self):
        self.prop_handler = {
            "frequency": self.config_chirp,
            # "new_dbf_ready": self.act_on_dbf,
            "frame_len_usec": self.config_frame,
            "number_of_beams:": self.set_mipi_num_beams,
            "bandwidth": self.config_chirp,
            "chirp_duration": self.config_chirp,
            # "decimation_ratio": self.act_on_decimation_ratio,
            # "debug_output_interface": self.,
            # "num_samples_out": self.config_decimator,
            "num_adc_samples": self.config_frame,
            # "data_out_type": self.act_on_data_out,
            # "run_mode": self.act_on_run_mode,
            # "beam_spacing": self.func,
            # "beam_stack_center": self.func,
            # "record_on":self.func,
        }
        pass

    def onBeforeStart(self):
        self.connect(self.global_params.hw_interface_type, self.can_bus_id)
        self.get_version()
        self.get_board_status()
        self.init_hw()
        self.config_frame()
        self.config_chirp()
        self.set_mipi_num_beams()
        self.set_run_mode()
        self.set_init_flag()
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

    def before_connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        self.hw_interface_type = hw_interface_type
        self.can_bus_unit_id = can_bus_unit_id
        logger.info(f"RxBase.init port: interface: {hw_interface_type}")
        self.is_connected = True
        logger.info("=============== Connected ==============")
        if hw_interface_type == HWInterfaceType.CanBus:
            self.radar_low_level = LowLevelCanBus()
        elif hw_interface_type == HWInterfaceType.I2C:
            self.radar_low_level = LowLevelI2C.LowLevelI2C()
        elif hw_interface_type == HWInterfaceType.Serial:
            self.radar_low_level = LowLevelSerial.LowLevelSerial()
        self.radar_low_level.connect(self.hw_interface_type, self.can_bus_unit_id)


    def get_version(self):
        synt = self.radar_low_level
        fpga_version = synt.read_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.FpgaVersion.value, ExpResType.Int)
        board_type = synt.read_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.BoardType.value, ExpResType.Int)
        serial_num = synt.read_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.SerialNum.value, ExpResType.Int)

        primary_version = fpga_version // 256
        secondary_version = fpga_version % 256
        try:
            board_type_enum = BoardType(board_type)
        except IndexError:
            board_type_enum = BoardType.Undef
        result = {
            'synt_fpga_version': f"{primary_version:02x}.{secondary_version:02x}",
            'synt_board_type': board_type_enum.name,
            'synt_serial_num': f"{serial_num:05d}",
        }
        for key, val in result.items():
            # self.values[key][1] = val
            logger.debug(f"{key}: {val}")

        self.version.fpga_version = fpga_version
        self.version.serial_num = serial_num
        self.version.board_type_enum = board_type_enum
        return self.version

    def get_board_status(self):
        logger.debug("Get board status")
        fpga_temp = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.FPGATemp.value, ExpResType.Int)
        temp_sinsirion = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.TempSinsirion.value, ExpResType.Int) / 100
        humidity = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.Humidity.value, ExpResType.Int) / 100
        acc_x = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.AccX.value, ExpResType.Int) / 100
        acc_y = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.AccY.value, ExpResType.Int) / 100
        acc_z = self.radar_low_level.read_reg(
            SyntBlock.CpuRegisters, SyntCpuBlockAddr.AccZ.value, ExpResType.Int) / 100
        accelerometer = (acc_x, acc_y, acc_z)

        result = {
            'synt_fpga_temp': fpga_temp, 'synt_board_temp': temp_sinsirion, 'synt_humidity': humidity,
            'synt_AccelerometerX': accelerometer[0],
            'synt_AccelerometerY': accelerometer[1],
            'synt_AccelerometerZ': accelerometer[2],
        }
        for key, val in result.items():
            # self.values[key][1] = val
            logger.debug(f"{key}: {val}")

    def config_chirp(self, start_freq: float = None, bandwidth: float = None,
                     sweep_time: float = None, ramp_type: RampType = None):
        # Start frequency is in MHz
        start_freq = start_freq if start_freq is not None else self.global_props.frequency
        sweep_time = sweep_time if sweep_time is not None else self.global_props.chirp_duration  # sweep time is in usec
        bandwidth = bandwidth if bandwidth is not None else self.global_props.bandwidth  # bandwidth is in MHz (in E-band)
        ramp_type = ramp_type if ramp_type is not None else self.global_params.ramp_type
        if start_freq < 76000 or start_freq > 78000:
            start_freq = None
            print("Invalid start frequency!")
        if bandwidth < 0 or bandwidth > 1000:
            bandwidth = None
            print("Invalid bandwidth!")

        # super().config_chirp(start_freq, bandwidth, sweep_time)
        logger.info(" Init PLL")
        synt = self.radar_low_level
        f_start_H = np.int16(start_freq // 65536)
        f_start_L = np.int16(start_freq % 65536)

        bandwidth_H = np.int16(bandwidth / 65536)
        bandwidth_L = np.int16(bandwidth % 65536)

        sweep_steps_H = np.int16((sweep_time / 0.1) // 65536)
        sweep_steps_L = np.int16((sweep_time / 0.1) % 65536)

        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.StartFreq_H.value, f_start_H)
        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.StartFreq_L.value, f_start_L)

        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.Bandwidth_H.value, bandwidth_H)
        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.Bandwidth_L.value, bandwidth_L)

        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.SweepTime_H.value, sweep_steps_H)
        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.SweepTime_L.value, sweep_steps_L)

        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.RampConfig.value, ramp_type.value)   # set ramp type

        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.ControlReg.value, 1)   # init PLL cmd

    def config_frame(self, num_samples: int = None, frame_len_usec: int = None, sync_delay: int = None):
        num_samples = num_samples if num_samples is not None else self.global_props.num_adc_samples
        frame_len_usec = frame_len_usec if frame_len_usec is not None else self.global_props.frame_len_usec
        frame_len = frame_len_usec * 50 - 1
        logger.info(" Init Frame Generator")

        synt = self.radar_low_level

        # turn off frame generator
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.ControlReg.value, 0)

        # Number of samples
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.SampleNumH.value, num_samples // 65536)  # Upper 16b
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.SampleNumL.value, num_samples & 65535)  # Lower 16b

        # Frame Rep
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.FrameLenH.value, frame_len // 65536)  # Upper 16bits
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.FrameLenL.value, frame_len % 65535)  # Lower 16bits

        # set run mode
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.ControlReg.value, self.global_props.run_mode.value)

    def set_init_flag(self, flag_val: bool = True):
        logger.info(f"Set INIT flag to {flag_val}")
        synt = self.radar_low_level
        synt.write_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.ControlReg.value, 128 if flag_val else 0)

    def get_init_flag(self):
        synt = self.radar_low_level
        flag_val = synt.read_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.ControlReg.value, ExpResType.Int)
        logger.info(f"INIT flag is {flag_val}")
        return flag_val

    def set_high_speed_debug_mem(self, test_data: np.dtype('complex')):
        synt = self.radar_low_level
        test_data_I = np.zeros([8192, ], dtype='int16')
        test_data_Q = np.zeros([8192, ], dtype='int16')

        if len(test_data) > 8192:
            test_data = test_data[0:8192]

        test_data_I[0:len(test_data)] = np.int16(np.real(test_data))
        test_data_Q[0:len(test_data)] = np.int16(np.imag(test_data))
        synt.write_block(SyntBlock.MIPI_RAM, SyntMipiRamBlockAddr.Sim_RAM_I_base_addr.value, test_data_I)
        synt.write_block(SyntBlock.MIPI_RAM, SyntMipiRamBlockAddr.Sim_RAM_Q_base_addr.value, test_data_Q)

    def get_high_speed_debug_mem(self):
        level = self.radar_low_level
        synt = level

        test_data_I = synt.read_block(SyntBlock.MIPI_RAM, SyntMipiRamBlockAddr.Sim_RAM_I_base_addr.value, 8192)
        test_data_Q = synt.read_block(SyntBlock.MIPI_RAM, SyntMipiRamBlockAddr.Sim_RAM_Q_base_addr.value, 8192)

        data_complex = test_data_I + 1j*test_data_Q
        return data_complex

    def set_run_mode(self, run_mode: SyntRunMode = None):
        run_mode = run_mode if run_mode is not None else self.global_props.run_mode
        self.radar_low_level.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.ControlReg.value, run_mode.value)

    def trigger_single_frame(self):
        synt = self.radar_low_level
        synt.write_reg(SyntBlock.FrameGen, SyntFrameGenBlockAddr.ControlReg.value, 1)

    def read_status_reg(self):
        val = self.radar_low_level.read_reg(SyntBlock.CpuRegisters, SyntCpuBlockAddr.StatusReg.value, ExpResType.Int)
        print(f"Status reg: 0x{val:04x}")
        return val

    def set_mipi_frame_format(self, frame_format: MipiDataFormat = MipiDataFormat.FMT_8192_32):
        synt = self.radar_low_level
        synt.write_reg(SyntBlock.MIPI_RAM, SyntMipiRamBlockAddr.ControlReg.value, frame_format.value)

    def set_mipi_num_beams(self, num_beams=None):
        num_beams = num_beams if num_beams is not None else self.global_props.number_of_beams
        if num_beams == 8:
            self.set_mipi_frame_format(MipiDataFormat.FMT_8192_32)
        elif num_beams == 16:
            self.set_mipi_frame_format(MipiDataFormat.FMT_8192_64)
        elif num_beams == 32:
            self.set_mipi_frame_format(MipiDataFormat.FMT_8192_128)
        elif num_beams == 64:
            self.set_mipi_frame_format(MipiDataFormat.FMT_8192_256)
        else:
            self.set_mipi_frame_format(MipiDataFormat.FMT_8192_32)
            print("Number of beams should be 8/16/32/64!")

    def reset_serdes(self):
        self.radar_low_level.write_reg(SyntBlock.CpuRegisters,SyntCpuBlockAddr.ControlReg.value,
                                       1 << SyntCpuCmdRegBits.ResetTRX.value)

    def set_gpio_LED(self, function: LedFunction = 0):
        self.radar_low_level.write_reg(SyntBlock.CpuRegisters,SyntCpuBlockAddr.LedFunction.value,function.value)