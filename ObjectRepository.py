# ObjectRepository.py
from xml.dom import minidom


class ObjectRepository:

    def __init__(self):
        commands = {}

    def LoadRestApiModules(self):
        for file in os.listdir('.'):
            lowerfile = file.lower()
            # print(lowerfile)
            if lowerfile.startswith('rest') and lowerfile.endswith('.py'):
                module = __import__(file.strip('.py'))
                if 'Initialize' in dir(module):
                    getattr(module, 'Initialize')()
                #print ('initializing Rest API from ' + file)
                InitializeRestAPI(module)

    def InitializeRestAPI(self, inModule):
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
