import EventBroker


class RadarLogic:
    def __init__(self):
        print("RadarLogic init...")

    @EventBroker.RegisterListener("Test")
    def onEventTest(a):
        print("RadarLogic, onEventTest")
