import WorkThread

import logging

logger = logging.getLogger(__name__)


class Worker(WorkThread.WorkThread):
    def __init__(self):
        tools.WorkThread.WorkThread.__init__(self)
        logger.debug("Worker Init")

    def work(self):
        logger.debug("Worker Work")
