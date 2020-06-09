import functools

_engineComponentList = []

def cRegisterEngineComponent(Cls):
    class NewCls(object):
        def __init__(self,*args,**kwargs):
            _engineComponentList.append(self)

    return NewCls

def RegisterEngineComponent(func):
    @functools.wraps(func)
    def wrapper():  # this calles when our function calls
        # print("Something is happening before the function is called.")
        _engineComponentList.append(func)
        func()
        #print("Something is happening after the function is called.")
    return wrapper


@cRegisterEngineComponent
class T():
    def __init__(self):
        print("Initi T")
    def p(self):
        print("t")


print("start")
t = T()
t.p()
t2 = T()
t3 = T()



x=5
x+=1