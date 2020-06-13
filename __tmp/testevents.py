import functools
from inspect import getcallargs

_engineComponentList = []


def cRegisterEngineComponent(Cls):
    class NewCls(object):
        def __init__(self, *args, **kwargs):
            _engineComponentList.append(self)

    return NewCls


def RegisterEngineComponent(func):
    print("xxxx is happening before the function is called.")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # this calles when our function calls
        print("Something is happening before the function is called.")
        _engineComponentList.append(func)
        func(*args, **kwargs)
        print("Something is happening after the function is called.")
    return wrapper


class T():
    def __init__(self):
        self.name = ""
        print("Initi T")

    @cRegisterEngineComponent
    def p(self):
        print("name=" + self.name)

    @RegisterEngineComponent
    def p2(self, x):
        print("name=" + self.name + x)


@RegisterEngineComponent
def zzz():
    print("zzz")


print("start")
t = T()
t.p()
t2 = T()
t3 = T()
t.name = "1"
t2.name = "2"
t3.name = "3"

t.p()
t2.p()
t3.p()

t.p2("xxx")
zzz()

x = 5
x += 1
