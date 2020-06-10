from enum import Enum


class RxParams:
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
        # self.f_test_divisor = round(self.rx_test_signal_offset * 8192 / SysConfig.fs)
        # Todo: calc from UI id's: 'rx_ChanSelectMode' and 'rx_ChanSelMultiStr_val'
        self.rx_ChanSelectMode = RXChanSelectMode.Single
        self.rx_ChanSelMultiStr_val = "3"
        self.channel = 3  # Chan to debug 0..47. calculated


class RXChanSelectMode(Enum):
    All = 0
    Multi = 1
    Single = 2


class RxTriggerMode(Enum):
    Stop = 0
    Manual = 1  # Write 1 to generate 1 frame --> Use this mode for Debug Data output
    FreeRun = 2
    External = 4
    ExternalDebug = 8


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
