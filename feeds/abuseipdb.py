"""
feeds/abuseipdb.py
AbuseIPDB – fetch recently reported malicious IPs.

API key location: .env  →  ABUSEIPDB_API_KEY
"""

import os
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()

API_KEY = os.getenv("ABUSEIPDB_API_KEY")
if not API_KEY:
    raise EnvironmentError("[AbuseIPDB] ABUSEIPDB_API_KEY not set in .env")

BASE_URL = "https://api.abuseipdb.com/api/v2"
HEADERS  = {
    "Accept":  "application/json",
    "Key":     API_KEY,
}


def fetch_blacklist(confidence_minimum: int = 90, limit: int = 500) -> list:
    """
    Fetch the AbuseIPDB blacklist.
    confidence_minimum: 0-100, higher = more certain malicious.
    limit: max IPs returned (max 10 000 on paid plan, 500 free).
    """
    params = {
        "confidenceMinimum": confidence_minimum,
        "limit":             limit,
    }
    resp = requests.get(f"{BASE_URL}/blacklist", headers=HEADERS,
                        params=params, timeout=20)
    resp.raise_for_status()
    return resp.json().get("data", [])


def ingest() -> int:
    """Pull blacklist and upsert into MongoDB."""
    print("[AbuseIPDB] Starting ingestion...")
    entries  = fetch_blacklist()
    inserted = 0

    for entry in entries:
        ioc = {
            "source":           "AbuseIPDB",
            "indicator":        entry.get("ipAddress"),
            "type":             "IPv4",
            "risk_score":       min(int(entry.get("abuseConfidenceScore", 0)), 100),
            "country":          entry.get("countryCode"),
            "total_reports":    entry.get("totalReports"),
            "last_reported_at": entry.get("lastReportedAt"),
            "status":           "active",
        }
        exists = ioc_data_collection.find_one({
            "source":    "AbuseIPDB",
            "indicator": ioc["indicator"],
        })
        if not exists:
            ioc_data_collection.insert_one(ioc)
            inserted += 1
            print(f"  [+] {ioc['indicator']:18s}  score={ioc['risk_score']}")

    print(f"[AbuseIPDB] Done – {inserted} new IPs inserted.\n")
    return inserted


if __name__ == "__main__":
    ingest()
