# ObjectRepository.py
import xml.etree.ElementTree as ET

xmlData = """<data> 
    <Modules>
        <Module type="RadarLogic" name="item1"></Module>
        <Module type="RadarManager" name="item2"></Module>
    </Modules>
</data>"""

class ObjectRepository:

    def __init__(self):
        objectTypes = {}

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
                if 'Initialize' in dir(module):
                    getattr(module, 'Initialize')()
                #print ('initializing Rest API from ' + file)
                InitializeRestAPI(module)

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

    def AddRestEndPoint(self, inCommand, inHandler, inGet=None, inSet=None):

        self.commands[inCommand] = {
            'default': inHandler, 'get': inGet, 'set': inSet}

    def Gethandler(self, inCommand, action):
        if inCommand in commands:
            # if commands[inCommand][action] == None:
            #     return commands[inCommand]['default']

            return self.commands[inCommand][action]
        return None

# LoadRestApiModules()


if __name__ == "__main__":
    OR = ObjectRepository()

    OR.loadConfiguration(xmlData)

