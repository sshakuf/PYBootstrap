import EventBroker
from tools.EngineComponent import EngineComponent
import logging
import tools.Engine as Engine

logger = logging.getLogger(__name__)


class RadarLogic(EngineComponent):
    def __init__(self):
        logger.debug("RadarLogic init...")
        self.engine = Engine.GetEngine()

    # change frequency should be on radarLogic
    def param_change(self, param):
        self.engine.eventBroker.fireEvent("changed_freq", freq)

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

    # @EventBroker.RegisterListener("Test")
    # def onEventTest(a):
    #     logger.debug("onEventTest")
    #
    # @EventBroker.RegisterListener("Test2")
    # def onEventTest2(a):
    #     logger.debug("onEventTest2")
