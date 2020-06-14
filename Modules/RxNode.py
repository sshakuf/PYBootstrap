from tools import EventBroker
from tools import EngineComponent
import time
from Modules.Helpers.Node import Node
from Modules.Helpers.RxParams import *
from Modules.Helpers.eNums import *
import logging
from tools.DataStore import RxStatus
from Modules.LowLevel import LowLevelBase, LowLevelCanBus, LowLevelI2C, LowLevelSerial
from tools.DataStore import NodeVersion
from Modules.Helpers.Enums.RxEnums import *
import numpy as np
from tools.EventBroker import *

logger = logging.getLogger(__name__)


# RxNode now has functionality of Doron's RxMidLevelBase and RxMidLevel.


class RxNode(Node):
    def __init__(self):
        super().__init__()
        logger.debug("init")
        self.rx_param = RxLocalParams()
        self.status = RxStatus()
        self.version = NodeVersion()
        # Doron's part #
        self.radar_low_level: LowLevelBase = LowLevelCanBus.LowLevelCanBus()
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False

    def frequency_change(self):
        print("do something")
        print("call other function")
        print("call other function2")

    def onBeforeInitialized(self):
        logger.info("RxNode initializing")
        # self.engine.eventBroker.subscribeEvent("changed_freq", self.frequency_change)
        self.engine.eventBroker.subscribeEvent("PropertyBeforeChange", self.prop_changed)
        return True

    def prop_changed(self, prop):
        if prop["Name"] == "freq":
            print("Freq changed, doing something from rx" + str(self.id))

    def onAfterInitialized(self):
        logger.info("RxNode initialized")
        # pass

    def onBeforeStart(self):
        return True

    def onAfterStart(self):
        pass

    def onBeforeRun(self):
        # if self.id == 1:
        #     print("AHHHH LOOK AT ME IM MISTER MISIX!")
        # if self.id == 2:
        #     print("RX ID 2 IS DOING ANOTHER THINGS IN ADDITION!")
        # print("FREQUENCY FROM RX ID: " + str(self.id) + " IS: " + str(self.engine.props.frequency))
        return True

    def onAfterRun(self):
        pass

    def onBeforeStop(self):
        return True

    def onAfterStop(self):
        pass

    def get_version(self, fpga_version=None, board_type=None, serial_num=None):
        rx = self.radar_low_level
        fpga_version = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.FpgaVersion.value, ExpResType.Int)
        board_type = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.BoardType.value, ExpResType.Int)
        serial_num = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.SerialNum.value, ExpResType.Int)

        primary_version = fpga_version // 256
        secondary_version = fpga_version % 256
        try:
            board_type_enum = BoardType(board_type)
        except IndexError:
            board_type_enum = BoardType.Undef

        result = {
            'rx_fpga_version': f"{primary_version:02x}.{secondary_version:02x}",
            'rx_board_type': board_type_enum.name,
            'rx_serial_num': f"{serial_num:05d}",
        }
        for key, val in result.items():
            # self._set_val(key, val)  # ?
            logger.info(f"{key}: {val}")

        self.version.fpga_version = fpga_version
        self.version.board_type_enum = board_type_enum
        self.version.serial_num = serial_num
        return self.version

    def before_disconnect(self):
        self.radar_low_level.disconnect()
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False

    def before_connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        self.hw_interface_type = hw_interface_type
        self.can_bus_unit_id = can_bus_unit_id
        logger.info(f"RxBase.init port: interface: {hw_interface_type}")
        self.is_connected = True
        logger.info("=============== Connected ==============")
        if hw_interface_type == HWInterfaceType.CanBus:
            self.radar_low_level = LowLevelCanBus.LowLevelCanBus()
        elif hw_interface_type == HWInterfaceType.I2C:
            self.radar_low_level = LowLevelI2C.LowLevelI2C()
        elif hw_interface_type == HWInterfaceType.Serial:
            self.radar_low_level = LowLevelSerial.LowLevelSerial()
        self.radar_low_level.connect(self.hw_interface_type, self.can_bus_unit_id)

    def get_board_status(self):
        rx = self.radar_low_level
        # Read Rx chips (MR2001) temperatures
        n_rx_chips = 16
        for i in range(n_rx_chips):
            self.status.temperature[i] = \
                rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.RxChipsTempBlockStart.value + i, ExpResType.Int) / 10.0

            self.status.lo_power[i] = val = \
                rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.RxLoSensBlockStart.value + i, ExpResType.Int)

            # RxLoInd[i] = 1.0 if val > 300 else 0.0

        self.status.fpga_temp = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.FpgaTemp.value, ExpResType.Int)
        self.status.board_temp = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.BoardTemp.value, ExpResType.Int) / 100.0
        self.status.board_humidity = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.BoardHumid.value, ExpResType.Int) / 100.0
        RxSat = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.RxSat.value, ExpResType.Int)
        for _ in range(0, n_rx_chips):
            self.status.saturation[_] = 1 if (RxSat & (1 << _)) else 0

        self.status.accelerometer[0] = self.radar_low_level.read_reg(
            RXBlock.CpuRegisters, RxCpuBlockAddr.AccX.value, ExpResType.Int) / 100
        self.status.accelerometer[1] = self.radar_low_level.read_reg(
            RXBlock.CpuRegisters, RxCpuBlockAddr.AccY.value, ExpResType.Int) / 100
        self.status.accelerometer[2] = self.radar_low_level.read_reg(
            RXBlock.CpuRegisters, RxCpuBlockAddr.AccZ.value, ExpResType.Int) / 100

        if self.is_verbose:
            line = f"FPGA Temp: {self.status.fpga_temp:5.1f}.\nRx temp: {self.status.temperature}\n"
            logger.info(line)
            line = f"Board temp: {self.status.board_temp:5.1f} C. Board Humidity: {self.status.board_humidity} %\n"
            logger.info(line)
            line = f"Rx Accelerometer: ({self.status.accelerometer:})"
            logger.info(line)
        return self.status

    def read_status_reg(self):
        val = self.radar_low_level.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.StatusReg.value, ExpResType.Int)
        self.status.int_clk = 1 if (val & (RxCpuStatusReg.IntClk.value)) else 0
        self.status.sweep_active = 1 if (val & (RxCpuStatusReg.SweepActive.value)) else 0
        self.status.sampling_clk_inverted = 1 if(val & RxCpuStatusReg.SamplingClkInv) else 0
        self.status.vss_pg = 1 if(val & RxCpuStatusReg.VssPG) else 0
        self.status.v_out_npg = 1 if (val & RxCpuStatusReg.Vout_nPG) else 0
        self.status.stage_3_pg = 1 if (val & RxCpuStatusReg.Vstage3_PG) else 0
        print(f"Status reg: 0x{val:04x}")
        return self.status

    #################################

    # This func needs to be subscribed to eventBroker to beam event.
    # @RegisterListener("beam_for_debug")
    def select_beam_for_debug(self, beam: int = 0):
        rx = self.radar_low_level
        beam = 0 if beam < 0 or beam >= 64 else beam
        rx.write_reg(RXBlock.BeamFormer, RxBeamFormerBlockAddr.BeamSelector.value, beam)

    def set_high_speed_debug_mem(self, test_data: np.dtype('complex')):
        rx = self.radar_low_level
        test_data_I = np.zeros([8192, ], dtype='int16')
        test_data_Q = np.zeros([8192, ], dtype='int16')

        if len(test_data) > 8192:
            test_data = test_data[0:8192]

        test_data_I[0:] = np.int16(np.real(test_data))
        test_data_Q[0:] = np.int16(np.imag(test_data))
        rx.write_block(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.SimMemBase_I.value, test_data_I)
        rx.write_block(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.SimMemBase_Q.value, test_data_Q)

    def get_high_speed_debug_mem(self):
        rx = self.radar_low_level
        test_data_I = np.zeros([8192, ], dtype='int16')
        test_data_Q = np.zeros([8192, ], dtype='int16')

        test_data_I[0:] = rx.read_block(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.SimMemBase_I.value, 8192)
        test_data_Q[0:] = rx.read_block(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.SimMemBase_Q.value, 8192)

        data_complex = test_data_I + 1j * test_data_Q
        return data_complex

    def set_run_mode(self, run_mode: RxTriggerMode):
        # super().set_run_mode(run_mode)
        self.radar_low_level.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.ControlReg.value, run_mode.value)
        self.rx_param.rx_TriggerMode = run_mode

    def select_data_out(self, data_out: DataOutType, num_beams = 8):
        val = data_out.value
        if num_beams == 16:
            val += (MipiDataFormat.FMT_8192_64.value << RxMipiControlRegBits.MipiDataFormat)
        elif num_beams == 32:
            val += (MipiDataFormat.FMT_8192_128.value << RxMipiControlRegBits.MipiDataFormat)
        elif num_beams == 64:
            val += (MipiDataFormat.FMT_8192_256.value << RxMipiControlRegBits.MipiDataFormat)
        else:
            val += (MipiDataFormat.FMT_8192_32.value << RxMipiControlRegBits.MipiDataFormat)

        # self.radar_low_level.write_reg(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.ControlReg.value, data_out.value)
        self.radar_low_level.write_reg(RXBlock.MipiDebugMem, RxMipiDebugMemBlockAddr.ControlReg.value, val)
        if data_out == DataOutType.DebugMemData:
            self.set_run_mode(RxTriggerMode.ExternalDebug)

    def set_init_flag(self, flag_val: bool):
        # super().set_init_flag(flag_val)
        logger.info(f"Set INIT flag to {flag_val}")
        rx = self.radar_low_level
        rx.modify_cpu_control_reg(RxCpuControlReg.SetGetConfigDone.value if flag_val else RxCpuControlReg.Nothing.value)

    def get_init_flag(self):
        # super().get_init_flag()
        rx = self.radar_low_level
        flag_val = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.ControlReg.value, ExpResType.Int)
        logger.info(f"INIT flag is {flag_val}")
        return flag_val

    def set_adc_clk_phase(self, adc_id: int = 3, offset: int = 7):  # A/D id is 0:5
        # super().set_adc_clk_phase(adc_id, offset)
        rx = self.radar_low_level
        rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.AdcChipPhaseAdjBlockStart.value + adc_id, offset)
        rx.modify_cpu_control_reg(RxCpuControlReg.InitADC.value)

    def set_adc_channel_offset(self, ch_id: int = 0, offset: int = 0):
        logger.debug("Set ADC offset")
        rx = self.radar_low_level
        rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.AdcOffsetBlockStart.value + ch_id, offset)
        rx.modify_cpu_control_reg(RxCpuControlReg.UpdateBiasDAC.value)

    def init_hw(self):
        ver = 6
        # super().init_hw()
        logger.info(" ************** Init HW **************\r")
        rx = self.radar_low_level
        InitFlag = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.ControlReg.value, ExpResType.Int)
        if (InitFlag & RxCpuControlReg.SetGetConfigDone.value) != 0:
            logger.debug(" ************** HW already Initialized**************")
            return
        logger.debug("Configure Bias DACs")
        biases = (
            0,  # 10GHz LO Amplifier max gain (approx. 8dB, Pin=5dBm)
            1825,  # 40GHz Multiplier, Bias 1&2, typ. -0.8V
            460,  # 40GHz Multiplier, Bias 3, typ. -0.2V
            3500,  # 80GHz Testsignal Amplifier
            3520,  # 80GHz Testsignal Doubler Bias
            2780,  # 80GHz Testsignal Mixer Bias
            2000,  # 40GHz LO Amplifier Bias, Id=280mA (1750 originally)
            3000,  # 80GHz LNA Gain   %3000
        )
        for i, val in enumerate(biases):
            rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.DacBiasBlockStart.value + i, val)
        rx.modify_cpu_control_reg(RxCpuControlReg.UpdateBiasDAC.value)

        logger.debug("Configure ADC mode")
        rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.AdcTestMode.value, 5 * 16 + 0)

        if ver < 6:
            logger.debug("Configure ADC offsets")
            offsets = (
                14, 29, 11, 19, 33, 18, 33, 20,  # 00 - 07
                13, 17, 28, 33, 16, 20, 1, 26,  # 08 - 15
                17, -9, 17, 17, 19, 17, 25, 13,  # 16 - 23
                8, 21, 18, 20, 14, 25, 28, 10,  # 24 - 31
                34, 15, 23, 33, 18, 7, 19, 31,  # 32 - 39
                17, 21, 14, 28, 18, 1, 10, 19)  # 40 - 47

            for i, val in enumerate(offsets):
                rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.AdcOffsetBlockStart.value + i, val)

            logger.debug("Adjust ADC chip phase")
            phase_adjusts = (
                7, 7, 7, 7, 7, 7)  # ADC #3 (0,1,2,3) should have phase offset 7, to avoid glitches

            for i, val in enumerate(phase_adjusts):
                rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.AdcChipPhaseAdjBlockStart.value + i, val)

        rx.modify_cpu_control_reg(RxCpuControlReg.InitADC.value)

        logger.debug("Configure receiver")
        val = 128 + 2  # Gain: 8dB, Activate RX (0= -2dB, 1= 4dB, 2 = 8dB,  = 16dB, 4 = 24dB)
        rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.RxConfiguration.value, val)
        rx.modify_cpu_control_reg(RxCpuControlReg.InitRX_Chips.value)

        logger.debug(" **************Finished HW Init**************")

    def config_fir(self, fir_index: int = None):
        fir_index = fir_index if fir_index is not None else self.rx_param.rx_FIR_Index
        # super().config_fir(fir_index)
        filt_bank = [
            [256, -228, 328, -455, 617, -823, 1090, -1443, 1934, -2674, 3949, -6818, 20815, 20815, -6818, 3949, -2674,
             1934, -1443, 1090, -823, 617, -455, 328, -228, 256, 0, 0],
            [29, 661, 1369, 1054, -427, -1184, 193, 1726, 306, -2745, -1691, 5807, 13644, 13644, 5807, -1691, -2745,
             306, 1726, 193, -1184, -427, 1054, 1369, 661, 29, 0, 0],
            [377, 407, 333, -40, -682, -1382, -1788, -1530, -393, 1540, 3865, 5959, 7200, 7200, 5959, 3865, 1540, -393,
             -1530, -1788, -1382, -682, -40, 333, 407, 377, 0, 0],
            [-1710, -455, -379, -194, 103, 507, 992, 1528, 2072, 2582, 3012, 3322, 3486, 3486, 3322, 3012, 2582, 2072,
             1528, 992, 507, 103, -194, -379, -455, -1710, 0, 0],
            [-408, 2256, 1069, 983, 1077, 1195, 1310, 1417, 1511, 1589, 1649, 1690, 1711, 1711, 1690, 1649, 1589, 1511,
             1417, 1310, 1195, 1077, 983, 1069, 2256, -408, 0, 0],
            [6112, 653, 681, 712, 735, 763, 783, 799, 820, 832, 839, 843, 845, 845, 843, 839, 832, 820, 799, 783, 763,
             735, 712, 681, 653, 6112, 0, 0],
            [1695, -532, 31, 452, -1495, 2155, -3084, 2807, -2538, -434, 3063, -15588, 22861, 22861, -15588, 3063, -434,
             -2538, 2807, -3084, 2155, -1495, 452, 31, -532, 1695, 0, 0]
        ]
        fir_values = filt_bank[fir_index]
        self.rx_param.rx_FIR_Index = fir_index

        upload_data = np.array(fir_values, dtype=np.int16)
        rx = self.radar_low_level
        rx.write_block(RXBlock.Decimation, RxDecimationBlockAddr.DecimationFilterTaps.value, upload_data)
        logger.info("**************Finished FIR-Filter Config**************")

    def config_decimator(self, decim_factor: int = None, num_samples_out: int = None):
        decim_factor = decim_factor if decim_factor is not None else self.rx_param.rx_DecimationRatio
        num_samples_out = num_samples_out if num_samples_out is not None else self.shared_params.rx_NumSamplesOut
        # super().config_decimator(decim_factor)
        rx = self.radar_low_level
        val = decim_factor
        self.rx_param.rx_DecimationRatio = decim_factor

        rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.Decimation.value, val)
        # Q-Multiplier is 1.26
        # rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.QMultiplier.value, 20643)  # 20800 in Leon's script
        rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.QMultiplier.value, 19300)  # 20800 in Leon's script
        # set latency (min. 1) to 80 samples
        rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.Latency.value, 140)  # 80
        # set data duration to 8192 samples
        rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.DataDuration.value, num_samples_out)

        # New in V00.07: after updating decimation value - need to initiate self calibration by setting
        # bit 5 in register 0 of block 6. This process takes ~100ms to complete, so a sleep must be used.

        # rx.write_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.ControlReg.value, 32)
        rx.modify_cpu_control_reg(RxCpuControlReg.CalibrateDecimatedClock.value)
        time.sleep(0.5)

    def correct_clk_phase(self):
        # super().correct_clk_phase()
        logger.info(" Correct sampling clock phase")
        rx = self.radar_low_level

        status_reg_val = rx.read_reg(RXBlock.CpuRegisters, RxCpuBlockAddr.StatusReg.value, ExpResType.Int)
        if status_reg_val & RxCpuStatusReg.SweepActive.value == 0:
            logger.debug(" WARNING: Synth-Unit is not sweeping\r")
        else:
            if status_reg_val & RxCpuStatusReg.SamplingClkInv.value == 8:
                logger.debug("Sampling_Clk inverted --> adjust\r")
                rx.modify_cpu_control_reg(RxCpuControlReg.SampleClkInverse.value)
            else:
                logger.debug(" Sampling_Clk correct\r")

    def enable_test_signal(self, en: bool = None):
        en = en if en is not None else self.rx_param.rx_test_signal_en
        # super().enable_test_signal(en)
        rx = self.radar_low_level
        self.rx_param.rx_test_signal_en = en

        rx.modify_cpu_control_reg(RxCpuControlReg.InitTestDAC.value)
        if en:
            rx.write_reg(RXBlock.TestSignal, RxTestSignalBlockAddr.TestOscOnOff.value, 3)  # 1 for async injection
        else:
            rx.write_reg(RXBlock.TestSignal, RxTestSignalBlockAddr.TestOscOnOff.value, 0)

    def config_test_signal(self, amp: int = None, f_offset: float = None):
        # f_offset is in MHz
        amp = amp if amp is not None else self.rx_param.rx_test_signal_amp
        f_offset = f_offset*1e6 if f_offset is not None else self.rx_param.rx_test_signal_offset
        # super().config_test_signal(amp, f_offset)
        rx = self.radar_low_level

        rx.write_reg(RXBlock.TestSignal, RxTestSignalBlockAddr.PhaseOffQ.value, 0)
        rx.write_reg(RXBlock.TestSignal, RxTestSignalBlockAddr.PhaseOffI.value, 0)  # -1400)

        length = 8192
        fs_divisor = round(f_offset * length / SysConfig.fs / 2)  # calculated field from f_offset.
        t = np.linspace(0.0, (length - 1) / SysConfig.fs, length)

        # in order to get in continuous mode and get a stable reading in the SA, the freq should be a
        # multiple of fs/Len
        f_test = fs_divisor * SysConfig.fs / length

        self.rx_param.rx_test_signal_amp = amp
        self.rx_param.rx_test_signal_offset = f_offset
        self.rx_param.f_test_divisor = fs_divisor

        logger.info(f"Test signal frequency: {f_test / 1.0e6:3.3f} MHz\n")
        amp_val = amp

        signal_c = np.round(amp_val * np.sin(2.0 * np.pi * f_test * t))
        signal_s = np.round(amp_val * np.cos(2.0 * np.pi * f_test * t))
        sig_len = len(signal_s)
        upload_data = np.zeros((sig_len, 2), dtype=np.int16)
        upload_data[:, 0] = signal_c
        upload_data[:, 1] = signal_s
        rx.write_block(RXBlock.TestSignal, RxTestSignalBlockAddr.TestSignalData.value, upload_data)

    def config_ssb(self, amp: float = None, f_offset: float = None):
        amp = amp if amp is not None else self.rx_param.rx_SSB_Amp
        f_offset = f_offset if f_offset is not None else self.rx_param.rx_SSB_Freq
        # super().config_ssb(amp, f_offset)
        logger.info("Init MIXER memory")
        rx = self.radar_low_level

        sig_len = 8192
        tt = np.linspace(0, (sig_len - 1) / (SysConfig.fs / (2.0 ** self.global_params.rx_DecimationRatio)),
                         sig_len)

        self.rx_param.rx_SSB_Amp = amp
        self.rx_param.rx_SSB_Freq = f_offset
        rx_SSB_Amp = amp

        mix_vect = rx_SSB_Amp * np.exp(-1j * 2.0 * np.pi * f_offset * tt)

        act_len = len(mix_vect)
        real_vect = mix_vect.real
        imag_vect = mix_vect.imag
        norm_fact = max(np.max(real_vect.__abs__()), np.max(imag_vect.__abs__()))
        real_vect = (real_vect / norm_fact) * 4096.0
        imag_vect = (imag_vect / norm_fact) * 4096.0
        upload_data = np.zeros([act_len * 2, ], dtype=np.int16)
        upload_data[0::2, ] = np.floor(real_vect)
        upload_data[1::2, ] = np.floor(imag_vect)
        rx.write_block(RXBlock.SSB, RxSsbBlockAddr.SsbData.value, upload_data)

    def config_ram(self, amp: int = None, freq: float = None, noise_std: int = None):
        amp = amp if amp is not None else self.rx_param.RAM_SignalAmp
        freq = freq if freq is not None else self.rx_param.rx_RAM_tone_freq
        noise_std = noise_std if noise_std is not None else self.rx_param.rx_RAM_STD
        # super().config_ram(amp, freq, noise_std)
        logger.info("Configure emulation memory")
        rx = self.radar_low_level

        self.rx_param.RAM_SignalAmp = amp
        self.rx_param.rx_RAM_tone_freq = freq
        self.rx_param.rx_RAM_STD = noise_std

        length = self.shared_params.rx_RAM_SamplesNum
        t = np.linspace(0, (length - 1) / self.rx_param.fs, length)
        signal = self.shared_params.rx_RAM_Amp * np.cos(2 * np.pi * self.rx_param.rx_RAM_tone_freq * t)
        noise = (self.rx_param.rx_RAM_STD * np.random.randn(length, 1))
        combine_signal = np.round(signal + noise)
        upload_data = combine_signal.astype(dtype=np.int16)
        rx.write_block(RXBlock.AdcSampling, RxAdcBlockAddr.RamDataDataStart.value, upload_data)

    def config_nco(self, freq: float = None, amp: int = None, phase0: float = None):
        freq = freq if freq is not None else self.rx_param.rx_NCO_Freq
        amp = amp if amp is not None else self.rx_param.rx_NCO_Amp
        phase0 = phase0 if phase0 is not None else self.rx_param.rx_NCO_Phase
        # super().config_nco(freq, amp, phase0)
        rx = self.radar_low_level

        logger.debug(" Configure NCO\r")
        Frequency = freq
        self.rx_param.rx_NCO_Freq = freq

        Phase = phase0
        self.rx_param.rx_NCO_Phase = phase0

        Amplitude = amp * 2
        if Amplitude > 4096:  # clip values to 4096 (12bit) - same as ADC
            Amplitude = 4096
        self.rx_param.rx_NCO_Amp = Amplitude

        dummy1 = round(Frequency * 68.719 * 62.5e6 / SysConfig.fs)
        dummy2 = round(Phase * 182.044)

        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.NCO_freq_H.value, dummy1 // 65536)  # Frequency NCO 'H'
        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.NCO_freq_L.value, dummy1 % 65536)  # Frequency NCO 'L'
        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.NCO_phase.value, dummy2)  # NCO phase
        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.NCO_amplitude.value, Amplitude)  # NCO amplitude

    def config_frame(self, num_samples: int = None, frame_len: int = None, sync_delay: int = None):
        # todo: add arguments to function call (defaults to self.RxParam values)
        num_samples = num_samples if num_samples is not None else self.rx_param.rx_FrameGen_N_Samples
        frame_len = frame_len if frame_len is not None else self.rx_param.FrameLen
        sync_delay = sync_delay if sync_delay is not None else self.rx_param.SyncDelay
        # super().config_frame(num_samples, frame_len, sync_delay)
        logger.info(" Init Frame Generator")
        rx = self.radar_low_level
        # turn off frame generator
        run_mode_keep = self.shared_params.rx_TriggerMode
        self.set_run_mode(RxTriggerMode.Stop)
        # rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.ControlReg.value, TriggerMode.Stop.value)

        # of samples
        self.rx_param.rx_FrameGen_N_Samples = num_samples
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.SamplesNumH.value,
                     num_samples // 65536)  # Upper 16bits
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.SamplesNumL.value,
                     num_samples & 65535)  # Lower 16bits

        # Frame Rep
        self.rx_param.FrameLen = frame_len
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.RepeatH.value,
                     self.rx_param.FrameLen // 65536)  # Upper 16bits
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.RepeatL.value,
                     self.rx_param.FrameLen % 65535)  # Lower 16bits

        # Sync delay (cable length compensation)
        self.rx_param.SyncDelay = sync_delay
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.SyncDelayH.value,
                     self.rx_param.SyncDelay // 65536)  # Upper 16bits
        rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.SyncDelayL.value,
                     self.rx_param.SyncDelay % 65535)  # Lower 16bits

        # restore run mode
        self.set_run_mode(run_mode_keep)
        # rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.ControlReg.value,
        #              self.RxParam.RunMode.value)  # self.RxParam.RunMode

    def frame_capture(self):
        # super().frame_capture()
        logger.info(" frame_capture start")
        rx = self.radar_low_level
        # turn on frame generator
        self.set_run_mode(RxTriggerMode.Manual)
        # rx.write_reg(RXBlock.FrameGen, RxFrameGenBlockAddr.ControlReg.value, TriggerMode.Manual.value)
        time.sleep(0.01)

    def config_dbf(self, bfm: np.ndarray([48, 64]) = np.zeros([48, 64]), num_beams_to_write: int = 64):
        # super().config_dbf(bfm)
        rx = self.radar_low_level

        if bfm.shape != (48, 64) or bfm.dtype != np.complex:
            print("Incorrect bfm size/type (should be 48*64 complex)")
            return

        # reshape and padd for easy writing
        n_pad = int(RxBeamFormerBlockAddr.BeamAllocatedSpace.value / 2 - 48)
        bfm = np.concatenate([bfm.transpose(), np.zeros([64, n_pad], dtype='complex')], axis=1)
        bfm = bfm.reshape([int(RxBeamFormerBlockAddr.BeamAllocatedSpace.value / 2) * 64, 1])
        dest = np.ndarray([RxBeamFormerBlockAddr.BeamAllocatedSpace.value * 64, 1], dtype='int16')
        dest[0::2] = bfm.real
        dest[1::2] = bfm.imag
        rx.write_block(RXBlock.BeamFormer, RxBeamFormerBlockAddr.Beam0Coeff.value,
                       dest[0:num_beams_to_write * RxBeamFormerBlockAddr.BeamAllocatedSpace.value])

    def config_dbf_eye(self):
        print("config_dbf_eye does nothing now.")
        # set the DBF memory to diagonal (eye matrix) - to output channel per beam
        # super().config_dbf_eye()
        # not a must

    def set_debug_data(self, debug_input: RxDebugInputSource = None, channel: int = None, bit_shift: int = None):
        debug_input = debug_input if debug_input is not None else self.rx_param.rx_DebugInputSource
        channel = channel if channel is not None else self.rx_param.channel
        bit_shift = bit_shift if bit_shift is not None else self.rx_param.rx_Bit_Shift
        # super().set_debug_data(debug_input, channel, bit_shift)
        rx = self.radar_low_level
        debug_inp_val = debug_input
        channel = 0 if channel < 0 or channel > 47 else channel
        bit_shift = 5 if bit_shift < 0 or bit_shift > 6 else bit_shift

        self.rx_param.rx_DebugInputSource = debug_inp_val
        self.rx_param.channel = channel
        self.rx_param.rx_Bit_Shift = bit_shift

        rx.write_reg(RXBlock.Decimation, RxDecimationBlockAddr.Decimation.value,
                     8 * self.rx_param.channel + self.global_params.rx_DecimationRatio)
        rx.write_reg(RXBlock.DebugMem, RxDbgMemBlockAddr.Multiplexer,
                     16 * self.rx_param.rx_Bit_Shift + self.rx_param.rx_DebugInputSource.value)

    def read_iq_data(self, do_capture: bool = True, num_samples: int = None, return_complex: bool = False,
                     return_db: bool = True, decim_ratio=4):
        num_samples = num_samples if num_samples is not None else self.rx_param.rx_NumSamplesOut
        self.rx_param.rx_NumSamplesOut = num_samples

        # super().read_iq_data(do_capture, num_samples, return_complex, return_db)
        # length = 8192  # complex values (16bit + 16bit)
        # length = self.RxParam.rx_FrameGen_N_Samples//(2**self.RxParam.rx_DecimationRatio)
        length = num_samples
        rx = self.radar_low_level

        if do_capture:
            self.frame_capture()
            time.sleep(0.1)

        i_data = rx.read_block(RXBlock.DebugMem, RxDbgMemBlockAddr.I_Data, length)
        q_data = rx.read_block(RXBlock.DebugMem, RxDbgMemBlockAddr.Q_Data, length)
        i_data = i_data.astype(dtype=np.float32)
        q_data = q_data.astype(dtype=np.float32)
        iq_data = np.array(i_data, dtype=complex)
        iq_data.real = i_data
        iq_data.imag = q_data
        iq_freq, iq_snr = mh.calc_iq_fft(iq_data, return_complex, return_db, decim_ratio)
        # iq_freq, iq_snr = self.calc_iq_fft(iq_data, return_complex, return_db)
        return iq_data, iq_freq, iq_snr

    def read_raw_adc(self, do_capture: bool):
        # super().read_raw_adc(do_capture)
        rx = self.radar_low_level

        if do_capture:
            self.frame_capture()
            time.sleep(0.05)

        temp = rx.read_block(RXBlock.DebugMem, RxDbgMemBlockAddr.ADC_raw_base, 64 * 256)  # read the complete block
        temp = temp.reshape([256, 64])
        temp = temp[:, 0:48].transpose()  # throw away unwanted memory segments
        raw_adc_data = temp.astype(dtype=np.float32)
        return raw_adc_data

    def select_debug_input_source(self, input_src: RxDebugInputSource = None, channel: int = None):
        input_src = input_src if input_src is not None else self.rx_param.rx_DebugInputSource
        channel = channel if channel is not None else self.rx_param.channel
        # super().select_debug_input_source(input_src, channel)
        # Set source
        logger.info("Configure input source")
        rx = self.radar_low_level

        self.rx_param.rx_DebugInputSource = input_src
        self.rx_param.channel = channel

        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.RamDataSelect.value,
                     self.rx_param.rx_DebugInputSource.value + 4 * self.rx_param.channel)

    def set_rx_data_source(self, source: RxInputSource = None, channel: int = None):
        source = source if source is not None else self.rx_param.rx_InputSource
        channel = channel if channel is not None else self.rx_param.channel
        # super().set_rx_data_source(source, channel)
        logger.info(f"Set data source to {source}")
        # Configure source registers
        rx = self.radar_low_level
        self.rx_param.rx_InputSource = source
        self.rx_param.channel = channel
        rx.write_reg(RXBlock.AdcSampling, RxAdcBlockAddr.ChannelSelect.value,
                     self.rx_param.rx_InputSource.value + 4 * self.rx_param.channel)



rx_test = RxNode()

print(rx_test.disconnect())
