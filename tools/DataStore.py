from EventBroker import EventBroker
import sys

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


class NodeVersion:
    fpga_version = None
    board_type_enum = None
    serial_num = None


class DataStore:
    def __init__(self):
        self.frequency = 76000


# rx = RxStatus()
# print(rx.status_register["sweep_active"])

