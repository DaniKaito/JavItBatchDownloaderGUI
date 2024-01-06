from bs4 import BeautifulSoup
import requests
import asyncio

class Dmm():
    def __init__(self):
        self.cookies = {"age_check_done":"1"}
        self.urls = []
        self.ids = []
    
    async def getPages(self, url):
        self.urls = []
        r = requests.get(url, cookies=self.cookies, timeout=20)
        self.urls.append(url)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            terminalPage = soup.find("div", {"class":"list-boxcaptside list-boxpagenation"}).find("ul").find("li", {"class":"terminal"}).find("a")["href"]
            pageNum = int(terminalPage.split("/")[-2].split("=")[-1])
            url = url.split('/')
            urlSearchString = url[-1]
            url.pop(-1)
            for i in range(1, pageNum + 1):
                if i != 1:
                    pageNum = 'page=' + str(i)
                    newUrl = '/'.join(url + [pageNum] + [urlSearchString])
                    self.urls.append(newUrl)
        except Exception as e:
            try:
                pageNum = int(soup.find("div", {"class":"list-boxcaptside list-boxpagenation"}).find("ul").find_all("li")[-2].find("a").getText())
                url = url.split('/')
                urlSearchString = url[-1]
                url.pop(-1)
                for i in range(1, pageNum + 1):
                    if i != 1:
                        pageNum = 'page=' + str(i)
                        newUrl = '/'.join(url + [pageNum] + [urlSearchString])
                        self.urls.append(newUrl)
            except IndexError:
                pass

        print("Found a total of: " + str(len(self.urls)) + " pages to scrape.")
        print(self.urls)
    
    async def getIds(self):
        self.ids = []
        for url in self.urls:
            r = requests.get(url, cookies=self.cookies, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.find("div", {"class":"d-item"}).find_all("li"):
                try:
                    if item.parent["id"] == "list":
                        id = item.find("a")["href"].split("=")[-1].split("/")[0]
                        self.ids.append(id)
                except:
                    continue
        print("Found a total of " + str(len(self.ids))+ " id")
    
    async def writeIds(self, queuePath):
        with open(queuePath, "w") as f:
            for id in self.ids:
                f.write(id)
                f.write("\n")
        print("Successfully wrote the queue.txt file")
    
    async def scrape(self, url, queuePath):
        await self.getPages(url=url)
        await self.getIds()
        await self.writeIds(queuePath=queuePath)