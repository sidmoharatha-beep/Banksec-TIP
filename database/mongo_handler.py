import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.getenv("MONGO_DB",  "threat_intelligence")

client = MongoClient(MONGO_URI)
db     = client[MONGO_DB]

ioc_data_collection = db["ioc_data"]
threats_collection  = db["threats"]
collection          = threats_collection

ioc_data_collection.create_index([("source", ASCENDING)])
