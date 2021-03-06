import EventBroker
from EngineComponent import EngineComponent
import tools.Engine as Engine
import tools.ObjectRepository
from Modules.Helpers.NodeManager import NodeManager
import logging

logger = logging.getLogger(__name__)


class TxManager(NodeManager):
    def __init__(self):
        super().__init__()
        self._nodeTypeName = "TxNode"

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

