from pymongo import MongoClient
from elasticsearch import Elasticsearch
import json

# MongoDB Connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["threat_intelligence"]
mongo_collection = mongo_db["ioc_data"]

# Elasticsearch Connection
es = Elasticsearch("http://localhost:9200")

# Fetch all MongoDB documents
data = mongo_collection.find()

for doc in data:

    # Convert ObjectId to string
    doc["_id"] = str(doc["_id"])

    # Send data to Elasticsearch
    response = es.index(
        index="threat-intel",
        document=doc
    )

    print("Indexed:", response["result"])

print("Data transfer completed!")
