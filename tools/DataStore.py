import sys

import json
import os.path
import traceback
import logging
from dotmap import DotMap

logger = logging.getLogger(__name__)

settings = ''
# %%


def getDefaultSettings():
    prop = {}
    prop['Connection_string'] = "udp:127.0.0.1:14551"  # SImulation or PI
    prop['ConnectOnStartup'] = "True"  # SImulation or PI

    return prop


def mergeWithDefaults():
    prop = getDefaultSettings()
    for e in prop.keys():
        if not settings.has_key(e):
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
        logger.info("Loaded settings from " + filename +
                    " " + settings['SerialPort'])
        # Todo merge values that done exist
        mergeWithDefaults()

settings = DotMap(settings)


def SaveSettingsTo(inFileName):
    with open(inFilename, mode='w') as f:
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
