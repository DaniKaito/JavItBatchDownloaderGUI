import json
import os
import asyncio

class ConfigManager():
    def __init__(self):
        self.ConfigFilePath = ".\\configs.json"
        self.defaultConfigs = {"cookie_path":".\\cookies.txt",
                               "download_server":"dmm",
                               "subscription_type":"None",
                               "vr_download":False,
                               "download_path":".\\",
                               "extension":".ts",
                               "merge":False,
                               "queue_path":".\\queue.txt",
                               "auto_parent_id":"None"}
        #Used by the gui in order to fill the fields in the settings tab when first starting
        self.startSettings = {}
        self.createDefaultSettings()
    
    #create a json file with default settings (needed mostly when starting script for the first time or when resetting settings)
    def createDefaultSettings(self):
        if not os.path.exists(self.ConfigFilePath):
            print(f"Created config file")
            asyncio.new_event_loop().run_until_complete(self.saveJsonFile(settingsDict=self.defaultConfigs))
            self.startSettings = self.defaultConfigs
        else:
            print(f"Configs loaded")
            self.startSettings = asyncio.new_event_loop().run_until_complete(self.loadJson())

    
    #Dumps a dict into a json file
    async def saveJsonFile(self, settingsDict):
        with open(self.ConfigFilePath, "w") as f:
            json.dump(settingsDict, f, indent=2)

    #Returns json file as dict
    async def loadJson(self):
        with open(self.ConfigFilePath, "r") as f:
            settingsDict = json.load(f)
        return settingsDict
    
    async def getSetting(self, key, settingsDict=None):
        if settingsDict == None:
            settingsDict = await self.loadJson()
        return settingsDict[key]

    #Returns list of dict keys
    async def getDictKeysList(self, settingsDict=None):
        if settingsDict == None:
            settingsDict = await self.loadJson()
        keys = list(settingsDict.keys())
        return keys
    
    #Modifies a settings of a json file given the key and value and saves it
    async def modifySetting(self, key, value):
        settingsDict = await self.loadJson()
        if settingsDict[key] != value:
            settingsDict[key] = value
            await self.saveJsonFile(settingsDict=settingsDict)