from EventBroker import RegisterListener
import logging

logger = logging.getLogger(__name__)


class Gil:
    def __init__(self):
        logger.debug("I am small person")

    @RegisterListener("Test")
    def onTestEvent(self):
        logger.debug("TEST")
