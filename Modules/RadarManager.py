import EventBroker
from EngineComponent import EngineComponent
import logging
import tools.Engine as Engine
import tools.DataStore as DataStore
import tools.ObjectRepository

logger = logging.getLogger(__name__)


# what is the relationship between radar_manager and radar_logic?


class RadarManager(EngineComponent):
    def __init__(self):
        logger.debug("init")
        self.data_store = DataStore.DataStore()
        self._txManager = None
        self._rxManager = None
        self._radarLogic = None
        self.engine = None

    def onBeforeInitialized(self):
        self.engine = Engine.GetEngine()
        self._txManager = self.engine.objectRepository.getInstancesById(
            "TxManager")
        self._rxManager = self.engine.objectRepository.getInstancesById(
            "RxManager")
        self._radarLogic = self.engine.objectRepository.getInstancesById(
            "TheOneAndOnly_RadarLogic")

        self._txManager.Initialize()
        self._rxManager.Initialize()
        self._radarLogic.Initialize()

        self.setDefaultProps()
        return True

    def setDefaultProps(self):
        # self.engine.props.freq = 500
        pass

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

    @EventBroker.RegisterListener("PropertyChanged")
    def onPropertyChanged(self, data):
        logger.debug("propertyChanged")
