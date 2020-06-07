import imports
import Engine


if __name__ == "__main__":
    # TODO: Get file name from args    https://www.geeksforgeeks.org/command-line-arguments-in-python/?ref=leftbar-rightbar
    engine = Engine.GetEngine()
    engine.LoadConfiguration(imports.currentdir+"/configurations/conf1.xml")

    print(engine.objectRepository.instances.RadarLogic)
    print(engine.objectRepository.instances.RadarManager)

    engine.objectRepository.instances.eventBroker.fireEvent('Test')

    x = 5
    x = x+3
