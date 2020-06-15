from enum import Enum


global rx_shared_params
rx_shared_params = None


class RxLocalParams:
    def __init__(self):
        self.SyncDelay = 9  # cable length delay (clks)
        self.rx_test_signal_offset = 0  # test (Calibration) signal frequency offset from carrier
        self.rx_test_signal_amp = 0  # test signal amplitude
        self.debug_channel = 3  # Chan to debug 0..47. calculated
        self.debug_beam = 0
        self.mipi_debug_ram = []
        self.output_mipi_test_ram = False  # needs to be in every instance (synth, tx and rx)
        self.modulator_freq = 0
        self.modulator_amp = 0
        self.test_signal_enable = False


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


# rx shared params is a single instance shared across all rx's objects.
class RxSharedParams(Singleton):
    def __init__(self):
        self.rx_FIR_Index = 1  # FIR1 cutoff is at 0.5*fs, matching decim 1:2. FIR2 matches 1:4 decim ...
        self.rx_TriggerMode = RxTriggerMode.External  # 0 - stop, 1- manual trigger, 2- free run, 4- external trigger
        self.rx_InputSource: RxInputSource = RxInputSource.ADC
        self.rx_DebugInputSource: RxDebugInputSource = RxDebugInputSource.ADC
        self.rx_Bit_Shift = 0
        self.rx_SSB_Freq = 0
        self.rx_SSB_Amp = 1
        self.rx_RAM_STD = 10
        self.rx_RAM_Amp = 100
        self.rx_RAM_tone_freq = 1.54e6
        self.rx_RAM_SamplesNum = 8200
        self.rx_NCO_Amp = 400  # was 1000
        self.rx_NCO_Freq = 1.23e6  # was 2.43e6
        self.rx_NCO_Phase = 0
        self.adc_test_module = 0
        self.test_signal_freq = 2.4
        self.test_signal_amp = 400


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


# Singleton engine
def get_rx_shared():
    global rx_shared_params
    if rx_shared_params == None:
        rx_shared_params = RxSharedParams()
    return rx_shared_params
