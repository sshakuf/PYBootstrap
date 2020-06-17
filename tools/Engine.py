from tools.EventBroker import EventBroker, NotificationProps
import DataStore
import tools.DataStore
from tools.EngineComponent import EngineComponent
import tools.ObjectRepository as ObjectRepository
from Modules.Helpers.ReadWriteLock import *

import logging

logger = logging.getLogger(__name__)

global _engine
_engine = None


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Engine(Singleton):
    def __init__(self):
        logger.info("Engine Init")

        self.objectRepository = ObjectRepository.GetObjectRepository()
        self.eventBroker = EventBroker()
        self.objectRepository.eventBroker = self.eventBroker

        self.props = NotificationProps()
        self.props.eventBroker = self.eventBroker

        # add to ObjectFactory we can use in . notation
        self.objectRepository.AddInstance(
            "objectRepository", self.objectRepository)
        self.objectRepository.AddInstance(
            "eventBroker", self.eventBroker)

        self.reader_writer_lock = get_read_write_lock()

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


# Singleton engine
def GetEngine():
    global _engine
    if _engine == None:
        _engine = Engine()
    return _engine
