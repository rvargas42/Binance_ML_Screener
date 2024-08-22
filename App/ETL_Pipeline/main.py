# ---------------------------------------------------------------------------- #
#                                 ETL pipeline                                 #
# ---------------------------------------------------------------------------- #
import os
import time, datetime
import requests
import json
from .database_utils import collectionExists, createCollection, insertMany

# ------------------------- read available endpoints ------------------------- #
endPointsPath : str = os.path.join(os.path.dirname(__file__), "endPoints.json")
appDataPath : str = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "Data")
with open(endPointsPath, "r") as endPointsFile:
    endPoints = json.load(endPointsFile)
# ---------------------------------------------------------------------------- #
# -------------------------- functions to fetch data ------------------------- #

def check_key(key: str):
    pass #TODO: make function to test api key with regex + request

def getAvailableBaseEndpoint()->str:
    for baseEndPoint in endPoints["base"]:
        responseStatus = requests.get(baseEndPoint).status_code
        print("Current base url: ", baseEndPoint, "\n")
        if responseStatus == 200:
            return baseEndPoint
    print("Cannot Connect to API\n")
    return -1

def getExchangeInformation()->json:
    ctimeM : int = int(datetime.datetime.now().strftime("%M"))
    endPointInfo : dict = endPoints["exchangeStatus"]
    baseEndpoint : str = getAvailableBaseEndpoint()
    if ctimeM % 1 == 0: # update market status every 30 minutes
        url = baseEndpoint + endPointInfo["url"]
        response = requests.get(url).json()["symbols"]
        if collectionExists("exchangeInformation") == False:
            createCollection("exchangeInformation", True, "symbol")
            insertMany("exchangeInformation", response)
        # else:
        #     mdb.updateMany("exchangeInformation", response)




if __name__ == "__main__":
    pass