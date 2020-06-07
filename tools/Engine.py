from EventBroker import EventBroker
import DataStore
import ObjectRepository

import logging

logger = logging.getLogger(__name__)

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
        logger.info("Engine Init")

        self.objectRepository = ObjectRepository.GetObjectRepository()
        self.eventBroker = EventBroker()

        # add to ObjectFactory we can use in . notation
        self.objectRepository.AddInstance(
            "objectRepository", self.objectRepository)
        self.objectRepository.AddInstance("eventBroker", self.eventBroker)

    def LoadConfiguration(self, infile):
        logger.info("Loading Configuration %s" % infile)

        self.objectRepository.LoadModules("./Modules")
        # OR.loadConfiguration(xmlData)
        self.objectRepository.loadConfigurationFromFile(infile)

    def initialize(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass


_engine = Engine()


def GetEngine():
    return _engine
