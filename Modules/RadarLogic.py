import EventBroker

import logging

logger = logging.getLogger(__name__)


class RadarLogic:
    def __init__(self):
        logger.debug("RadarLogic init...")

    @EventBroker.RegisterListener("Test")
    def onEventTest(a):
        logger.debug("onEventTest")

    @EventBroker.RegisterListener("Test2")
    def onEventTest2(a):
        logger.debug("onEventTest2")
