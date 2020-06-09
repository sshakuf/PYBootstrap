import EventBroker
from EngineComponent import EngineComponent
import tools.Engine as Engine
import tools.ObjectRepository
from enum import Enum
import logging

logger = logging.getLogger(__name__)

import Modules.Helpers.eNums as eNums


class Node():
    def __init__(self):
        logger.debug("init")
        self.id = "1"
        self._state= eNums.RuningState.NOTINITIALIZED

    def getState(self):
        return self._state

    def Initialize(self):
        self.engine = Engine.GetEngine()
        self._state= eNums.RuningState.INITIALIZED

    def Start(self):
        if self.onBeforeStart():
            self.onAfterStart()
            self._state = eNums.RuningState.STARTED
            return True
        return False

    def Run(self):
        if self.onBeforeRun():
            self.onAfterRun()
            self._state = eNums.RuningState.RUNNING
            return True
        return False

    def Stop(self):
        if self.onBeforeStop():
            self.onAfterStop()
            self._state = eNums.RuningState.STOPPED
            return True
        return False


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

