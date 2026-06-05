"""
Firewall-PolicyEngine/ioc_extractor.py
Reads MongoDB threats collection and reports active threat counts.

Pipeline position:
  MongoDB (threats)  →  ioc_extractor.py  →  firewall_enforcer.py
"""

import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.mongo_handler import threats_collection
from logs.logs import get_logger

logger = get_logger(__name__)


def extract_and_log() -> int:
    """Report count of active threats ready for enforcement."""
    logger.info("IOC Extractor: reading active threats from MongoDB...")
    count = threats_collection.count_documents({"status": "active"})
    fp_count = threats_collection.count_documents({"status": "false_positive"})
    blocked_count = threats_collection.count_documents({"status": "blocked"})
    logger.info(
        "IOC Extractor: active=%d  already_blocked=%d  false_positives=%d",
        count, blocked_count, fp_count
    )
    return count


if __name__ == "__main__":
    extract_and_log()
