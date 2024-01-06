import os
import subprocess
import shutil
from datetime import datetime

TEMP_FOLDER_PATH = ".\\temp"
ERROR_FOLDER_PATH = ".\\#ERROR"
ERROR_FILE_PATH = '.\\#ERRORS.txt'
MERGE_FILE_PATH = os.path.join(TEMP_FOLDER_PATH, "merge.txt")


IS_RUNNING = False

def createTemp():
    if not os.path.exists(TEMP_FOLDER_PATH):
        print(f'Created the temp folder')
        os.mkdir(TEMP_FOLDER_PATH)
    if not os.path.exists(ERROR_FOLDER_PATH):
        print(f'Created the error folder')
        os.mkdir(ERROR_FOLDER_PATH)
    

async def createProcessLine(id, settings):
    commandLine = ".\\jav-it.exe download"
    commandLine = " ".join([commandLine, "/c", settings["cookie_path"]])
    if settings["subscription_type"] != "None":
        commandLine = " ".join([commandLine, "/s", settings["subscription_type"]])
    commandLine = " ".join([commandLine, "/o", ".\\temp"])
    commandLine = " ".join([commandLine, "/server", "dmm"])
    commandLine = " ".join([commandLine, "/i", id])
    if settings["vr_download"]:
       commandLine = " ".join([commandLine, "/vr-content"]) 
    if settings["auto_parent_id"] != 'None':
        commandLine = " ".join([commandLine, "/p", id+settings["auto_parent_id"]])
    return commandLine

async def runCommandLine(commandLine):
    print(commandLine)
    if commandLine == "" or commandLine == None:
        return False
    output = subprocess.run(commandLine)
    if output.returncode == 0:
        return True
    else:
        return False

async def writeErr(err, id):
    with open(ERROR_FILE_PATH, "a") as f:
        f.write(f'[{datetime.now().strftime("%m/%d/%Y | %H:%M:%S")}]')
        f.write("\n")
        f.write(err)
        f.write("\n\n\n")
    with open('failedQueue.txt', "a") as f:
        f.write(id)
        f.write("\n")

async def download(queueBox, settings):
    global IS_RUNNING
    extension = settings["extension"]
    for id in await queueBox.getQueue():
        print('\n\n\n')
        if IS_RUNNING:
            #RUN JAV-IT
            commandLine = await createProcessLine(id=id, settings=settings)
            successful = await runCommandLine(commandLine=commandLine)
            if not successful:
                print(f"An error occured while donwloading the following id: {id}")
                await writeErr(f'An error occured while downloading the following id: {id}', id=id)
                await move(outputPath=ERROR_FOLDER_PATH)
                await queueBox.removeId(id=id)
                continue

            #manage the downloaded files
            if settings["merge"] and len(await getTempFiles()) > 1:
                successful, paths = await merge(outputPath=settings["download_path"], extension=settings["extension"])
            else:
                if extension == ".ts":
                    successful, paths = await move(outputPath=settings["download_path"])
                else:
                    successful, paths = await convert(outputPath=settings["download_path"], extension=settings["extension"])

            if not successful:
                print(f"A problem occured while managing the videos associated with this id: {id}, they will be moved in the error folder")
                await writeErr(err=f"A problem occured while managing the videos associated with this id: {id}", id=id)
                await move(outputPath=ERROR_FOLDER_PATH)
            else:
                if paths != None:
                    tempDuration = 0
                    tempFiles = await getTempFiles()
                    for file, name in tempFiles:
                        result = subprocess.run(["mediainfo", '--Output=Video;%Duration%', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        tempDuration += float(result.stdout.decode("utf-8").strip()) // 1000
                    finalDuration = 0
                    for file in paths:
                        result = subprocess.run(["mediainfo", '--Output=Video;%Duration%', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        finalDuration += float(result.stdout.decode("utf-8").strip()) // 1000
                    if finalDuration not in range(int(tempDuration)-len(tempFiles), int(tempDuration)+len(tempFiles)):
                        print(f"Duration doesn't match for downloaded and converted/merged files, id: {id}")
                        await writeErr(f"Duration doesn't match for downloaded and converted/merged files, id: {id}", id=id)
                        await move(ERROR_FOLDER_PATH)
                        for file in paths:
                            os.remove(file)
                        continue
                    else:
                        print(f'Duration matches')
            print(f'Finished downloading for the following id: {id}')
            for file, name in await getTempFiles():
                os.remove(file)
            await queueBox.removeId(id=id)
        else:
            break
    IS_RUNNING = False

async def getTempFiles():
    fileList = []
    for file in os.listdir(TEMP_FOLDER_PATH):
        filePath = os.path.join(TEMP_FOLDER_PATH, file)
        fileList.append((filePath, file))
    fileList.sort(key=sortParts)
    print(fileList)
    return fileList

async def move(outputPath):
    for file, name in await getTempFiles():
        destinationPath = os.path.join(outputPath, name)
        shutil.move(file, destinationPath)
    return True, None

async def convert(outputPath, extension):
    outputPaths = []
    for file, name in await getTempFiles():
        fileName = name.split(".")[0]
        outputPathSingle = os.path.join(outputPath, fileName + extension)
        outputPaths.append(outputPathSingle)
        commandLine = " ".join(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", file, "-c", "copy", outputPathSingle])
        successful = await runCommandLine(commandLine=commandLine)
    return successful, outputPaths

async def merge(outputPath, extension):
    for file, name in await getTempFiles():
        with open(MERGE_FILE_PATH, "a") as f:
            print(file)
            f.write("file '" + name + "'")
            f.write("\n")
    
    newName = name.split("_")
    newName.pop(-1)
    newName = "".join(newName)
    outputPath = os.path.join(outputPath, newName + extension)
    commandLine = " ".join(["ffmpeg", "-y", "-hide_banner", "-v", "error", "-f", "concat",
                                "-safe", "0", "-i", MERGE_FILE_PATH, "-c", "copy", outputPath])
    successful = await runCommandLine(commandLine=commandLine)
    os.remove(MERGE_FILE_PATH)
    return successful, [outputPath]

createTemp()

def sortParts(fileName):
    try:
        if "_" not in fileName[1]:
            return 0
        else:
            return int(fileName[1].split("_")[-1].split(".")[0])
    except:
        return 0