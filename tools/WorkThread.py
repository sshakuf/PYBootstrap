import sys
import thread
import logging

logger = logging.getLogger(__name__)

def startWorking(worker):
    # print(tracker)
    if not worker.isWorking:
        worker.workThreadLogic()


class WorkThread:
    def __init__(self):
        self.isWorking = False
        pass

    def Start(self):
        if (self.isWorking == False):
            thread.start_new_thread(startWorking, (self,))

    def Stop(self):
        self.isWorking = False


    def workThreadLogic(self):
        self.beforeWork()

        self.isWorking = True

        while self.isWorking:
            self.work()

        self.afterWork()

        self.isWorking = False

    def work(self):
        pass

    def beforeWork(self):
        pass

    def afterWork(self):
        pass

