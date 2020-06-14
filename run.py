import imports
from tools.Engine import *
import logging
import Logger
from Modules.RadarLogic import RadarLogic
from tools.EngineComponent import EngineComponent

Logger.SetupLogger()

logger = logging.getLogger(__name__)

def param_change(prop):
    print("param_change" + str(prop))
    if prop.get("Name") == "rx_FrameGen_N_Samples":
        print("From param_change, property changed is rx_FrameGen_N_Samples")
    if prop.get("Name") == "frequency":
        print("From param_change, property changed is frequency")


if __name__ == "__main__":
    logger.info("________Start_________Main_________")
    # TODO: Get file name from args    https://www.geeksforgeeks.org/command-line-arguments-in-python/?ref=leftbar-rightbar
    engine = GetEngine()
    engine.LoadConfiguration(imports.currentdir+"/configurations/conf1.xml")

    # print(engine.objectRepository.instances.RadarLogic)
    # print(engine.objectRepository.instances.RadarManager)
    # engine.eventBroker.subscribeEvent("PropertyBeforeChange", param_change)
    engine.Initialize()
    engine.Start()
    engine.Run()
    engine.Stop()

    engine.objectRepository.instances.eventBroker.fireEvent('Test')
    engine.objectRepository.instances.eventBroker.fireEvent('Test2')

    # test the usage
    print(engine.props.frequency)
    engine.props.rx_FrameGen_N_Samples = 112
    engine.props.frequency = 32132
    print(engine.props.frequency)

    # engine.props["s"] = 11
    # print(engine.props.get("s"))
    # engine.props.eventBroker.subscribeEvent("p", pp)
    # print(engine.props.eventBroker.fireEvent("p"))
    # print("S property: " + str(engine.props["s"]))

    x = 5
    x = x+3
