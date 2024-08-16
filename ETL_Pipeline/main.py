# ---------------------------------------------------------------------------- #
#                                 ETL pipeline                                 #
# ---------------------------------------------------------------------------- #
import os
import time, datetime
import requests
import json
# ------------------------- read available endpoints ------------------------- #
endPointsPath : str = os.path.join(os.path.dirname(__file__), "endPoints.json")
with open(endPointsPath, "r") as endPointsFile:
    endPoints = json.load(endPointsFile)
# ---------------------------------------------------------------------------- #
# -------------------------- functions to fetch data ------------------------- #
def getExchangeInformation(endpoint:str = "")->json:
    ctimeH : int = int(datetime.datetime.now().strftime("%H"))
    ctimeM : int = int(datetime.datetime.now().strftime("%M"))

    if ctimeM % 5 == 0: # update market status every 5 minutes
        try:
            response : json = ...
        except:
            print("websocket request error")

getExchangeInformation("hello")