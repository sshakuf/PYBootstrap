# ObjectRepository.py
import sys
import os
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

sys.path.insert(0, parentdir + '/tools')
sys.path.insert(0, parentdir + '/logic')

sys.path.insert(0, currentdir + '/Modules')


import xml.etree.ElementTree as ET

xmlData = """<data> 
    <Modules>
        <Module type="RadarLogic" name="item1"></Module>
        <Module type="RadarManager" name="item2"></Module>
    </Modules>
</data>"""

class ObjectRepository:

    def __init__(self):
        self.objectTypes = {}
        self.instances = {}

    def loadConfigurationFromFile(self, inFile):
        tree = ET.parse('country_data.xml')
        root = tree.getroot()  
        self.parseConfiguration(root)

    def loadConfiguration(self, instring):
        root = ET.fromstring(xmlData)
        self.parseConfiguration(root)

    def parseConfiguration(self, root):
        items = root.find('Modules')
        for item in items:
            print(item.attrib)
            for key in item.attrib:
                print (key, item.attrib[key])

    def LoadModules(self, inPath = '.'):
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

    def InitializeModules(self, inModule):
        # find all functions that starts with REST in this module
        x = dir(inModule)
        for func in dir(inModule):
            if func.startswith('R_'):
                command = func[2:]
                defaultptr = getattr(inModule, func)
                getptr = None
                setptr = None
                functions = dir(inModule)
                if "Get_"+command in functions:
                    getptr = getattr(inModule, "Get_"+func[2:])
                if "Set_"+command in functions:
                    setptr = getattr(inModule, "Set_"+func[2:])
                self.AddRestEndPoint(command, defaultptr, getptr, setptr)
                # print ('Endpoint: ' + command)

    def AddType(self, inTypeName, inType, isSingleton):
        #TODO check type not exist... if so rase error
        self.objectTypes[inTypeName] = {'type': inType, 'isSingleton':isSingleton}

    def CreateInstance(self, inTypeName):
        if inTypeName in self.objectTypes:
            newObj = self.objectTypes[inTypeName]['type']()
            if inTypeName not in self.instances.keys():
                self.instances[inTypeName] = []
            self.instances[inTypeName].append(newObj)


    def getInstances(self, inTypeName):
        if inTypeName in self.instances.keys():
            return self.instances[inTypeName]
        return None

# LoadRestApiModules()


if __name__ == "__main__":
    OR = ObjectRepository()
    OR.LoadModules("./Modules")
    OR.loadConfiguration(xmlData)

