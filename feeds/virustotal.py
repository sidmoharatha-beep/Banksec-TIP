import os
import time
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()
API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
BASE_URL = "https://www.virustotal.com/api/v3"
HEADERS = {"x-apikey": API_KEY}

def enrich(limit=10):
    print(f"[VirusTotal] Starting enrichment (limit={limit})...")
    cursor = ioc_data_collection.find(
        {"type": "IPv4", "vt_malicious": {"$exists": False}}, limit=limit)
    enriched = 0
    for doc in cursor:
        ip = doc.get("indicator")
        if not ip:
            continue
        print(f"  [~] Querying VT for {ip} ...")
        resp = requests.get(f"{BASE_URL}/ip_addresses/{ip}", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            attrs = resp.json().get("data", {}).get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})
            ioc_data_collection.update_one({"_id": doc["_id"]}, {"$set": {
                "vt_malicious": stats.get("malicious", 0),
                "vt_suspicious": stats.get("suspicious", 0),
            }})
            enriched += 1
            print(f"      malicious={stats.get('malicious',0)}")
        time.sleep(15)
    print(f"[VirusTotal] Done – {enriched} records enriched.\n")
    return enriched
