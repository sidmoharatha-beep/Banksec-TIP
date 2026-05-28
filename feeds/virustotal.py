"""
feeds/virustotal.py
VirusTotal – query a list of IPs already in MongoDB for VT reputation.

API key location: .env  →  VIRUSTOTAL_API_KEY

Note: Free tier is limited to 4 requests/minute.
      This module enriches existing ioc_data records rather than bulk-fetching.
"""

import os
import time
import requests
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()

API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
if not API_KEY:
    raise EnvironmentError("[VirusTotal] VIRUSTOTAL_API_KEY not set in .env")

BASE_URL = "https://www.virustotal.com/api/v3"
HEADERS  = {"x-apikey": API_KEY}
RATE_DELAY = 15  # seconds between requests (free-tier: 4 req/min)


def query_ip(ip: str) -> dict:
    """Return VirusTotal analysis summary for a single IP."""
    url  = f"{BASE_URL}/ip_addresses/{ip}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 404:
        return {}
    resp.raise_for_status()
    attrs = resp.json().get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})
    return {
        "vt_malicious":  stats.get("malicious", 0),
        "vt_suspicious": stats.get("suspicious", 0),
        "vt_harmless":   stats.get("harmless", 0),
        "vt_reputation": attrs.get("reputation", 0),
        "vt_country":    attrs.get("country", ""),
    }


def enrich(limit: int = 20) -> int:
    """
    Enrich up to `limit` IPv4 records in ioc_data that lack VT data.
    """
    print(f"[VirusTotal] Starting enrichment (limit={limit})...")
    cursor  = ioc_data_collection.find(
        {"type": "IPv4", "vt_malicious": {"$exists": False}},
        limit=limit,
    )
    enriched = 0

    for doc in cursor:
        ip = doc.get("indicator")
        if not ip:
            continue
        print(f"  [~] Querying VT for {ip} ...")
        vt_data = query_ip(ip)
        if vt_data:
            ioc_data_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": vt_data},
            )
            enriched += 1
            print(f"      malicious={vt_data['vt_malicious']}  "
                  f"suspicious={vt_data['vt_suspicious']}")
        time.sleep(RATE_DELAY)

    print(f"[VirusTotal] Done – {enriched} records enriched.\n")
    return enriched


if __name__ == "__main__":
    enrich()
