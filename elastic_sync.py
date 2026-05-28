"""
elastic_sync.py  –  MongoDB threats  →  Elasticsearch
Aditya Tamakhuwala  |  ELK Stack Branch

Reads normalised threat records from MongoDB and indexes them into
Elasticsearch so Kibana can visualise them.

Pipeline position:
  MongoDB (threats)  →  elastic_sync.py  →  Elasticsearch  →  Kibana
"""

import os
from datetime import datetime
from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
MONGO_URI   = os.getenv("MONGO_URI",  "mongodb://localhost:27017/")
MONGO_DB    = os.getenv("MONGO_DB",   "threat_intelligence")
ES_HOST     = os.getenv("ES_HOST",    "http://localhost:9200")
ES_INDEX    = "threat-intelligence"
COLLECTION  = "threats"

# ── Connections ─────────────────────────────────────────────────────────────
mongo_client = MongoClient(MONGO_URI)
db           = mongo_client[MONGO_DB]
collection   = db[COLLECTION]

es = Elasticsearch(ES_HOST)


def create_index_if_needed():
    """Create the ES index with an explicit mapping (once)."""
    if es.indices.exists(index=ES_INDEX):
        return
    mapping = {
        "mappings": {
            "properties": {
                "indicator":   {"type": "keyword"},
                "type":        {"type": "keyword"},
                "source":      {"type": "keyword"},
                "risk_score":  {"type": "integer"},
                "country":     {"type": "keyword"},
                "status":      {"type": "keyword"},
                "synced_at":   {"type": "date"},
            }
        }
    }
    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"[ES] Index '{ES_INDEX}' created.")


def generate_actions():
    """Yield bulk-index actions from MongoDB documents."""
    for doc in collection.find():
        doc["_id"]       = str(doc["_id"])
        doc["synced_at"] = datetime.utcnow().isoformat()
        yield {
            "_index": ES_INDEX,
            "_id":    doc["_id"],
            "_source": doc,
        }


def sync():
    """Sync all threats from MongoDB to Elasticsearch."""
    print("[ES Sync] Starting MongoDB → Elasticsearch sync...")
    create_index_if_needed()

    success, errors = helpers.bulk(es, generate_actions(), stats_only=False,
                                   raise_on_error=False)
    print(f"[ES Sync] Indexed: {success}  Errors: {len(errors)}")
    if errors:
        for err in errors[:5]:
            print(f"  [!] {err}")
    print("[ES Sync] Done.\n")


if __name__ == "__main__":
    sync()
