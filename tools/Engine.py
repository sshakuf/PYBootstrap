from EventBroker import EventBroker
import DataStore
import ObjectRepository

_engineComponentList = []


def AddEnginComponent(inObj):
    if inObj not in _engineComponentList:
        _engineComponentList.append(inObj)


def RemoveEnginComponent(inObj):
    if inObj in _engineComponentList:
        _engineComponentList.remove(inObj)


class EngineComponenet:
    def initialize(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class Engine:
    def __init__(self):
        self.objectRepository = ObjectRepository.GetObjectRepository()
        self.eventBroker = EventBroker()

        # add to ObjectFactory we can use in . notation
        self.objectRepository.AddInstance(
            "objectRepository", self.objectRepository)
        self.objectRepository.AddInstance("eventBroker", self.eventBroker)

    def LoadConfiguration(self, infile):
        self.objectRepository.LoadModules("./Modules")
        # OR.loadConfiguration(xmlData)
        self.objectRepository.loadConfigurationFromFile(infile)


_engine = Engine()


def GetEngine():
    return _engine
