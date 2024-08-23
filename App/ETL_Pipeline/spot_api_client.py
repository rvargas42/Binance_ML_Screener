# ---------------------------------------------------------------------------- #
#                            Binance REST API client                           #
# ---------------------------------------------------------------------------- #
import os
import time, datetime
import requests
import json
from ETL_Pipeline.database_utils import database_utils as mdb
from datetime import datetime, timezone, time

appDataPath : str = os.path.join(os.path.dirname(__file__),)

class apiClient:
    '''
    class that will consume all data from binance and push it to a database
    '''
    endPointsPath : str = os.path.join(os.path.dirname(__file__), "endPoints.json")
    def __init__(self, api_key):
        # ---------------------------- instance variables ---------------------------- #
        self.key = None
        self.serverTime : int = None
        self.cTime : time = datetime.now()
        self.utcTime: time = datetime.now(timezone.utc)
        self.utcOffset : int = int(
            (self.cTime - self.utcTime.replace(tzinfo=None)).total_seconds() / 3600
        )

        # ------------------------ get api config information ------------------------ #
        with open(self.endPointsPath, "r") as endPointsFile:
            self.endPoints = json.load(endPointsFile)
        # -------------------------- get available base url -------------------------- #
        for endPoint in self.endPoints["base"]:
            responseStatus = requests.get(endPoint).status_code
            print("Current base url: ", endPoint, "\n")
            if responseStatus == 200:
                self.baseEndpoint = endPoint
                break
        if not self.baseEndpoint:
            print("Cannot get a valid base url for REST API\n")

    async def getServerTime(self):
        endPointInfo : str = self.endPoints["checkServerTime"]
        url : str = self.baseEndpoint + endPointInfo["url"]
        self.serverTime = requests.get(url).json()["serverTime"]
        return self.serverTime

    async def getExchangeInformation(interval: int = 1) -> dict:
        ctimeM : int = int(datetime.now().strftime("%M"))
        endPointInfo : dict = self.endPoints["exchangeStatus"]
        if ctimeM % interval == 0: # update market status every { interval } minutes
            url = self.baseEndpoint + endPointInfo["url"]
            response = requests.get(url).json()["symbols"]
            if collectionExists("exchangeInformation") == False:
                createCollection("exchangeInformation", True, "symbol")
                insertMany("exchangeInformation", response)
            else:
                mdb.updateMany("exchangeInformation", response)

    async def getKlineData(asset: str, start, end):
        pass

    async def run(self):
        print("running apiClient")


def check_key(key: str):
    pass #TODO: make function to test api key with regex + request


if __name__ == "__main__":
    pass