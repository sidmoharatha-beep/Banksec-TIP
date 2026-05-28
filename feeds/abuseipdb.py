import os
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_API_KEY")
BASE_URL = "https://api.abuseipdb.com/api/v2"
HEADERS = {"Accept": "application/json", "Key": API_KEY}

def ingest():
    print("[AbuseIPDB] Starting ingestion...")
    resp = requests.get(f"{BASE_URL}/blacklist", headers=HEADERS,
                        params={"confidenceMinimum": 90, "limit": 500}, timeout=20)
    resp.raise_for_status()
    inserted = 0
    for entry in resp.json().get("data", []):
        ioc = {
            "source": "AbuseIPDB",
            "indicator": entry.get("ipAddress"),
            "type": "IPv4",
            "risk_score": int(entry.get("abuseConfidenceScore", 0)),
            "country": entry.get("countryCode"),
            "status": "active",
        }
        if not ioc_data_collection.find_one({"source": "AbuseIPDB", "indicator": ioc["indicator"]}):
            ioc_data_collection.insert_one(ioc)
            inserted += 1
            print(f"  [+] {ioc['indicator']:18s}  score={ioc['risk_score']}")
    print(f"[AbuseIPDB] Done – {inserted} new IPs inserted.\n")
    return inserted
