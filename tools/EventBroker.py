# EventBroker
from dotmap import DotMap
import functools
from tools import ObjectRepository

# takes a function (not in a class)


def RegisterListener(name):
    def imy_decorator(func):  # this is global when a new object is created
        ObjectRepository.GetObjectRepository().instances.eventBroker.subscribeEvent(name, func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # this calles when our function calls
            #print("Something is happening before the function is called.")
            func(*args, **kwargs)
            #print("Something is happening after the function is called.")
        return wrapper
    return imy_decorator


class EventBroker:

    def __init__(self):
        self.events = {}

        self.subscribeEvent("ObjectCreatedEvent",
                            "onObjectCreated", self)

    def onObjectCreated(self, inData):
        if hasattr(inData["obj"], 'RegisterEvents'):
            func = getattr(inData["obj"], 'RegisterEvents')
            func()

    def registerEvent(self, name):
        if name not in self.events.keys():
            self.events[name] = []

    # subscribe is used for registering also if the key is nor registered.
    def subscribeEvent(self, name, handler, obj=None):
        if name not in self.events.keys():
            self.events[name] = []
        self.events[name].append({"func": handler, "obj": obj})

    # def subscribeEvent(self, name, handler):
    #     if name not in self.events.keys():
    #         self.events[name] = []
    #     self.events[name].append({"func": handler, "obj": None})

    def fireEvent(self, *args, **kwargs):
        # def fireEvent(self, name, **kwargs):
        name, *data = args
        if name in self.events.keys():
            for handler in self.events[name]:
                if handler["obj"] != None:
                    func = getattr(handler["obj"], handler["func"])
                    func(*data)
                else:
                    handler["func"](*data)


class NotificationProps(DotMap):
    def __init__(self, *args, **kwargs):
        super(NotificationProps, self).__init__(*args, **kwargs)
        # self.eventBroker = args[0]

    def __setitem__(self, k, v):
        oldVal = None
        if k != "eventBroker":
            if k in self._map:
                oldVal = self[k]
            self.eventBroker.fireEvent("PropertyBeforeChange", {
                "Name": k, "oldVal": oldVal, "newVal": v})
            retVal = super(NotificationProps, self).__setitem__(k, v)
            self.eventBroker.fireEvent("PropertyChanged", {
                "Name": k, "oldVal": oldVal, "newVal": v})
        else:
            retVal = super(NotificationProps, self).__setitem__(k, v)
        return retVal

    def __getitem__(self, k):
        return super(NotificationProps, self).__getitem__(k)
# broker = EventBroker()


# def repeat(_func=None, *, name=""):
#     def decorator_repeat(func):
#         @functools.wraps(func)
#         def wrapper_repeat(*args, **kwargs):
#             for _ in range(num_times):
#                 value = func(*args, **kwargs)
#             return value
#         return wrapper_repeat

#     if _func is None:
#         return decorator_repeat
#     else:
#         return decorator_repeat(_func)
