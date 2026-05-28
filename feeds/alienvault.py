"""
feeds/alienvault.py
AlienVault OTX – OSINT threat feed ingestion.

API key location: .env  →  OTX_API_KEY
"""

import os
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()

API_KEY = os.getenv("OTX_API_KEY")
if not API_KEY:
    raise EnvironmentError("[AlienVault] OTX_API_KEY not set in .env")

BASE_URL = "https://otx.alienvault.com/api/v1"
HEADERS  = {"X-OTX-API-KEY": API_KEY}


def fetch_pulses(max_pages: int = 3) -> list:
    """Fetch subscribed pulses (paginated)."""
    pulses = []
    url    = f"{BASE_URL}/pulses/subscribed"
    page   = 0

    while url and page < max_pages:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pulses.extend(data.get("results", []))
        url = data.get("next")   # None when last page
        page += 1

    return pulses


def ingest() -> int:
    """Pull OTX pulses and store raw IOC records in MongoDB."""
    print("[AlienVault] Starting ingestion...")
    pulses  = fetch_pulses()
    inserted = 0

    for pulse in pulses:
        for indicator in pulse.get("indicators", []):
            ioc = {
                "source":     "AlienVault_OTX",
                "pulse_name": pulse.get("name"),
                "indicator":  indicator.get("indicator"),
                "type":       indicator.get("type"),       # IPv4, domain, URL …
                "risk_score": 80,
                "tags":       pulse.get("tags", []),
                "status":     "active",
            }
            # Deduplicate by (source + indicator)
            exists = ioc_data_collection.find_one({
                "source":    ioc["source"],
                "indicator": ioc["indicator"],
            })
            if not exists:
                ioc_data_collection.insert_one(ioc)
                inserted += 1
                print(f"  [+] {ioc['type']:10s}  {ioc['indicator']}")

    print(f"[AlienVault] Done – {inserted} new IOCs inserted.\n")
    return inserted


if __name__ == "__main__":
    ingest()
