"""
rollback.py  –  BankSec-TIP Firewall Policy Engine
Sidharth Ranjan Moharatha

SOC Analyst false-positive recovery tool.

Removes a specific IP from iptables DROP rules and marks it as
'false_positive' in MongoDB so it won't be re-blocked and Kibana
dashboards correctly exclude it from threat counts.

Usage:
    sudo venv/bin/python rollback.py <IP_ADDRESS>

Examples:
    sudo venv/bin/python rollback.py 185.220.101.47
    sudo venv/bin/python rollback.py 203.0.113.5

Requirements:
    - Must be run with sudo (iptables requires root)
    - MongoDB must be running
    - IP must have been previously blocked by the enforcer
"""

import sys
import os
import argparse

# Ensure the Firewall-PolicyEngine subpackage is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Firewall-PolicyEngine"))

from firewall_enforcer import rollback_ip
from database.mongo_handler import threats_collection
from logs.logs import get_logger

logger = get_logger("rollback")


def rollback(ip: str) -> None:
    """Full rollback: remove iptables rule + update MongoDB."""

    # Validate that the IP exists in our threats collection
    threat = threats_collection.find_one({"indicator": ip})
    if not threat:
        logger.error(
            "Rollback: IP %s not found in MongoDB threats collection. "
            "It may have never been ingested or was already removed.", ip
        )
        sys.exit(1)

    current_status = threat.get("status", "unknown")
    if current_status == "false_positive":
        logger.warning(
            "Rollback: %s is already marked as false_positive in MongoDB. "
            "Attempting iptables removal anyway in case rule still exists...", ip
        )

    logger.info("Rollback: initiating rollback for %s (current status: %s)...", ip, current_status)

    success = rollback_ip(ip)

    if success:
        logger.info(
            "Rollback: SUCCESS — %s has been unblocked and marked false_positive in MongoDB.", ip
        )
        logger.info("Rollback: Kibana dashboard will reflect this on next sync.")
    else:
        logger.error(
            "Rollback: FAILED — iptables rule for %s could not be removed. "
            "Check if the rule exists: sudo iptables -L INPUT -n | grep %s", ip, ip
        )
        sys.exit(1)


def list_blocked() -> None:
    """Print all currently blocked IPs from MongoDB."""
    blocked = list(threats_collection.find(
        {"status": "blocked"},
        {"indicator": 1, "risk_score": 1, "source": 1, "_id": 0}
    ))
    if not blocked:
        logger.info("Rollback: no IPs currently marked as blocked in MongoDB.")
        return
    logger.info("Rollback: currently blocked IPs (%d total):", len(blocked))
    for entry in blocked:
        print(f"  {entry['indicator']:20s}  score={entry.get('risk_score','?'):>3}  source={entry.get('source','?')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BankSec-TIP — SOC Analyst False Positive Rollback Tool",
        epilog="Example: sudo venv/bin/python rollback.py 185.220.101.47"
    )
    parser.add_argument(
        "ip", nargs="?",
        help="IP address to unblock and mark as false positive"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all currently blocked IPs instead of rolling back"
    )
    args = parser.parse_args()

    if args.list:
        list_blocked()
    elif args.ip:
        rollback(args.ip)
    else:
        parser.print_help()
        sys.exit(1)
