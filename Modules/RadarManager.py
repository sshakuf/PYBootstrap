import EventBroker
from EngineComponent import EngineComponent
import logging

logger = logging.getLogger(__name__)


class RadarManager(EngineComponent):
    def __init__(self):
        logger.debug("init")

    def Initialize(self):
        logger.debug("Initialize")
        pass

    def Start(self):
        logger.debug("Start")
        pass

    def Run(self):
        logger.debug("Start")
        pass

    def Stop(self):
        logger.debug("Stop")
        pass

    @EventBroker.RegisterListener("Test2")
    def onEventTest2(a):
        logger.debug("onEventTest2")
