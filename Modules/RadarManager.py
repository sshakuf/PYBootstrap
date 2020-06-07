import EventBroker
import logging

logger = logging.getLogger(__name__)


class RadarManager:
    def __init__(self):
        logger.debug("init")

    @EventBroker.RegisterListener("Test2")
    def onEventTest2(a):
        logger.debug("onEventTest2")
