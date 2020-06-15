"""
RX enumuration
aligned with register map V00.11 (07/06/2020)
To use the Debug Memory over MIPI, the Frame Generator must be triggered in "ExternalDebug" mode
"""

from enum import Enum

# from Core.BaseNiArtObject import BaseNiArtObject # THIS IMPORT WAS CAUSING PROBLEMS. IT IS NOT USED ANYWAYS HERE.
# from Core.Enums import *



class RxInputSource(Enum):
    ADC = 0  # 0 changed in V0004
    NCO = 1  # 1 changed in V0004
    RAM = 3


class RxDebugInputSource(Enum):
    ADC = 0
    FIR = 1  # in UI caption is decimator
    Hilbert = 2
    DBF = 3
    SSB = 4
    FFT = 5


class RXChanSelectMode(Enum):
    All = 0
    Multi = 1
    Single = 2


# MOVED TO GLOBAL TRIGGER MODE
class RxTriggerMode(Enum):
    Stop = 0
    Manual = 1  # Write 1 to generate 1 frame --> Use this mode for Debug Data output
    FreeRun = 2
    External = 4
    ExternalDebug = 8


class RxMipiControlRegBits:
    MipiDataSourceSelect = 0  # DataOutType
    MipiDataFormat = 4        # MipiDataFormat


class DataOutType(Enum):
    MipiTestData = 0
    DebugMemData = 1
    BeamFormerData = 2  # Added in V00.08
    RawAdcData = 3  # added in V00.10


class RxBaudRate(Enum):
    BR1042000 = '1042000'
    BR1302000 = '1302000'


class RXBlock(Enum):
    AdcSampling = 1
    Decimation = 2
    DebugMem = 3
    BeamFormer = 4
    SSB = 5
    CpuRegisters = 6
    TestSignal = 7
    FrameGen = 8
    MipiDebugMem = 9  # new in ver V00.07


class RxMipiDebugMemBlockAddr(Enum):  # new in ver V00.07
    ControlReg = 0
    SimMemBase_I = 0x2000  # By default a sinewave with amplitude 20000 is stored here
    SimMemBase_Q = 0x4000


class RxFrameGenBlockAddr(Enum):
    ControlReg = 0
    SamplesNumH = 1
    SamplesNumL = 2
    RepeatH = 3
    RepeatL = 4
    SyncDelayH = 5  # ver 0004
    SyncDelayL = 6  # ver 0004


class RxBeamFormerBlockAddr(Enum):
    Beam0Coeff = 0
    BeamAllocatedSpace = 0x80
    BeamSelector = 0x2000  # new in ver 00.05


# Todo: update enum for block 1 (ADC)
class RxAdcBlockAddr(Enum):
    ChannelSelect = 0
    RamDataSelect = 0
    NCO_freq_H = 1
    NCO_freq_L = 2
    NCO_phase = 3
    NCO_amplitude = 4
    RamDataDataStart = 65536


# note: not enum
class RxDbgMemBlockAddr:
    Multiplexer = 0
    I_Data = 0
    Q_Data = 8192
    ADC_raw_base = 16384


class RxSsbBlockAddr(Enum):
    SsbData = 0


class RxDecimationBlockAddr(Enum):
    Decimation = 0  # Decimation
    QMultiplier = 1  # Q-Multiplier
    Latency = 2  # Latency
    DataDuration = 3  # Data duration
    DecimationFilterTaps = 64  # Decimation Filter taps


class RxCpuBlockAddr(Enum):
    ControlReg = 0  # register to issue commands to radar. For commands see RxCpuControlReg
    DacBiasBlockStart = 8  # dac bias 0-7
    AdcTestMode = 16  # adc test mode
    AdcOffsetBlockStart = 17  # Adc offset block 0 - 47 (reg17 - reg64)
    AdcChipPhaseAdjBlockStart = 65  # ADC Chip Phase Adjust block 0 - 6
    RxConfiguration = 80  # RX Configuration
    FpgaVersion = 128  # fpga version
    BoardType = 129  # Voard type
    SerialNum = 130  # Serial number
    RxChipsTempBlockStart = 143  # Rx chips (MR2001) temperatures block start(16 regs)
    FpgaTemp = 160  # Fpga temp in 1 degC resolution
    BoardTemp = 161  # Board temp in 0.01 degC resolution
    BoardHumid = 162  # Board humidity in 0.01% resolution
    RxSat = 163  # MR2001 Saturation flag, [bitwise]
    AccX = 164  # Accelerometer X in 0.01g resolution
    AccY = 165  # Accelerometer Y in 0.01g resolution
    AccZ = 166  # Accelerometer Z in 0.01g resolution
    StatusReg = 167  # See enum RxCpuStatusReg
    RxLoSensBlockStart = 176  # MR2001 LO power sensor in mV, block start (16 regs). Values should be >300mV


class RxTestSignalBlockAddr(Enum):
    TestOscOnOff = 0  # Switch off/on test oscillator
    PhaseOffQ = 1  # Offset Q
    PhaseOffI = 2  # Offset I
    TestSignalData = 16384  # test signal data


# multiple bits values. cpu will reset bit after done
# only 128 is permanent
class RxCpuControlReg(Enum):
    Nothing = 0
    UpdateBiasDAC = 1  # Update Bias voltages (self clearing)
    InitADC = 2  # Init 48 A/D-Converters (self clearing)
    InitRX_Chips = 4  # Init RX-Chips
    InitTestDAC = 8  # new in V0004
    SampleClkInverse = 16  # invert sampling clock (when there is shift of 1/2 clk from Tx module)
    CalibrateDecimatedClock = 32  # New in ver 00.07: calibrate phase of decimated clock. This takes ~100ms to complete
    SetGetConfigDone = 128  # get/set configuration done


# bitwise status register
class RxCpuStatusReg(Enum):
    IntClk = 1  # 1 - unit is running on internal clock
    SweepActive = 4  # 1 - receiving sweep from synthesizer
    SamplingClkInv = 8  # 1 - Compared to Synthesizer, the Sampling_Clk is inverted (180° shift)
    VssPG = 16  # 1 - internal negative voltage is OK
    Vout_nPG = 32  # 1 - voltage output to next unit is NOT ok. (0- Voltage OK)
    Vstage3_PG = 64  # 1 - all internal positive voltages are OK


class RxParam:
    # Todo: need to move to Rx instance
    def __init__(self):
        # from system Config, update by EngineBase on startup
        # =================================
        self.SyncDelay = 9  # cable length delay (clks)

        # Todo: need to read from engine base
        # commands that are broadcast to all Rx cards
        # =================================
        # Todo: FIR equal decimation, same for all rx
        self.rx_FIR_Index = 1  # FIR1 cutoff is at 0.5*fs, matching decim 1:2. FIR2 matches 1:4 decim ...
        self.rx_DecimationRatio = 1  # Decimation Ratio = 2^Decimation_factor (0 = No decim, 1 = decim by 2....)

        # Frame generator params
        # Todo: next 3: same for all rx, only with apply
        # Todo: I need to be sure what is the relation between trigger and frame gen
        # I have:   rx_FrameGen_N_Samples, rx_FrameGen_Repitition,
        #           rx_Trigger, rx_TriggerFrameIndex, rx_TriggerFramesNumber
        #           button rx_Trigger_OnOff
        self.rx_FrameGen_N_Samples = 17000  # Number of samples
        self.rx_FrameGen_Rep_Cycle = 2.0  # Repitition cycle
        self.FrameLen = 20000  # Length of frame (in fs_clk units). calculated from 'FrameGen_Repetition'
        self.rx_NumSamplesOut = 8192  # Todo: is it rx_FrameGen_Repitition, rx_TriggerFramesNumber ?
        # Todo: calculate from rx_TriggerMode, rx_TriggerFrameIndex, rx_TriggerFramesNumber
        self.rx_TriggerFrameIndex = 0
        self.rx_TriggerFramesNumber = 10
        self.rx_TriggerMode = RxTriggerMode.External  # 0 - stop, 1- manual trigger, 2- free run, 4- external trigger

        # commands for single Rx card
        # =================================

        # Todo: next 4, only with apply
        self.rx_InputSource: RxInputSource = RxInputSource.ADC
        # select source for debug test point
        self.rx_DebugInputSource: RxDebugInputSource = RxDebugInputSource.ADC
        self.rx_Bit_Shift = 0

        # SSB mixer parameters
        # Todo: next 2, only with apply
        self.rx_SSB_Freq = 0
        self.rx_SSB_Amp = 1

        # RAM parameters
        # Todo: next 4, on change, on apply load signal to card
        self.rx_RAM_STD = 10
        self.rx_RAM_Amp = 100
        self.rx_RAM_tone_freq = 1.54e6
        self.rx_RAM_SamplesNum = 8200

        # NCO parameters
        # Todo: next 3, on change
        self.rx_NCO_Amp = 400  # was 1000
        self.rx_NCO_Freq = 1.23e6  # was 2.43e6
        self.rx_NCO_Phase = 0

        # DBF parameters
        # Todo: Gil define, update on mid level function
        self.rx_DBF_Steering = 5
        self.rx_DBF_Selected = 5
        # Todo: put parameters here

        # test signal
        # Todo: next 4, on change, on apply load signal to card
        self.rx_test_signal_en = 0  # Enable the amplifier for calibration network injection
        self.rx_test_signal_offset = 0  # test (Calibration) signal frequency offset from carrier
        self.rx_test_signal_amp = 0  # test signal amplitude

        # calculated params
        # =================================
        # Todo: make properties to update params
        # test signal frequency, as fraction of the sampling freq
        self.f_test_divisor = round(self.rx_test_signal_offset * 8192 / SysConfig.fs)
        # Todo: calc from UI id's: 'rx_ChanSelectMode' and 'rx_ChanSelMultiStr_val'
        self.rx_ChanSelectMode = RXChanSelectMode.Single
        self.rx_ChanSelMultiStr_val = "3"
        self.channel = 3  # Chan to debug 0..47. calculated
