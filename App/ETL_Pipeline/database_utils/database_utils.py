# ---------------------------------------------------------------------------- #
#                        Utils Functions to Get DB data                        #
# ---------------------------------------------------------------------------- #

from pymongo import MongoClient
import os, json

client = MongoClient("mongodb://localhost:27017")
db = client["binance_screener"]

with open(os.path.join(os.path.dirname(__file__), "..", "schemas.json"), "r") as schemas:
    db_schemas = json.load(schemas)[0]

def createCollection(name : str, customIndex : bool = False, *args):
    db.create_collection(name)
    if customIndex == True and args:
        collection = db[name]
        primaryKey = args[0]
        collection.create_index(primaryKey, unique=True)

def collectionExists(name: bool):
    '''
    name: name of collection
    return value : (bool) : True or False if collection exists
    '''
    collections : list[str] = db.list_collection_names()
    if name in collections:
        return True
    else:
        return False

def collectionQuery(name : str, query : dict) -> dict:
    if collectionExists(name):
        collection = db[name]
        data = collection.find(query)
        return data
    else:
        print("No collection named ", name)

def filteredFields(data : dict, collName: str) -> dict:
    '''
    Filters a list of documents with given collection name.
    return : list of filtered data
    '''
    requiredFields = db_schemas[collName]["$jsonSchema"]["required"]
    for item in data:
        filteredElement = {field : item.get(field) for field in requiredFields}
        item = filteredElement
    return data

def insertMany(name : str, data : dict):
    collection = db[name]
    filteredData = filteredFields(data, name)
    collection.insert_many(data)

def updateMany(name: str, data : dict):
    collection = db[name]
    filteredData = filteredFields(data, name)
    try:
        for item in data:
            result = collection.update_many(filter={"symbol":item.get("symbol")}, upsert=True, update={"$set":item})
            if result.matched_count:
                print(f"MongoDB Client (Update): Symbol Exchange Info {item['symbol']}")
            elif result.upserted_id:
                print(f"MongoDB Client (Insert): Symbol Exchange Info {item['symbol']}")
    except Exception as e:
        print("MongoDB client: Problem updating exchange information,", e)

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