import os
from datetime import datetime
from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

MONGO_URI  = os.getenv("MONGO_URI",  "mongodb://localhost:27017/")
MONGO_DB   = os.getenv("MONGO_DB",   "threat_intelligence")
ES_HOST    = os.getenv("ES_HOST",    "http://localhost:9200")
ES_INDEX   = "threat-intelligence"

mongo_client = MongoClient(MONGO_URI)
db           = mongo_client[MONGO_DB]
collection   = db["threats"]
es           = Elasticsearch(ES_HOST)

def generate_actions():
    for doc in collection.find():
        doc_id = str(doc.pop("_id"))  # Remove _id from body, use as ES doc id
        doc["synced_at"] = datetime.utcnow().isoformat()
        yield {
            "_index": ES_INDEX,
            "_id":    doc_id,
            "_source": doc,   # _id is NOT inside _source
        }

def sync():
    print("[ES Sync] Starting MongoDB → Elasticsearch sync...")

    # Delete and recreate index for clean sync
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
        print(f"[ES] Old index deleted.")

    es.indices.create(index=ES_INDEX, body={
        "mappings": {"properties": {
            "indicator":  {"type": "keyword"},
            "type":       {"type": "keyword"},
            "source":     {"type": "keyword"},
            "risk_score": {"type": "integer"},
            "country":    {"type": "keyword"},
            "status":     {"type": "keyword"},
            "synced_at":  {"type": "date"},
        }}
    })
    print(f"[ES] Index '{ES_INDEX}' created.")

    success, errors = helpers.bulk(es, generate_actions(),
                                   stats_only=False, raise_on_error=False)
    print(f"[ES Sync] Indexed: {success}  Errors: {len(errors)}")
    print("[ES Sync] Done.\n")
