# import EventBroker
# from EngineComponent import EngineComponent
import tools.Engine as Engine
from tools.DataStore import *
from enum import Enum
import logging
from Modules.Helpers.eNums import BoardType
from Modules.Helpers.eNums import *
import Modules.Helpers.eNums as eNums
from Modules.Helpers.RxParams import *


logger = logging.getLogger(__name__)

# ### Node now have only behavior functions which shared with all components (rx, tx and synt) ### #


class Node:
    def __init__(self):
        logger.debug("init")
        self.id = "1"
        self._state = eNums.RuningState.NOTINITIALIZED
        self.is_verbose = True
        self.engine = None
        self.global_params = get_global_params()  # singleton object (should be on engine?)
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False
        self.can_bus_id = None

    def getState(self):
        return self._state

    def Initialize(self):
        self.engine = Engine.GetEngine()
        if self.onBeforeInitialized():
            self._state = eNums.RuningState.INITIALIZED
            self.onAfterInitialized()
            return True
        return False

    def Start(self):
        if self.onBeforeStart():
            self.onAfterStart()
            self._state = eNums.RuningState.STARTED
            return True
        return False

    def Run(self):
        if self.onBeforeRun():
            self.onAfterRun()
            self._state = eNums.RuningState.RUNNING
            return True
        return False

    def Stop(self):
        if self.onBeforeStop():
            self.onAfterStop()
            self._state = eNums.RuningState.STOPPED
            return True
        return False

    def onBeforeInitialized(self):
        return True

    def onAfterInitialized(self):
        pass

    def onBeforeStart(self):
        return True

    def onAfterStart(self):
        pass

    def onBeforeRun(self):
        return True

    def onAfterRun(self):
        pass

    def onBeforeStop(self):
        return True

    def onAfterStop(self):
        pass

    # #################################################################### #
    # ### Functions shared with all base mid classes from Doron's code ### #
    # #################################################################### #

    def get_version(self):
        pass

    def disconnect(self):  # CLEANUP?
        if self.before_disconnect():
            self.after_disconnect()
            self._state = eNums.RuningState.CONNECTED
            return True
        return False

    def before_disconnect(self):
        return True

    def after_disconnect(self):
        pass

    def connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        if self.before_connect(hw_interface_type, can_bus_unit_id):
            self.after_connect()
            self._state = eNums.RuningState.CONNECTED
            return True
        return False

    def before_connect(self, hw_interface_type: HWInterfaceType, can_bus_unit_id: CanBusUnitID):
        return True

    def after_connect(self):
        pass

    def get_status(self):
        pass

    # same signature at doron's code, different implementation
    def config_frame(self, num_samples: int = None, frame_len_usec: int = None, sync_delay: int = None):
        pass

    def init_hw(self):
        pass

    def set_init_flag(self, flag_val: bool):  # only rx and tx has it
        pass

    def get_init_flag(self):  # only rx and tx has it
        pass

    def set_run_mode(self, run_mode):
        pass

    def start_hardware(self):
        pass

    def set_high_speed_debug_mem(self, test_data):# test_data: np.dtype('complex')):
        pass

    def get_high_speed_debug_mem(self):
        pass

    def set_img_format(self):
        pass

    # ### Added by us to support Doron's code ### #
