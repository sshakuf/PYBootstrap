from tools.EngineComponent import EngineComponent
import logging
import tools.Engine as Engine
from Modules.Helpers.MathHelpers import MathHelper as mh
from tools.DataStore import *

logger = logging.getLogger(__name__)


class RadarLogic(EngineComponent):
    def __init__(self):
        super().__init__()
        logger.debug("RadarLogic init...")
        self.engine = Engine.GetEngine()
        self.global_props = self.engine.props
        self.global_params = get_global_params()
    # def calc_something(self):
    #     print("Im calculating some things...")
    #     self.engine.props.freq = 75000
    #     print("After calculations i changed number of properties")

    # change frequency should be on radarLogic
    # def param_change(self, param):
        # self.engine.eventBroker.fireEvent("changed_freq", freq)

    def calc_dbf(self):
        num_of_rx = self.engine.objectRepository.getInstancesById("RxManager").get_num_of_nodes()
        result = mh.CalculateDBF(num_channels=num_of_rx * 48, num_beams=self.global_props.number_of_beams,
                            stack_center=self.global_props.beam_stack_center, spacing=self.global_props.beam_spacing,
                            sll=self.global_params.side_lobe_lvl, fc=self.global_props.frequency)

        self.global_params.dbf = result  # self.global_params should be changed to self.global_props
        self.global_props.new_dbf_ready = True
        self.global_props.new_dbf_ready = False

    def Initialize(self):
        logger.debug("Initialize")
        logger.info("Calculate beam forming matrix")
        # self.calc_dbf()

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
