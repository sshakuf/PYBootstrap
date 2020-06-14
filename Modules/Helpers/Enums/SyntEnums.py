"""
SYNT enumuration
aligned with register map V00.13 (31/05/2020)
"""

from enum import Enum


class SyntConfig:
    def __init__(self):
        # self.force_init = 1

        self.FrameGen_N_Samples = 17000  # Number of samples
        self.FrameLen = 20000  # Length of frame (in fs_clk units). calculated from 'FrameGen_Repitition'
        self.RunMode = SyntRunMode.FreeRun  # 0- manual trigger, 1- free run, 2- external trigger

        # self.fc = 77.5e9        # center frequency (77GHz) ui id: 'CenterFreq'
        self.Bandwidth: float = 120.0  # [MHz] in E-band domain
        self.SweepTime: float = 500.0  # [usec]
        self.RampConfiguration = RampType.Sawtooth


class SyntBlock(Enum):
    CpuRegisters = 0
    FrameGen = 1
    MIPI_RAM = 2  # new in ver 00.10


class SyntCpuBlockAddr(Enum):
    ControlReg = 0  # register to issue commands to radar. For commands see SyntCpuControlReg
    LedFunction = 0x01   # control the functionality of the LED as testpoint (added in 00.13)
    StartFreq_H = 0x010  # start frequency in MHz, upper 2 bits (18bit number)
    StartFreq_L = 0x011  # start frequency in MHz, lower 16 bits (18bit number)
    Bandwidth_H = 0x012  # frequency bandwidth in MHz, IN THE 77GHz DOMAIN, upper 2 bits (18bit number)
    Bandwidth_L = 0x013  # frequency bandwidth in MHz, IN THE 77GHz DOMAIN, lower 16 bits (18bit number)
    SweepTime_H = 0x014  # Sweep time in 0.1us resolution, upper 2 bits (18bit number)
    SweepTime_L = 0x015  # Sweep time in 0.1us resolution, lower 16 bits (18bit number)
    RampConfig = 0x016  # 0 - Sawtooth, 1 - Triangle (UP/DOWN)

    FpgaVersion = 0x080  # fpga version
    BoardType = 0x081  # Board type: 0=RX-Board, 1=Synt-Board, 2=Synthesizer
    SerialNum = 0x082  # Serial number

    FPGATemp = 0x0A0  # 1°C resolution
    TempSinsirion = 0x0a1  # 0.01°C resolution
    Humidity = 0x0a2  # 0.01% resolution
    AccX = 0x0a3  # 0.01g resolution
    AccY = 0x0a4
    AccZ = 0x0a5
    StatusReg = 0x0a7  # status bits


# bitwise status register
class SyntCpuStatusReg(Enum):
    TrxLocked = 1       # 1 - high-speed tranceiver is locked
    MainPllLocked = 2   # 1 - Main PLL is locked
    Vstage5_PG = 4  # 1 - all internal positive voltages are OK
    Vout_nPG = 8  # 1 - voltage output to next unit is NOT ok. (0- Voltage OK)
    LvdsPllLocked = 16  # 1 - PLL of LVDS high speed connection (MIPI) is locked
    LoopbackClkDetected = 32  # 1 - Clock detected on data-in port
    ReceiverCalibrationActive = 64  # 1 - transceiver is calibrating


class SyntCpuCmdRegBits(Enum):
    InitPll = 0  # Initialize PLL (self clearing)
    EnableCanLogger = 1  # enable logging CAN commands on NIOS terminal
    DisableCanLogger = 2  # disable logging CAN commands on NIOS terminal
    ResetTRX = 3          # reset all SERDESs (suggested after startup)


class SyntFrameGenBlockAddr(Enum):
    ControlReg = 0  # register to issue commands to radar. For commands see SyntCpuControlReg
    SampleNumH = 1  # Number of ADC samples in sweep, 16ns increment, write this register first
    SampleNumL = 2  # Number of ADC samples, lower 16 bits, 16ns increment, write second
    FrameLenH = 3  # Frame repetition, upper 16 bits, 16ns increment, write this register first
    FrameLenL = 4  # Frame repetition, lower 16 bits, 16ns increment, write this register second


class SyntMipiRamBlockAddr(Enum):  # new in ver 00.10
    ControlReg = 0  # register for future use. MipiDataFormat
    Sim_RAM_I_base_addr = 0x2000
    Sim_RAM_Q_base_addr = 0x4000


# class SyntMipiFormat(Enum):  # new in ver 00.12 (MIPI picture size)
#     R8192_A32 = 0   # 48bit per pixel, 811.6us
#     R8192_A64 = 1   # 48bit per pixel, 1.621ms
#     R8192_A128 = 2  # 48bit per pixel, 3.24ms
#     R8192_A256 = 3  # 48bit per pixel, 6.479ms


# MOVED TO GLOBAL TRIGGER MODE
class SyntRunMode(Enum):
    Stop = 0
    Manual = 1
    FreeRun = 2


class RampType(Enum):
    Sawtooth = 0
    Triangle = 1


class LedFunction(Enum):
    FrameActive = 0
    FrameActiveDelayed = 1
    ClkDetected = 2
    CPU = 3
