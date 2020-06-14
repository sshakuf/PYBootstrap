import tools.EventBroker
from tools.EngineComponent import EngineComponent
import logging
import tools.Engine as Engine
# import tools.DataStore as DataStore
import tools.ObjectRepository
from tools.DataStore import *

logger = logging.getLogger(__name__)


# what is the relationship between radar_manager and radar_logic?


class RadarManager(EngineComponent):
    def __init__(self):
        super().__init__()
        logger.debug("init")
        self.data_store = DataStore()
        self._txManager = None
        self._rxManager = None
        self._radarLogic = None
        self.engine = None
        self.global_params = GlobalParams()

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
        # self.engine.eventBroker.subscribeEvent("PropertyBeforeChange", self.onPropertyChanged)
        return True

    def setDefaultProps(self):
        # assign all global parameters to their engine properties
        global_param_dict = vars(self.global_params)
        for key in global_param_dict:
            self.engine.props[str(key)] = global_param_dict[key]
        pass

    def onAfterInitialized(self):
        # self.engine.eventBroker.subscribeEvent("PropertyBeforeChange", self.onPropertyChanged)
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

    def RegisterEvents(self):
        Engine.GetEngine().eventBroker.subscribeEvent(
            'PropertyChanged', "onPropertyChanged", self)

    def onPropertyChanged(self, data):
        logger.debug("propertyChanged")
        print("prop changed is: " + str(data))

    # @EventBroker.RegisterListener("Test2")
    # def onEventTest2():
    #     logger.debug("onEventTest2")
