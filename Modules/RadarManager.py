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

    def Initialize(self):
        logger.debug("Initialize")
        self.engine = Engine.GetEngine()
        self._txManager = self.engine.objectRepository.getInstancesById("TxManager")
        self._rxManager = self.engine.objectRepository.getInstancesById("RxManager")

        self._txManager.Initialize()
        self._rxManager.Initialize()
        pass

    def Start(self):
        logger.debug("Start")
        self._txManager.Start()
        self._rxManager.Start()
        pass

    def Run(self):
        logger.debug("Start")
        self._txManager.Run()
        self._rxManager.Run()
        pass

    def Stop(self):
        logger.debug("Stop")
        self._txManager.Stop()
        self._rxManager.Stop()
        pass

    @EventBroker.RegisterListener("Test2")
    def onEventTest2(a):
        logger.debug("onEventTest2")
