import EventBroker
from EngineComponent import EngineComponent

import logging

from Modules.Helpers.Node import Node
from Modules.Helpers.TxParams import *
from Modules.Helpers.Enums.TxEnums import *
from tools.DataStore import *
from Modules.LowLevel import LowLevelBase, LowLevelCanBus, LowLevelI2C, LowLevelSerial


logger = logging.getLogger(__name__)


class TxNode(Node):
    def __init__(self):
        super().__init__()
        logger.debug("init")
        self.tx_param = TxLocalParams()
        self.status = TxStatus()
        self.version = NodeVersion()
        # Doron's part #
        self.is_connected = False
        self.is_hw_initialized = False
        self.is_started = False

    def onBeforeInitialized(self):
        self.can_bus_id = BoardType.TX.value * 16 + int(self.id)
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
