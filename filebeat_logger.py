"""
filebeat_logger.py  –  BankSec-TIP ELK Stack & Visualization Branch
Aditya Tamakhuwala

Reads MongoDB threats collection and writes JSON log lines to
firewall_events.json.  Filebeat then ships these to Elasticsearch.

Pipeline position:
  MongoDB (threats)  →  filebeat_logger.py  →  firewall_events.json
                     →  Filebeat  →  Elasticsearch  →  Kibana

Fix applied:
  - Uses datetime.now(timezone.utc) instead of deprecated datetime.utcnow()
  - Skips threats already marked as false_positive
  - Uses structured logger instead of print()
"""

import os
import json
from datetime import datetime, timezone
from database.mongo_handler import threats_collection
from logs.logs import get_logger

logger = get_logger(__name__)

LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "firewall_events.json"
)


def write_events() -> int:
    """Write one JSON log line per active threat to firewall_events.json."""
    logger.info("Filebeat Logger: writing events to %s ...", LOG_PATH)
    written = 0

    with open(LOG_PATH, "a") as f:
        for threat in threats_collection.find({
            "status": "active",
            "false_positive": {"$ne": True},   # skip false positives
        }):
            event = {
                "event":         "IP_BLOCKED",
                "ip":            threat.get("indicator", ""),
                "risk_score":    threat.get("risk_score", 0),
                "source":        threat.get("source", ""),
                "country":       threat.get("country", ""),
                "false_positive": threat.get("false_positive", False),
                "timestamp":     datetime.now(timezone.utc).isoformat(),
            }
            f.write(json.dumps(event) + "\n")
            written += 1

    logger.info("Filebeat Logger: done — %d events written.", written)
    return written


if __name__ == "__main__":
    write_events()
