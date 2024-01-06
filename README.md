## Description
The script allows to process a queue directly from a .txt file or from the GUI inputs, it does support VR option, subscriptions download (with all the subs included), merge/convert videos directly after a download is completed and move them to another location/drive, the possibility to generate a queue from a DMM URL.

## Installation for the script
1. Install the latest python version from: https://www.python.org/downloads/ (tick add to PATH option)
2. Install the python depencies, by running this command on CMD: pip install -r requirements.txt
3. Download latest CLI version of MediaInfo from here: https://mediaarea.net/it/MediaInfo/Download/Windows
4. Exctract the folder to C:\mediainfo (create the folder)
5. Add MediaInfo to Windows PATH Enviroment Variables, if you don't know how to do it follow this guide: https://www.educative.io/answers/how-to-add-an-application-path-to-system-environment-variables
6. Insert into the same folder of the script jav-it.exe (latest Patreon version of jav-it, https://jav-it.itch.io/jav-it).
7. Run the script using: python GUI.py

## Functions:
-`DOWNLOAD DIRECTORY`: insert the path you want the final file to be transfered after the download is completed and the conversion/merge it's done (if enabled).

-`COOKIE PATH`: select the file extracted with https://addons.mozilla.org/it/firefox/addon/cookies-txt/ from DMM, or you can generate the cookie directly with the script (only for DMM subscription account).

-`QUEUE PATH`: select the file location where the queue will be saved during the batch download or imported.

-`DOWNLOAD VR VIDEOS`: enable this option ONLY if the queue contains VR videos, don't use if they are mixed with normal videos, do 1 type of batch at the time.

-`MERGE VIDEOS`: if enabled when multiparts videos are downloaded, they will be merged into a single file, using FFMPEG remux (without loss of quality).

-`SUBSCRIPTION TYPE`: option menu that allows you to pick a subscription type, obviously you need to have an account with that subscription active.

-`VIDEO EXTENSION`: allows to choose if you want the videos to be converted, after the download is completed, to mp4 or mkv, if you leave .ts (default) they won't be converted, the conversion use FFMPEG remux, no quality loss.

-`AUTO PARENT ID`: option menu with different type of parent id suffix, default is none, but if you are using a subscription I suggest to use dl6, if you are downloading a 4K video use dl7, if you are downloading old videos and dl6 didn't work use dl or none, in some cases VR videos will require parent ID (dl7) to start.

-`GENERATE QUEUE`: insert a search url or an URL containing the standard pagination of dmm, example: https://www.dmm.co.jp/monthly/premium/-/list/search/=/sort=date/?searchstr=84mild, it will grab all the contentids from all the pages and insert them in the queue.txt file (1 per line) that will be ready to be imported into the queue.

-`IMPORT QUEUE AND SAVE QUEUE`: it will import from the queue path all the contentids to download, 1 per line, you can also change/add/remove them directly from the GUI, the save button will save the ids inserted/edited in the GUI to the queue file path.

-`START/STOP DOWNLOAD`: the download will start using the settings inserted in the GUI, downloading from the queue top to bottom ids, after each video is downloaded the respective id will be removed from the queue and the file will be updated, if you stop the download it will continue the ongoing download and stop before going to the next one.

## License
GNU GPLv3
