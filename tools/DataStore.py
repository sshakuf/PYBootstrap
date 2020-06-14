from EventBroker import EventBroker
import sys
from Modules.Helpers.eNums import *
import json
import os.path
import traceback
import logging
from dotmap import DotMap

logger = logging.getLogger(__name__)

# #################################### #
# ### System params should be here ### #
# #################################### #

settings = ''
# %%

global global_params
global_params = None



def getDefaultSettings():
    prop = {}
    prop['example'] = "udp:127.0.0.1:14551"
    return prop


def mergeWithDefaults():
    prop = getDefaultSettings()
    for e in prop.keys():
        if e not in settings.keys():
            settings[e] = prop[e]


filename = 'settings.json'
if (len(sys.argv) > 1):
    filename = sys.argv[1]

if not os.path.exists(filename):
    logger.info("Default settings")
    settings = getDefaultSettings()

    with open(filename, mode='w') as f:
        json.dump(settings, f)
else:
    # load data
    with open(filename, 'r') as f:
        settings = json.load(f)
        # Todo merge values that done exist
        mergeWithDefaults()

settings = DotMap(settings)


def SaveSettingsTo(inFileName):
    with open(inFileName, mode='w') as f:
        json.dump(settings, f)


def LoadSettingsFrom(inFilename):
    with open(inFilename, 'r') as f:
        settings = json.load(f)
    return settings


def PrintError(err):
    logger.error("ERROR Exception" + str(err))
    tb = traceback.format_exc()
    logger.error(tb)
    c = 2


class RxStatus:
    def __init__(self):
        self.saturation = [0] * 16
        self.accelerometer = [0] * 3
        self.temperature = [0] * 16

        self.lo_power = [0] * 16
        self.board_temp = None
        self.board_humidity = None
        self.fpga_temp = None

        # ### status register ### #
        self.int_clk = None
        self.sweep_active = None
        self.sampling_clk_inverted = None
        self.vss_pg = None
        self.v_out_npg = None
        self.stage_3_pg = None


class TxStatus:
    def __init__(self):
        print("Tx status")


class NodeVersion:
    fpga_version = None
    board_type_enum = None
    serial_num = None


class GlobalParams:
    def __init__(self):
        self.frequency = 76000
        self.rx_FrameGen_N_Samples = 17000  # Number of samples
        self.rx_FrameGen_Rep_Cycle = 2.0  # Repitition cycle
        self.FrameLen = 20000  # Length of frame (in fs_clk units). calculated from 'FrameGen_Repetition'
        self.NumSamplesOut = 8192  # Todo: is it rx_FrameGen_Repitition, rx_TriggerFramesNumber ?
        self.rx_DBF_Steering = 5
        self.rx_DBF_Selected = 5
        self.number_of_beams = 8
        self.taper = None
        self.bandwidth = 1000
        self.chirp_duration = 10000
        self.decimation_ratio = 1  # Decimation Ratio = 2^Decimation_factor (0 = No decim, 1 = decim by 2....)
        self.debug_output_interface = DebugOutputInterface.MIPI.value
        self.output_format = MipiDataFormat.FMT_8192_32.value
        self.system_run_mode = 0


class DataStore:
    def __init__(self):
        self.dstore = 1

# rx = RxStatus()
# print(rx.status_register["sweep_active"])


# Singleton engine
def get_global_params():
    global global_params
    if global_params == None:
        global_params = GlobalParams()
    return global_params
