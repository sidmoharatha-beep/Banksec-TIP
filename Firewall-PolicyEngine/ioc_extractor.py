"""
Firewall-PolicyEngine/ioc_extractor.py
Reads normalised threats from MongoDB and writes firewall_events.json.

Pipeline position:
  MongoDB (threats)  →  IOC Extractor  →  firewall_events.json
"""

import re
import os
import sys
import json
from datetime import datetime

# Fix import path so this works when run from the subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.mongo_handler import threats_collection

IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

# ── Output path: write to project root so Filebeat can pick it up ────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH     = os.path.join(PROJECT_ROOT, "firewall_events.json")


def extract_and_log() -> int:
    """Extract active threat IPs and write structured JSON logs."""
    print("[IOC Extractor] Starting extraction for firewall logging...")
    written = 0

    with open(LOG_PATH, "a") as f:
        for threat in threats_collection.find({"status": "active"}):
            ip = threat.get("indicator", "")
            if not ip or not IP_PATTERN.match(ip):
                continue

            event = {
                "event":      "IP_BLOCKED",
                "ip":         ip,
                "risk_score": threat.get("risk_score", 0),
                "source":     threat.get("source", ""),
                "country":    threat.get("country", ""),
                "timestamp":  datetime.utcnow().isoformat(),
            }
            f.write(json.dumps(event) + "\n")
            written += 1
            print(f"  [+] Logged: {ip}  score={event['risk_score']}")

    print(f"[IOC Extractor] Done – {written} events written to {LOG_PATH}\n")
    return written


if __name__ == "__main__":
    extract_and_log()
