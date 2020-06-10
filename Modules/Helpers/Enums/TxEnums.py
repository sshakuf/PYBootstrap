"""
TX enumuration
aligned with register map V00.13 (20/05/2020)
"""

from enum import Enum


class TxConfig:
    def __init__(self):
        # self.cpu_freq_clk = 100e6  # board clock freq (100MHz using internal VCXO, 125MHz using external clock)
        # self.fs = self.cpu_freq_clk // 2
        # self.baud_rate = 1042000
        pass


class TXBlock(Enum):
    CpuRegisters = 0
    TxModulator = 1
    TxMipiBlock = 2
    FrameGen = 8


class TxCpuBlockAddr(Enum):
    CmdReg = 0  # register to issue commands to radar. For commands see TxCpuControlReg
    DacBiasStart = 0x010  # Bias Multiplier
    FpgaVersion = 0x080  # fpga version
    BoardType = 0x081  # Board type: 0=RX-Board, 1=TX-Board, 2=Synthesizer
    SerialNum = 0x082  # Serial number
    FPGATemp = 0x0a0  # 1°C resolution
    TempSinsirion = 0x0a1  # 0.01°C resolution
    Humidity = 0x0a2  # 0.01% resolution
    AccX = 0x0a3  # 0.01g resolution
    AccY = 0x0a4
    AccZ = 0x0a5
    OutPower = 0x0a6  # Output Power PA. Detector level in mV.
    StatusReg = 0x0a7  # status bits
    # Corresponds to PA power (see MAAP-011106 datasheet), updated every 250ms


class TxCpuCmdRegBits(Enum):
    TurnOff = 0
    InitDacBias = 0x01  # Update Bias voltages (self clearing)
    InitTxDac = 0x02  # Init D/A Converter for Upconversion
    SampleClkInverse = 0x04  # invert sampling clock (when there is shift of 1/2 clk)
    ConfigDone = 0x80  # Configuration complete (just a memory location, no action)


# bitwise status register
class TxCpuStatusReg(Enum):
    IntClk = 1  # 1 - unit is running on internal clock
    VssPG = 2  # 1 - internal negative voltage is OK
    Vstage5_PG = 4  # 1 - all internal positive voltages are OK
    Vout_nPG = 8  # 1 - voltage output to next unit is NOT ok. (0- Voltage OK)
    SweepActive = 16  # 1 - receiving sweep from synthesizer
    SamplingClkInv = 32  # 1 - Compared to Synthesizer, the Sampling_Clk is inverted (180° shift)
    TransmitterLocked = 64	 # 1=Serial Transmitter is working correctly
    ReceiverCalibrationActive = 128  # 1=Serial Receiver Calibration running


class TxModulatorBlockAddr(Enum):
    CmdReg = 0  # register to issue commands to radar. For commands see TxModulatorCmdRegBits
    DacQOffset = 1  # Signed value, +2047 corresponds to amplitude '1'
    DacIOffset = 2  # Signed value, +2047 corresponds to amplitude '1'
    ModuISampPntStart = 0x04000  # Modulation Samplepoint start, I-Channel
    ModuQSampPntStart = 0x04001  # Modulation Samplepoint start, Q-Channel


class TxModulatorCmdRegBits(Enum):
    TurnOff = 0
    FreeRun = 1  # 1=free run mode
    ExtSync = 2  # 1=triggered from external SYNC
    BankSelect = 8  # bits 3..7 are used to select memory bank for modulator


class TxFrameGenBlockAddr(Enum):
    CmdReg = 0  # register to issue commands to radar. For commands see TxCpuControlReg
    SampleNumH = 1  # Number of ADC samples in sweep, 16ns increment, write this register first
    SampleNumL = 2  # Number of ADC samples, lower 16 bits, 16ns increment, write second
    FrameLenH = 3  # Frame repetition, upper 16 bits, 16ns increment, write this register first
    FrameLenL = 4  # Frame repetition, lower 16 bits, 16ns increment, write this register second
    SyncDelayH = 5  # ver 0012
    SyncDelayL = 6  # ver 0012


class TxMipiBlockAddr(Enum):  # new in ver V00.11
    ControlReg = 0
    SimMemBase_I = 0x2000  # By default a sinewave with amplitude 20000 is stored here
    SimMemBase_Q = 0x4000


class TxMipiControlRegBits:
    MipiDataSourceSelect = 0  # MipiDataOutType
    MipiDataFormat = 3        # MipiDataFormat


class MipiDataOutType(Enum):
    MipiTestData = 0
    MipiStream = 1


# class MipiDataFormat(Enum):
#     FMT_8192_32 = 0
#     FMT_8192_64 = 1
#     FMT_8192_128 = 2
#     FMT_8192_256 = 3


class TxFrameGenCmdRegBits(Enum):
    TurnOff = 0
    FreeRun = 1  # 1=free run mode
    ExtSync = 2  # 1=triggered from external SYNC


class TxTriggerMode(Enum):
    Stop = 0
    Manual = 1   # Write 1 to generate 1 frame --> Use this mode for Debug Data output
    FreeRun = 2
    External = 4
