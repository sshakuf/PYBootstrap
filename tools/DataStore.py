import sys
vehicle = ''

import json
import os.path
import traceback
import logging
from dotmap import DotMap

logger = logging.getLogger(__name__)


settings = ''
location =''
#%%
def getDefaultSettings():
    prop = {}
    prop['SerialPort'] = "/dev/ttyS2" 
    prop['Connection_string'] = "udp:127.0.0.1:14551"  #SImulation or PI
    prop['ConnectOnStartup'] = "True"  #SImulation or PI
    prop['SendLocation'] = "True"  # send the location via Serial port ever x sec
    prop['PrintToLog'] = "True"
    prop['ISDrone'] = "True"
    prop['HTTPServer'] = "True"
    prop['SerialServer'] ="True"
    prop['Port'] = '8090'
    prop["Target_Connection_string"] =  "tty.SLAB_USBtoUART*"
    prop["Drone_2_Simulated"] = "False"
    prop["UDPServerEnabled"] = "False"
    prop["SerialRelay"] = "False"           # send command throu  the Serial port.  this is for groundstation to act as a relay.
    prop["HostUDPServerAddress"] = "localhost"
    prop["TCPStreaming"] = 'True'
    prop["RealVideo"] = "True"
    prop["DrawTargetOnVideo"] = 'False'
    prop["MissionLogicOn"] = 'True'
    prop["RadarIP"] = '127.0.0.1'
    prop["RadarPort"] = '5001'
    prop["SendTargetViaHttp"] = 'True'       # ground station will send Target drone location via HTTP
    prop["DroneIPAddress"] = '192.168.28.107'     # this is the IP address that the ground station will use to send the Drone the location of the target drone.
    prop["SendTargetViaSerial"] = 'False'   # ground station will send Target drone location via Serial
    prop["DefaultAirSpeed"] = "15"
    prop["TakeOffAlt"] = "8"                # Target altitude when taking off
    prop["TargetBBAltComp"] = "0"           # compensation for the target position when optic tracking is working this will move the 0 point of the y axis
    prop["TargetBBHeadingComp"] = "0"       # compensation for the target position when optic tracking is working this will move the 0 point of the X axis
    prop["TargetBBRange"] = "10"       # compensation for the target position when optic tracking is working this will move the 0 point of the z axis
    

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
        json.dump(settings,f)
else:
    #load data
    with open(filename, 'r') as f:
        settings = json.load(f)  
        logger.info("Loaded settings from " + filename + " " + settings['SerialPort'])
        # Todo merge values that done exist
        mergeWithDefaults()
    
settings = DotMap(settings)      

def SaveSettingsTo(inFileName):
    with open(inFilename, mode='w') as f:
        json.dump(settings,f)

def LoadSettingsFrom(inFilename):
    with open(inFilename, 'r') as f:
        settings = json.load(f)  
    return settings


def PrintError(err):
    logger.error("ERROR Exception" + str(err))
    tb = traceback.format_exc()
    logger.error(tb)
    c =2

