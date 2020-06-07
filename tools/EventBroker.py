# EventBroker

class EventBroker:

    def __init__(self):
        self.events = {}

    def registerRegister(name):
        if not self.events.has_key(name):
            self.events[name] = []

    # subscribe is used for registering also if the key is nor registered.
    def subscribeEvent(name, handler):
        if self.events.has_key(name):
            self.events[name] = []
        self.events[name].append(handler)

    def fireEvent(name, data=None):
        if self.events.has_key(name):
            for handler in self.events[name]:
                handler(data)


# broker = EventBroker()
