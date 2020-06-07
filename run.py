import imports
import Engine
import logging
import Logger

Logger.SetupLogger()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("________Start_________Main_________")
    # TODO: Get file name from args    https://www.geeksforgeeks.org/command-line-arguments-in-python/?ref=leftbar-rightbar
    engine = Engine.GetEngine()
    engine.LoadConfiguration(imports.currentdir+"/configurations/conf1.xml")

    print(engine.objectRepository.instances.RadarLogic)
    print(engine.objectRepository.instances.RadarManager)

    engine.Initialize()
    engine.Start()
    engine.Run()
    engine.Stop()

    engine.objectRepository.instances.eventBroker.fireEvent('Test')
    engine.objectRepository.instances.eventBroker.fireEvent('Test2')

    x = 5
    x = x+3
