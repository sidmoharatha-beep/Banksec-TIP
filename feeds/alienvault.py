import os
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()
API_KEY = os.getenv("OTX_API_KEY")
BASE_URL = "https://otx.alienvault.com/api/v1"
HEADERS = {"X-OTX-API-KEY": API_KEY}

def ingest():
    print("[AlienVault] Starting ingestion...")
    url = f"{BASE_URL}/pulses/subscribed"
    inserted = 0
    page = 0
    while url and page < 3:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for pulse in data.get("results", []):
            for indicator in pulse.get("indicators", []):
                ioc = {
                    "source": "AlienVault_OTX",
                    "indicator": indicator.get("indicator"),
                    "type": indicator.get("type"),
                    "risk_score": 80,
                    "status": "active",
                }
                if not ioc_data_collection.find_one({"source": "AlienVault_OTX", "indicator": ioc["indicator"]}):
                    ioc_data_collection.insert_one(ioc)
                    inserted += 1
                    print(f"  [+] {ioc['type']:10s}  {ioc['indicator']}")
        url = data.get("next")
        page += 1
    print(f"[AlienVault] Done – {inserted} new IOCs inserted.\n")
    return inserted
