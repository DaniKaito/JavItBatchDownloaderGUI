import customtkinter as ctk
import tkinter
from tkinter import *
import asyncio
import threading
import downloader
from configManager import ConfigManager
from dmmScraper import Dmm
import psutil

dmm = Dmm()
configs = ConfigManager()
APPLICATION_NAME:str = "JAVIT BatchDownloader"
APPLICATION_APPEREANCE:str = "system"

def runAsync(targetFunction):
    threading.Thread(target=lambda loop: loop.run_until_complete(targetFunction), args=(asyncio.new_event_loop(),)).start()

class settingOptionMenu():
    def __init__(self, master, settingName, settingKey, options, row, column):
        self.settingKey = settingKey
        self.settingLabel = ctk.CTkLabel(master=master, text=settingName, font=("Robotodo", 15))
        self.settingLabel.grid(row=row, column=column, padx=5, pady=5)
        self.settingMenu = ctk.CTkOptionMenu(master=master, values=options,
                                             command= lambda x: runAsync(configs.modifySetting(key=self.settingKey,
                                                                                             value=self.settingMenu.get())))
        self.settingMenu.grid(row=row, column=column+1, padx=5, pady=5)
        self.settingMenu.set(configs.startSettings[settingKey])

class settingCheckBox():
    def __init__(self, master, settingName, settingKey, row, column):
        self.settingKey = settingKey
        self.settingLabel = ctk.CTkLabel(master=master, text=settingName, font=("Robotodo", 15))
        self.settingLabel.grid(row=row, column=column, padx=5, pady=5)
        self.checkBoxVar = BooleanVar(master)
        self.settingBox = ctk.CTkCheckBox(master=master, variable=self.checkBoxVar, text="",
                                          command= lambda: runAsync(configs.modifySetting(key=self.settingKey,
                                                                                            value=self.checkBoxVar.get())))
        self.settingBox.grid(row=row, column=column+1, padx=5, pady=5)
        self.checkBoxVar.set(value=configs.startSettings[self.settingKey])

#Basically a label with an entry to insert a path and a button to open the explorer and select that file
class settingPath():
    def __init__(self, master, settingName, settingKey, filters, row, column):
        self.settingKey = settingKey
        self.settingLabel = ctk.CTkLabel(master=master, text=settingName, font=("Robotodo", 15))
        self.settingLabel.grid(row=row, column=column, padx=5, pady=5)
        self.settingEntry = ctk.CTkEntry(master=master, placeholder_text="Insert File Path", width=300)
        self.settingEntry.grid(row=row, column=column+1, padx=5, pady=5)
        if filters != None:
            explorerCommand = lambda: self.askFile(filters=filters)
        else:
            explorerCommand = lambda: self.askDir()
            
        self.expolererBtn = ctk.CTkButton(master=master, text="Choose Path",
                                          command=explorerCommand)
        self.expolererBtn.grid(row=row, column=column+2)

        #Everytime you focus out the elements, it saves the setting
        self.settingEntry.bind("<Leave>", command=lambda x: runAsync(configs.modifySetting(key=self.settingKey,
                                                                                       value=self.settingEntry.get())))
        #Insert the setting loaded from the json file as initial one
        self.settingEntry.insert(0, configs.startSettings[self.settingKey])
    
    #open the explorer and select a file depending on the filters
    def askFile(self, filters):
        fileName = tkinter.filedialog.askopenfilename(filetypes=filters)
        if fileName == "":
            return
        self.settingEntry.delete(0, END)
        self.settingEntry.insert(0, fileName)
        runAsync(configs.modifySetting(key=self.settingKey, value=self.settingEntry.get()))
    
    def askDir(self):
        dirName = tkinter.filedialog.askdirectory()
        if dirName == "":
            return
        self.settingEntry.delete(0, END)
        self.settingEntry.insert(0, dirName)
        runAsync(configs.modifySetting(key=self.settingKey, value=self.settingEntry.get()))

class queueBox():
    def __init__(self, master, row, column):
        self.frame = ctk.CTkFrame(master=master)
        self.frame.grid(row=row, column=column, padx=5, pady=5)
        self.queueLabel = ctk.CTkLabel(master=self.frame, text="QUEUE",
                                       font=("Robotodo", 18))
        self.queueLabel.grid(row=0, column=0, padx=7, pady=5)
        self.textBox = ctk.CTkTextbox(master=self.frame, width=200, height=550)
        self.textBox.grid(row=1, column=0, padx=7, pady=5)
        self.queuePath = ""
        self.importQueueBtn = ctk.CTkButton(master=self.frame, text="Import Queue",
                                            command=lambda: runAsync(self.loadQueue()))
        self.importQueueBtn.grid(row=2, column=0, padx=7, pady=5)
        self.saveQueueBtn = ctk.CTkButton(master=self.frame, text="Save Queue",
                                            command=lambda: runAsync(self.saveQueue()))
        self.saveQueueBtn.grid(row=3, column=0, padx=7, pady=5)

    async def saveQueue(self, askFile=True):
        if askFile:
            filePath = tkinter.filedialog.asksaveasfile(initialfile="queue.txt",
                                             defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
            filePath = filePath.name
        else:
            filePath = await configs.getSetting(key='queue_path')
        rows = await self.getQueue()
        if filePath != None:
            with open(filePath, "w") as f:
                for row in rows:
                    f.write(row)
                    if row != rows[-1]:
                        f.write("\n")

    async def loadQueue(self, text=None):
        if text == None:
            with open(await configs.getSetting(key="queue_path"), "r") as f:
                text = f.read()
        self.textBox.delete("0.0", "end")
        self.textBox.insert("0.0", text)
    
    async def getQueue(self):
        text = self.textBox.get("0.0", "end")
        text = text.split("\n")
        text.pop(-1)
        return text

    async def removeId(self, id):
        currentQueue = await self.getQueue()
        currentQueue.remove(id)
        await self.loadQueue(text='\n'.join(currentQueue))
        await self.saveQueue(askFile=False)

class GUI():
    def __init__(self):
        self.MainWindow = self.setUpMainWindow()

        #SETTING TAB
        self.settingsFrame = ctk.CTkFrame(master=self.MainWindow)
        self.settingsFrame.grid(row=0, column=0, padx=10, pady=10)
        self.settingLabel = ctk.CTkLabel(master=self.settingsFrame, text="SETTINGS",
                                         font=("Robotodo", 21))
        self.settingLabel.grid(row=0, column=1, padx=5, pady=7)
        self.downloadPathSelector = settingPath(master=self.settingsFrame, settingName="Download Directory", settingKey="download_path", 
                                              filters=None, row=1, column=0)
        self.cookiePathSelector = settingPath(master=self.settingsFrame, settingName="Cookie Path", settingKey="cookie_path", 
                                              filters=[("txt files", "*.txt")], row=2, column=0)
        self.queuePathSelector = settingPath(master=self.settingsFrame, settingName="Queue Path", settingKey="queue_path",
                                             filters=[("txt files", "*.txt")], row=3, column=0)
        self.vrDownloadSelector = settingCheckBox(master=self.settingsFrame, settingName="Download VR Videos",
                                                  settingKey="vr_download", row=4, column=0)
        self.mergeVideosSelector = settingCheckBox(master=self.settingsFrame, settingName="Merge Videos",
                                                   settingKey="merge", row=5, column=0)
        self.subscriptioSelector = settingOptionMenu(master=self.settingsFrame, settingName="Subscription Type",
                                                     settingKey="subscription_type", options=["None", "premium", "alice", "avstation", "dream", "hhh", "kmp", "jukujo", "mania", "momotaroubb", "moodyz", "mousouzoku", "paradisetv", "playgirl", "s1", "shirouto", "sod", "vr"],
                                                     row=8, column=0)
        self.extensionSelector = settingOptionMenu(master=self.settingsFrame, settingName="Video Extension",
                                                     settingKey="extension", options=[".ts", ".mkv", ".mp4"],
                                                     row=9, column=0)
        self.parentIdSelector = settingOptionMenu(master=self.settingsFrame, settingName="Auto parent ID",
                                                     settingKey="auto_parent_id", options=["None","dl", "dl6", "dl7"],
                                                     row=10, column=0)
        
        #QUEUE TAB
        self.queueFrame = ctk.CTkFrame(master=self.MainWindow)
        self.queueFrame.grid(row=0, column=1, padx=10, pady=10, rowspan=3)
        self.queueTextBox = queueBox(master=self.queueFrame, row=0, column=0)

        #LINK TAB
        self.utilitiesFrame = ctk.CTkFrame(master=self.MainWindow)
        self.utilitiesFrame.grid(row=1, column=0, padx=10, pady=10)
        self.generateQueueLabel = ctk.CTkLabel(master=self.utilitiesFrame, text="GENERATE QUEUE",
                                                font=("Robotodo", 21))
        self.generateQueueLabel.grid(row=0, column=1, padx=35, pady=10)
        self.dmmUrlField = ctk.CTkEntry(master=self.utilitiesFrame, placeholder_text="Insert DMM URL", width=200)
        self.dmmUrlField.grid(row=1, column=1, padx=5, pady=5, rowspan=3)
        self.generateQueueBtn = ctk.CTkButton(master=self.utilitiesFrame, text="Generate Queue",
                                              command=lambda: runAsync(dmm.scrape(url=self.dmmUrlField.get(),
                                                                                  queuePath=self.queuePathSelector.settingEntry.get())))
        self.generateQueueBtn.grid(row=4, column=1, padx=5, pady=5)

        #RUN PROCESS TAB
        self.runFrame = ctk.CTkFrame(master=self.MainWindow)
        self.runFrame.grid(row=2, column=0, padx=10, pady=10)
        self.runButton = ctk.CTkButton(master=self.runFrame, text="Start Download",
                                       command=lambda: runAsync(self.startProcess()))
        self.runButton.grid(row=0, column=0, padx=5, pady=7)

        self.MainWindow.mainloop()

    async def saveDmmCredentials(self):
        await configs.modifySetting(key='dmm_video_url', value=self.dmmVideoUrlField.get())
        await configs.modifySetting(key='dmm_user', value=self.userNameField.get())
        await configs.modifySetting(key='dmm_password', value=self.passwordField.get())

    async def startProcess(self):
        await self.queueTextBox.saveQueue(askFile=False)
        runAsync(self.processButtonText())
        if downloader.IS_RUNNING:
            downloader.IS_RUNNING = False
            self.runButton.configure(text="Start Download")
        else:
            downloader.IS_RUNNING = True
            self.runButton.configure(text="Stop Download")
            runAsync(downloader.download(queueBox=self.queueTextBox, settings=await configs.loadJson()))
    
    async def processButtonText(self):
        while True:
            await asyncio.sleep(0.1)
            if downloader.IS_RUNNING:
                self.runButton.configure(text="Stop Download")
            else:
                self.runButton.configure(text="Start Download")

    #SETTING THE APPEREANCE OF THE WINDOW
    def setUpMainWindow(self):
        mainWindow = ctk.CTk()
        mainWindow._set_appearance_mode(APPLICATION_APPEREANCE)
        mainWindow.title(APPLICATION_NAME)
        rows = [0, 1]
        columns = [0, 1]
        for i in rows:
            mainWindow.rowconfigure(i, weight=1)
        for i in columns:
            mainWindow.columnconfigure(i, weight=1)
        return mainWindow


#FOR TESTING PURPOSE:
if __name__ == "__main__":
    g = GUI()