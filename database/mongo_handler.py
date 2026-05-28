"""
mongo_handler.py
Centralised MongoDB connection for BankSec-TIP.
All collections are defined here so every module imports from ONE place.
"""

import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.getenv("MONGO_DB",  "threat_intelligence")

client = MongoClient(MONGO_URI)
db     = client[MONGO_DB]

# Raw feed data (all sources write here)
ioc_data_collection = db["ioc_data"]

# Normalised, deduplicated threats (IOC extractor writes here)
threats_collection  = db["threats"]

# Backward-compatible alias used by older modules
collection = threats_collection

# ── Indexes (idempotent – safe to call repeatedly) ──────────────────────────
ioc_data_collection.create_index([("name",      ASCENDING)], unique=False)
ioc_data_collection.create_index([("source",    ASCENDING)])
threats_collection.create_index( [("indicator", ASCENDING)], unique=True, sparse=True)
threats_collection.create_index( [("risk_score",ASCENDING)])
