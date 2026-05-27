from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)

# Database
db = client["threat_intelligence"]

# Collections
ioc_data = db["ioc_data"]
threats = db["threats"]

# Create unique index for deduplication
threats.create_index("indicator", unique=True)
