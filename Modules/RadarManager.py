import EventBroker
from EngineComponent import EngineComponent
import logging
import tools.Engine as Engine
import tools.ObjectRepository

logger = logging.getLogger(__name__)


class RadarManager(EngineComponent):
    def __init__(self):
        logger.debug("init")
        # _txManager = Engine.GetEngine().objectRepository.CreateInstance("TxManager")

    def onBeforeInitialized(self):
        self.engine = Engine.GetEngine()
        self._txManager = self.engine.objectRepository.getInstancesById("TxManager")
        self._rxManager = self.engine.objectRepository.getInstancesById("RxManager")

        self._txManager.Initialize()
        self._rxManager.Initialize()
        return True

    def onAfterInitialized(self):
        pass

    def onBeforeStart(self):
        self._txManager.Start()
        self._rxManager.Start()
        return True

    def onAfterStart(self):
        pass
    def onBeforeRun(self):
        self._txManager.Run()
        self._rxManager.Run()
        return True
    def onAfterRun(self):
        pass
    def onBeforeStop(self):
        self._txManager.Stop()
        self._rxManager.Stop()
        return True
    def onAfterStop(self):
        pass




    @EventBroker.RegisterListener("Test2")
    def onEventTest2(a):
        logger.debug("onEventTest2")
