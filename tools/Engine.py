from EventBroker import EventBroker, NotificationProps
import DataStore
from EngineComponent import EngineComponent
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


class Engine:
    def __init__(self):
        logger.info("Engine Init")

        self.objectRepository = ObjectRepository.GetObjectRepository()
        self.eventBroker = EventBroker()
        #self.props = NotificationProps(self.eventBroker)

        # add to ObjectFactory we can use in . notation
        self.objectRepository.AddInstance(
            "objectRepository", self.objectRepository)
        self.objectRepository.AddInstance("eventBroker", self.eventBroker)

    def LoadConfiguration(self, infile):
        logger.info("Loading Configuration %s" % infile)

        self.objectRepository.LoadModules("./Modules")
        # OR.loadConfiguration(xmlData)
        self.objectRepository.loadConfigurationFromFile(infile)

    def Initialize(self):
        componenets = self.objectRepository.getInstancesByType(
            EngineComponent)
        for component in componenets:
            component.Initialize()

    def Start(self):
        componenets = self.objectRepository.getInstancesByType(
            EngineComponent)
        for component in componenets:
            component.Start()

    def Run(self):
        componenets = self.objectRepository.getInstancesByType(
            EngineComponent)
        for component in componenets:
            component.Run()

    def Stop(self):
        componenets = self.objectRepository.getInstancesByType(
            EngineComponent)
        for component in componenets:
            component.Stop()

_engine = Engine()


def GetEngine():
    return _engine
