from tools.EventBroker import RegisterListener
import Engine
import logging

logger = logging.getLogger(__name__)


@RegisterListener("Test")
def onTestEvent1():
    logger.debug("TEST")


class Gil:
    def __init__(self):
        logger.debug("I am small person")

    @RegisterListener("Test")
    def onTestEvent():
        logger.debug("TEST")

    def RegisterEvents(self):
        pass
        # Engine.GetEngine().eventBroker.SubscribeEvent(self, 'Test' Gil.onTestEvent)

        # class Node2:
        #     def __init__(self):
        #         self.id = "1"
        #
        #     def check_if_connected(self):
        #         print("Is connected")
        #
        #     def Run(self):
        #         if self.onBeforeRun():
        #             print("Father running")
        #             self.onAfterRun()
        #             return True
        #         return False
        #
        #     def Stop(self):
        #         #if self.onBeforeStop():
        #         print("Father stopping")
        #         #    self.onAfterStop()
        #         #    return True
        #         # return False
        #
        #     def onBeforeRun(self):
        #         return True
        #
        #     def onAfterRun(self):
        #         pass
        #
        #     def onBeforeStop(self):
        #         return True
        #
        #     def onAfterStop(self):
        #         pass
        #
        #
        # class RxNode2(Node2):
        #     def __init__(self):
        #         super().__init__()
        #         logger.debug("init")
        #
        #     def onBeforeRun(self):
        #         return True
        #
        #     def onAfterRun(self):
        #         pass
        #
        #     def onBeforeStop(self):
        #         print("Before stop at child")
        #         return True
        #
        #     def onAfterStop(self):
        #         print("After stop at child")
        #         pass
        #
        #     def Stop(self):
        #         print("Before stop at child")
        #         super().Stop()
        #         print("After stop at child")

        # rx_node = RxNode2()
        #
        # # rx_node.onBeforeStop()
        # rx_node.Stop()
        #
