"""
ioc_extractor.py
Reads raw IOC data from ioc_data_collection, extracts & normalises
IPv4 indicators, and writes unique entries to threats_collection.

Pipeline position:
  MongoDB (ioc_data)  →  IOC Extractor  →  MongoDB (threats)
"""

import re
from database.mongo_handler import ioc_data_collection, threats_collection

IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")


def is_private_ip(ip: str) -> bool:
    """Reject RFC-1918 and loopback addresses – these are never threats."""
    parts = list(map(int, ip.split(".")))
    return (
        parts[0] == 10
        or (parts[0] == 172 and 16 <= parts[1] <= 31)
        or (parts[0] == 192 and parts[1] == 168)
        or parts[0] == 127
    )


def extract_and_store() -> int:
    """Extract IPs from raw IOC records and insert into threats."""
    print("[IOC Extractor] Starting extraction...")

    # Build a set of already-known indicators to avoid duplicate-key errors
    existing = {
        doc["indicator"]
        for doc in threats_collection.find(
            {"indicator": {"$exists": True}},
            {"indicator": 1, "_id": 0},
        )
    }

    inserted = 0

    for doc in ioc_data_collection.find():
        # If the feed already stored a clean 'indicator' field, use it directly
        direct_ip = doc.get("indicator", "")
        if direct_ip and IP_PATTERN.match(direct_ip):
            candidate_ips = [direct_ip]
        else:
            # Fall back: scan the whole document text
            text = str(doc)
            candidate_ips = IP_PATTERN.findall(text)

        for ip in candidate_ips:
            if ip in existing:
                continue
            if is_private_ip(ip):
                print(f"  [skip] private IP: {ip}")
                continue

            threat = {
                "indicator":  ip,
                "type":       "IPv4",
                "source":     doc.get("source", "unknown"),
                "risk_score": doc.get("risk_score", 80),
                "country":    doc.get("country", ""),
                "status":     "active",
            }

            threats_collection.insert_one(threat)
            existing.add(ip)
            inserted += 1
            print(f"  [+] Extracted & stored: {ip}")

    print(f"[IOC Extractor] Done – {inserted} new threats stored.\n")
    return inserted


if __name__ == "__main__":
    extract_and_store()
