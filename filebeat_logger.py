"""
filebeat_logger.py  –  Write firewall_events.json for Filebeat → Kibana
Aditya Tamakhuwala  |  ELK Stack Branch

Reads from MongoDB threats collection and writes JSON log lines to
firewall_events.json.  Filebeat then ships these to Elasticsearch.

Pipeline position:
  MongoDB (threats)  →  filebeat_logger.py  →  firewall_events.json
                      →  Filebeat  →  Elasticsearch  →  Kibana
"""

import os
import json
from datetime import datetime
from database.mongo_handler import threats_collection

# Write logs to the project root (Filebeat watches this path)
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "firewall_events.json")


def write_events() -> int:
    """Write one JSON log line per threat to firewall_events.json."""
    print(f"[Filebeat Logger] Writing events to {LOG_PATH} ...")
    written = 0

    with open(LOG_PATH, "a") as f:
        for threat in threats_collection.find({"status": "active"}):
            event = {
                "event":      "IP_BLOCKED",
                "ip":         threat.get("indicator", ""),
                "risk_score": threat.get("risk_score", 0),
                "source":     threat.get("source", ""),
                "country":    threat.get("country", ""),
                "timestamp":  datetime.utcnow().isoformat(),
            }
            f.write(json.dumps(event) + "\n")
            written += 1

    print(f"[Filebeat Logger] Done – {written} events written.\n")
    return written


if __name__ == "__main__":
    write_events()
