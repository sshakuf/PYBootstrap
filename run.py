# ObjectRepository.py
import imports
import xml.etree.ElementTree as ET

from ObjectRepository import ObjectRepository


xmlData = """<data> 
    <Modules>
        <Module type="RadarLogic" id="TheOneAndOnly_RadarLogic" stamProp="myProp" ></Module>
        <Module type="RadarManager" id="TheOneAndOnly_RadarManager"></Module>
    </Modules>
</data>"""


if __name__ == "__main__":
    OR = ObjectRepository()
    OR.LoadModules("./Modules")
    # OR.loadConfiguration(xmlData)
    OR.loadConfigurationFromFile(
        imports.currentdir+"/configurations/conf1.xml")

    radarLogic = OR.getFirstInstance('RadarLogic')
    radarManager = OR.getFirstInstance('RadarManager')

    print(radarLogic.id)
    print(radarManager.id)

    x = 5
    x = x+3
