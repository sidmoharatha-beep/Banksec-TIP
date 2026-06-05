"""
elastic_sync.py  –  BankSec-TIP ELK Stack & Visualization Branch
Aditya Tamakhuwala

Syncs all normalised threat records from MongoDB → Elasticsearch.
Uses bulk indexing for performance and proper index mapping.

Pipeline position:
  MongoDB (threats)  →  elastic_sync.py  →  Elasticsearch (threat-intelligence)
"""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
from logs.logs import get_logger

load_dotenv()

logger = get_logger(__name__)

MONGO_URI = os.getenv("MONGO_URI",  "mongodb://localhost:27017/")
MONGO_DB  = os.getenv("MONGO_DB",   "threat_intelligence")
ES_HOST   = os.getenv("ES_HOST",    "http://localhost:9200")
ES_INDEX  = "threat-intelligence"

mongo_client = MongoClient(MONGO_URI)
db           = mongo_client[MONGO_DB]
collection   = db["threats"]
es           = Elasticsearch(ES_HOST)


def generate_actions():
    for doc in collection.find():
        doc_id = str(doc.pop("_id"))
        # Convert any non-serialisable ObjectId leftovers to str
        doc["synced_at"] = datetime.now(timezone.utc).isoformat()
        # Ensure false_positive field exists for new documents
        doc.setdefault("false_positive", False)
        doc.setdefault("blocked", False)
        yield {
            "_index": ES_INDEX,
            "_id":    doc_id,
            "_source": doc,
        }


def sync():
    logger.info("ES Sync: starting MongoDB → Elasticsearch sync...")

    # Recreate index for a clean, consistent sync
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
        logger.info("ES Sync: old index deleted.")

    es.indices.create(index=ES_INDEX, body={
        "mappings": {"properties": {
            "indicator":     {"type": "keyword"},
            "type":          {"type": "keyword"},
            "source":        {"type": "keyword"},
            "risk_score":    {"type": "integer"},
            "country":       {"type": "keyword"},
            "status":        {"type": "keyword"},
            "blocked":       {"type": "boolean"},
            "false_positive":{"type": "boolean"},
            "synced_at":     {"type": "date"},
        }}
    })
    logger.info("ES Sync: index '%s' created with mapping.", ES_INDEX)

    success, errors = helpers.bulk(
        es, generate_actions(),
        stats_only=False,
        raise_on_error=False,
    )
    logger.info("ES Sync: indexed=%d  errors=%d", success, len(errors))
    if errors:
        for err in errors[:5]:   # log first 5 only
            logger.warning("ES Sync error: %s", err)
    logger.info("ES Sync: done.")
