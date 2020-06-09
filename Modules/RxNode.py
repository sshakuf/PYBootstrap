import EventBroker
from EngineComponent import EngineComponent
from Modules.Helpers.Node import Node

import logging

logger = logging.getLogger(__name__)


class RxNode(Node):
    def __init__(self):
        logger.debug("init")

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



