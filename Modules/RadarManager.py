import tools.EventBroker
from tools.EngineComponent import EngineComponent
import logging
import tools.Engine as Engine
# import tools.DataStore as DataStore
import tools.ObjectRepository
from tools.DataStore import *
import platform
import sys

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
        self.system_platform()
        self._txManager = self.engine.objectRepository.getInstancesById(
            "TxManager")
        self._rxManager = self.engine.objectRepository.getInstancesById(
            "RxManager")
        self._synt = self.engine.objectRepository.getInstancesById(
            "SyntNode")
        self._radarLogic = self.engine.objectRepository.getInstancesById(
            "TheOneAndOnly_RadarLogic")

        self._synt.Initialize()
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
        self._synt.Start()
        return True

    def onAfterStart(self):
        pass

    def onBeforeRun(self):
        self._radarLogic.calc_something()  # calculating and changes props
        self._txManager.Run()  # has shared properties which rise event when one changes
        self._rxManager.Run()  # has shared properties which rise event when one changes
        self._synt.Run()  # has shared properties which rise event when one changes

        return True

    def onAfterRun(self):
        pass

    def onBeforeStop(self):
        self._txManager.Stop()
        self._rxManager.Stop()
        self._synt.Stop()
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

    def system_platform(self):
        # RxNode now has functionality of Doron's RxMidLevelBase and RxMidLevel.
        if platform.machine() == 'aarch64' and sys.platform == "linux":
            self.global_params.cal_vect_path = "/ext_ssd/PrjGL/radar-control/SystemTests/Calibration/REF_files/"
            self.global_params.hw_interface_type = HWInterfaceType.I2C
            return True
        else:
            self.global_params.cal_vect_path = "c:/temp2/"
            self.global_params.hw_interface_type = HWInterfaceType.CanBus
            return False
