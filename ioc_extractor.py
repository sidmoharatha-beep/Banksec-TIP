"""
ioc_extractor.py
Reads raw IOC data from ioc_data_collection, extracts & normalises
IPv4 indicators, and writes unique entries to threats_collection.

Pipeline position:
  MongoDB (ioc_data)  →  IOC Extractor  →  MongoDB (threats)

Fix applied:
  - Added 'false_positive' and 'blocked' fields to threat schema
    so the Firewall-PolicyEngine rollback.py can update status cleanly.
  - Replaced print() with structured logger calls.
"""

import re
from database.mongo_handler import ioc_data_collection, threats_collection
from logs.logs import get_logger

logger = get_logger(__name__)

IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")


def is_private_ip(ip: str) -> bool:
    """Reject RFC-1918 and loopback addresses — these are never threats."""
    try:
        parts = list(map(int, ip.split(".")))
    except ValueError:
        return True   # malformed — skip safely
    return (
        parts[0] == 10
        or (parts[0] == 172 and 16 <= parts[1] <= 31)
        or (parts[0] == 192 and parts[1] == 168)
        or parts[0] == 127
    )


def extract_and_store() -> int:
    """Extract IPs from raw IOC records and insert into threats."""
    logger.info("IOC Extractor: starting extraction...")

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
        direct_ip = doc.get("indicator", "")
        if direct_ip and IP_PATTERN.match(direct_ip):
            candidate_ips = [direct_ip]
        else:
            candidate_ips = IP_PATTERN.findall(str(doc))

        for ip in candidate_ips:
            if ip in existing:
                continue
            if is_private_ip(ip):
                logger.debug("IOC Extractor: skipping private IP %s", ip)
                continue

            threat = {
                "indicator":     ip,
                "type":          "IPv4",
                "source":        doc.get("source", "unknown"),
                "risk_score":    doc.get("risk_score", 80),
                "country":       doc.get("country", ""),
                # status field — enforcer sets to "blocked"; rollback sets to "false_positive"
                "status":        "active",
                "blocked":       False,
                "false_positive": False,
            }

            threats_collection.insert_one(threat)
            existing.add(ip)
            inserted += 1
            logger.info("IOC Extractor: stored %s (score=%s)", ip, threat["risk_score"])

    logger.info("IOC Extractor: done — %d new threats stored.", inserted)
    return inserted


if __name__ == "__main__":
    extract_and_store()
