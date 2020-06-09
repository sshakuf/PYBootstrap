import EventBroker
from EngineComponent import EngineComponent
import tools.Engine as Engine
import tools.ObjectRepository
from enum import Enum
import logging

logger = logging.getLogger(__name__)

import Modules.Helpers.eNums as eNums


class NodeManager():
    def __init__(self):
        logger.debug("init")
        self.numOfNodes = "1"
        self._nodes = []
        self._nodeTypeName = ""
        self._state= eNums.RuningState.NOTINITIALIZED

    def getState(self):
        return self._state

    def Initialize(self):
        logger.debug("Initialize")
        self.engine = Engine.GetEngine()
        if self.onBeforeInitialized():
            for nodeId in range(0, int(self.numOfNodes)):
                node = self.engine.objectRepository.CreateInstance(self._nodeTypeName)
                node.id = nodeId
                node.Initialize()
                self._nodes.append(node)
            self._state= eNums.RuningState.INITIALIZED
            self.onAfterInitialized()
            return True
        return False

    def Start(self):
        if self.onBeforeStart():
            for nodeId in range(0, int(self.numOfNodes)):
                self._nodes[nodeId].Start()
            self.onAfterStart()
            self._state = eNums.RuningState.STARTED
            return True
        return False

    def Run(self):
        if self.onBeforeRun():
            for nodeId in range(0, int(self.numOfNodes)):
                self._nodes[nodeId].Run()
            self.onAfterRun()
            self._state = eNums.RuningState.RUNNING
            return True
        return False

    def Stop(self):
        if self.onBeforeStop():
            for nodeId in range(0, int(self.numOfNodes)):
                self._nodes[nodeId].Stop()
            self.onAfterStop()
            self._state = eNums.RuningState.STOPPED
            return True
        return False

    def onBeforeInitialized(self):
        return True
    def onAfterInitialized(self):
        pass
    def onBeforeStart(self):
        return True
    def onAfterStart(self):
        pass
    def onBeforeRun(self):
        return True
    def onAfterRun(self):
        pass
    def onBeforeStop(self):
        return True
    def onAfterStop(self):
        pass

