from pymongo import MongoClient
from elasticsearch import Elasticsearch
import json

# MongoDB Connection
mongo_client = MongoClient("mongodb://localhost:27017/")

# Database name
db = mongo_client["banksec_tip"]

# Collection name
collection = db["threat_feeds"]

# Elasticsearch Connection
es = Elasticsearch("http://localhost:9200")

# Fetch MongoDB data
data = collection.find()

# Push data to Elasticsearch
for document in data:

    # Convert ObjectId to string
    document["_id"] = str(document["_id"])

    # Insert into Elasticsearch
    es.index(
        index="threat-intelligence",
        document=document
    )

print("Data successfully pushed to Elasticsearch!")
