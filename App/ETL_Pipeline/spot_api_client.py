# ---------------------------------------------------------------------------- #
#                            Binance REST API client                           #
# ---------------------------------------------------------------------------- #

import os
import json
import requests
import aiohttp
import asyncio
from datetime import datetime, timezone
from .database_utils import database_utils as mdb

appDataPath: str = os.path.join(os.path.dirname(__file__),)
endPointsPath: str = os.path.join(os.path.dirname(__file__), "endPoints.json")

class apiClient:
    '''
    Class that will consume all data from Binance and push it to the database.
    '''
    def __init__(self, api_key):
        # ---------------------------- instance variables ---------------------------- #
        self.key = api_key
        self.serverTime = None
        self.cTimeH, self.cTimeM, self.cTimeS = int(datetime.now().strftime("%H")), int(datetime.now().strftime("%M")), int(datetime.now().strftime("%S"))
        self.utcTime = datetime.now(timezone.utc)
        self.utcOffset = int(
            (datetime.now() - self.utcTime.replace(tzinfo=None)).total_seconds() / 3600
        )
        self.endPoints = None
        self.baseEndpoint = None
        self.clientStatus = None
        self.retryAfter = 0
        self.lastUpdate = {"exhangeInformation":[], "kLineData":[]}
        self.updatedTickers = []

        # ------------------------ get api config information ------------------------ #
        with open(endPointsPath, "r") as endPointsFile:
            self.endPoints = json.load(endPointsFile)

        # -------------------------- get available base url -------------------------- #
        for endPoint in self.endPoints["base"]:
            response = requests.get(endPoint)
            if response.status_code == 200:
                self.baseEndpoint = endPoint
                break
        if not self.baseEndpoint:
            print("Cannot get a valid base URL for REST API\n")

        # Initialize aiohttp ClientSession
        self.session = aiohttp.ClientSession()

    @property
    def currentTime(self):
        current_time = datetime.now()
        self.cTimeH = int(current_time.strftime("%H"))
        self.cTimeM = int(current_time.strftime("%M"))
        self.cTimeS = int(current_time.strftime("%S"))
        return current_time

    @staticmethod
    def coolDown(func):
        errorCodes = [418, 429]
        async def wrapper(self, *args, **kwargs):
            while True:
                try:
                    response = await func(self, *args, **kwargs)
                    if self.clientStatus in errorCodes:
                        print(f"Cooling down API requests... Sleeping for {self.retryAfter} seconds.")
                        await asyncio.sleep(int(self.retryAfter))
                    else:
                        return response
                except aiohttp.ClientError as e:
                    print(f"Client error occurred: {e}")
                    await asyncio.sleep(2)  # Retry after a delay on client error
        return wrapper

    @coolDown
    async def getServerTime(self):
        endPointInfo: str = self.endPoints["checkServerTime"]
        url: str = self.baseEndpoint + endPointInfo["url"]
        async with self.session.get(url) as response:
            response.raise_for_status()  # Ensure we handle HTTP errors
            self.serverTime = await response.json()
    
    @coolDown
    async def getExchangeInformation(self) -> dict:
        endPointInfo: dict = self.endPoints["exchangeStatus"]
        url = self.baseEndpoint + endPointInfo["url"]
        async with self.session.get(url) as response:
            self.clientStatus = response.status
            self.retryAfter = response.headers.get("Retry-After", 1)
            return await response.json()

    @coolDown
    async def getKlineData(self, asset: str, interval: str = "1m", limit: int = 1000):
        url = self.baseEndpoint + self.endPoints["kLineData"]["url"]
        params = {"symbol": asset, "interval": interval, "limit": limit}
        async with self.session.get(url, params=params) as response:
            self.clientStatus = response.status
            self.retryAfter = response.headers.get("Retry-After", 1)
            return await response.json()

    async def updateExchangeInfo(self):
        try:
            response : json = await self.getExchangeInformation()
            data : dict = response["symbols"]
            if not mdb.collectionExists("exchangeInformation"):
                mdb.createCollection("exchangeInformation", True, primaryKey="symbol")
                mdb.insertMany("exchangeInformation", data)
            else:
                mdb.updateMany("exchangeInformation", data)
        except Exception as e:
            print("apiClient: Problem updating exchange information,", e)
    
    async def fetchTicker(self, ticker, semaphore):
        async with semaphore:
            try:
                response : json = await self.getKlineData(ticker, interval="1m", limit=1000)
                data : dict = {"symbol" : ticker, "kLinePrice": response}
                if not mdb.collectionExists("kLineData"):
                    mdb.createCollection("kLineData", True, primaryKey="symbol")
                    mdb.insertMany("kLineData", [data])
                else:
                    mdb.updateMany("kLineData", [data])
            except Exception as e:
                print(f"apiClient: Problem updating {ticker} price data:", e)

        self.updatedTickers.append(ticker)

    async def updateKlineData(self):
        exchangeInfo = list(mdb.getExchanceInfo())
        tickers = [i["symbol"] for i in exchangeInfo if i["status"] == "TRADING"]
        semaphore = asyncio.Semaphore(100)
        #build task list
        updateTasks = [self.fetchTicker(ticker, semaphore=semaphore) for ticker in tickers]
        await asyncio.gather(*updateTasks)

    def setLastUpdate(self, ctime):
        return [int(ctime.strftime("%H")), int(ctime.strftime("%M")), int(ctime.strftime("%S"))]

    async def run(self):
        while True:
            ctime = self.currentTime
            if self.cTimeM % 5 == 0:
                last = self.lastUpdate.get("exhangeInformation", None)
                if (last and last[1] != self.cTimeM) or not last:
                    print(f"apiClient : Updating Exchange Information data at : {self.cTimeH}:{self.cTimeM}:{self.cTimeS}", flush=True)
                    self.lastUpdate["exhangeInformation"] = self.setLastUpdate(ctime)
                    await self.updateExchangeInfo()
            if self.cTimeM % 1 == 0:
                last = self.lastUpdate.get("kLineData", None)
                if (last and last[1] != self.cTimeM) or not last:
                    print(f"apiClient : Updating kline price data at : {self.cTimeH}:{self.cTimeM}:{self.cTimeS}", flush=True)
                    self.lastUpdate["kLineData"] = self.setLastUpdate(ctime)
                    await self.updateKlineData()
                    print(f"{len(self.updatedTickers)} updated symbols\n")
            
            self.updatedTickers = []
            await asyncio.sleep(1)

    async def close(self):
        await self.session.close()

if __name__ == "__main__":
    pass
