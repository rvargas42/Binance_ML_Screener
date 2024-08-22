# ---------------------------------------------------------------------------- #
#                        Utils Functions to Get DB data                        #
# ---------------------------------------------------------------------------- #

from pymongo import MongoClient
import os, json

client = MongoClient("mongodb://localhost:27017")
db = client["binance_screener"]

with open(os.path.join(os.path.dirname(__file__), "schemas.json"), "r") as schemas:
    db_schemas = json.load(schemas)[0]

def createCollection(name : str, customIndex : bool = False, *args):
    db.create_collection(name)
    if customIndex == True and args:
        collection = db[name]
        primaryKey = args[0]
        collection.create_index(primaryKey, unique=True)

def collectionExists(name):
    collections : list[str] = db.list_collection_names()
    if name in collections:
        return True
    else:
        return False

def collectionQuery(name : str, query : dict):
    if collectionExists(name):
        collection = db[name]
        data = collection.find(query)
        return data
    else:
        print("No collection named ", name)

def filteredFields(data : dict, requiredFields) -> dict:
    filteredData = {item : data.get(item) for item in requiredFields}
    return filteredData

def insertMany(name : str, data : list[dict]):
    collection = db[name]
    collection.insert_many(data)

def getExchanceInfo():
    '''
    Returns data with available symbols
    '''
    collName = "exchangeInformation"
    collection = db[collName]
    if collectionExists(collName) == False:
        createCollection(collName, True, "symbol")
    data = collection.find({})
    return data

if __name__ == "__main__":
    pass