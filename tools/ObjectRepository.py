# ObjectRepository.py
# from tools.EventBroker import EventBroker
import logging
from dotmap import DotMap

import xml.etree.ElementTree as ET
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

sys.path.insert(0, parentdir + '/tools')
sys.path.insert(0, parentdir + '/logic')

sys.path.insert(0, currentdir + '/../Modules')

logger = logging.getLogger(__name__)


xmlData = """<data> 
    <Modules>
        <Module type="RadarLogic" id="TheOneAndOnly_RadarLogic" stamProp="myProp" ></Module>
        <Module type="RadarManager" id="TheOneAndOnly_RadarManager"></Module>
    </Modules>
</data>"""


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class ObjectRepository(Singleton):

    def __init__(self):
        self._objectTypes = {}
        self._instances = {}
        self.instances = DotMap(self._instances)
        self.eventBroker = None

    def loadConfigurationFromFile(self, inFile):
        tree = ET.parse(inFile)
        root = tree.getroot()
        self.parseConfiguration(root)

    def loadConfiguration(self, instring):
        root = ET.fromstring(xmlData)
        self.parseConfiguration(root)

    def parseConfiguration(self, root):
        items = root.find('Modules')
        for item in items:
            # print(item.attrib)
            instance = self.CreateInstance(item.attrib['type'])
            for key in item.attrib:
                if key != 'type':
                    instance.__setattr__(key, item.attrib[key])
                print(key, item.attrib[key])

    def LoadModules(self, inPath='.'):
        for file in os.listdir(inPath):
            lowerfile = file.lower()
            # print(lowerfile)
            if lowerfile.endswith('.py'):
                module = __import__(file.strip('.py'))
                for func in dir(module):
                    if not func.startswith("_"):
                        obj = getattr(module, func)
                        if isinstance(obj, type):
                            print(f"Class found {func} in module {file}")
                            self.AddType(func, obj, False)

    def AddType(self, inTypeName, inType, isSingleton):
        # TODO check type not exist... if so rase error
        self._objectTypes[inTypeName] = {
            'type': inType, 'isSingleton': isSingleton}

    def CreateInstance(self, inTypeName):
        if inTypeName in self._objectTypes:
            newObj = self._objectTypes[inTypeName]['type']()
            self.AddInstance(inTypeName, newObj)
            logger.info("Object Created " + inTypeName)
            self.eventBroker.fireEvent("ObjectCreatedEvent", {
                                       "TypeName": inTypeName, "obj": newObj})
            return newObj

    def AddInstance(self, inTypeName, newObj):
        if inTypeName not in self._instances.keys():
            self._instances[inTypeName] = []
        self._instances[inTypeName].append(newObj)
        self.instances[inTypeName] = newObj

    def getInstancesById(self, inIdName):
        for objs in self._instances.keys():
            for obj in self._instances[objs]:
                if hasattr(obj, "id"):
                    if getattr(obj, "id") == inIdName:
                        return obj
        return None

    def getInstances(self, inTypeName):
        if inTypeName in self._instances.keys():
            return self._instances[inTypeName]
        return None

    def getFirstInstance(self, inTypeName):
        if inTypeName in self._instances.keys():
            return self._instances[inTypeName][0]
        return None

    def getInstancesByType(self, inType):
        retVal = []
        for typeName in self._instances.keys():
            for obj in self._instances[typeName]:
                if isinstance(obj, inType):
                    retVal.append(obj)
        return retVal

# LoadRestApiModules()


_objectRepository = ObjectRepository()


def GetObjectRepository():
    return _objectRepository


if __name__ == "__main__":
    OR = ObjectRepository()
    OR.LoadModules("./Modules")
    OR.loadConfiguration(xmlData)

    radarLogic = OR.getFirstInstance('RadarLogic')
    radarManager = OR.getFirstInstance('RadarManager')

    print(radarLogic.id)
    print(radarManager.id)

    x = 5
    x = x+3
