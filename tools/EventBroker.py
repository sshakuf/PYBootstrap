# EventBroker
import functools
from tools import ObjectRepository


def RegisterListener(name):
    def imy_decorator(func):  # this is global when a new object is created
        ObjectRepository.GetObjectRepository().instances.eventBroker.subscribeEvent(name, func)

        @functools.wraps(func)
        def wrapper():  # this calles when our function calls
            #print("Something is happening before the function is called.")
            func()
            #print("Something is happening after the function is called.")
        return wrapper
    return imy_decorator


class EventBroker:

    def __init__(self):
        self.events = {}

    def registerEvent(self, name):
        if name not in self.events.keys():
            self.events[name] = []

    # subscribe is used for registering also if the key is nor registered.
    def subscribeEvent(self, name, handler):
        if name not in self.events.keys():
            self.events[name] = []
        self.events[name].append(handler)

    def fireEvent(self, name, **kwargs):
        if name in self.events.keys():
            for handler in self.events[name]:
                handler(**kwargs)


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
