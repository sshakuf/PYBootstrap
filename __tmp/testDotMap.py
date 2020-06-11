from dotmap import DotMap


class EventDotMap(DotMap):

    def __setitem__(self, k, v):
        oldVal = None
        if k in self._map:
            oldVal = self[k]
        print("PropertyBeforeChange" + "Name: " + k +
              " newVal: " + str(v) + " oldVal:" + str(oldVal))
        val = super(EventDotMap, self).__setitem__(k, v)
        return val


x = EventDotMap()
x.s = 3
print(x.s)
x['s'] = 4
print(x.s)
