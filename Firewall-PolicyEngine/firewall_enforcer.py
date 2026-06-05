"""
Firewall-PolicyEngine/firewall_enforcer.py
Dynamic Security Policy Enforcer  –  BankSec-TIP
Sidharth Ranjan Moharatha

Reads active threats from MongoDB, blocks them via iptables,
and logs each action to blocked_ips.log and firewall_events.json.

Pipeline position:
  MongoDB (threats)  →  Firewall Enforcer  →  iptables + logs

IMPORTANT: Must be run with sudo (iptables requires root).

Week 4 additions:
  - rollback_ip() now updates MongoDB status to "false_positive"
  - Uses centralised logger instead of print()
  - datetime.utcnow() replaced with timezone-aware datetime.now(UTC)
  - Daemon mode added via run_daemon()
"""

import subprocess
import sys
import os
import json
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.mongo_handler import threats_collection
from logs.logs import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH     = os.path.join(PROJECT_ROOT, "blocked_ips.log")
EVENTS_PATH  = os.path.join(PROJECT_ROOT, "firewall_events.json")

# ── Load already-blocked IPs from previous run (rollback-friendly) ───────────
blocked_ips: set = set()

if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as lf:
        for line in lf:
            if " - Blocked: " in line:
                blocked_ips.add(line.strip().split(" - Blocked: ")[-1])

logger.info("Firewall Enforcer: loaded %d previously blocked IPs.", len(blocked_ips))


def _is_private(ip: str) -> bool:
    """Guard: skip RFC-1918 and loopback addresses."""
    try:
        parts = list(map(int, ip.split(".")))
    except ValueError:
        return True
    return (
        parts[0] == 10
        or (parts[0] == 172 and 16 <= parts[1] <= 31)
        or (parts[0] == 192 and parts[1] == 168)
        or parts[0] == 127
    )


def block_ip(ip: str, risk_score: int) -> bool:
    """
    Add an iptables DROP rule for the given IP.
    Writes to both plain-text log and JSON events file.
    Returns True if the rule was applied successfully.
    """
    if _is_private(ip):
        logger.debug("Enforcer: skipping private IP %s", ip)
        return False

    cmd    = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error("Enforcer: iptables error for %s: %s", ip, result.stderr.strip())
        return False

    now = datetime.now(timezone.utc).isoformat()

    # Plain text audit log
    with open(LOG_PATH, "a") as lf:
        lf.write(f"{now} - Blocked: {ip}\n")

    # JSON event for Filebeat → ELK pipeline
    event = {
        "event":      "IP_BLOCKED",
        "ip":         ip,
        "risk_score": risk_score,
        "timestamp":  now,
    }
    with open(EVENTS_PATH, "a") as ef:
        ef.write(json.dumps(event) + "\n")

    # Update MongoDB so ELK and rollback.py see the correct status
    threats_collection.update_one(
        {"indicator": ip},
        {"$set": {"status": "blocked", "blocked": True}}
    )

    logger.info("Enforcer: blocked %s (risk=%d)", ip, risk_score)
    return True


def rollback_ip(ip: str) -> bool:
    """
    Remove an iptables DROP rule (false-positive recovery).
    Updates MongoDB status to 'false_positive' so Kibana reflects it.
    Returns True if the rule was removed successfully.
    """
    cmd    = ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error("Rollback: iptables removal failed for %s: %s", ip, result.stderr.strip())
        return False

    # Mark as false positive in MongoDB
    threats_collection.update_one(
        {"indicator": ip},
        {"$set": {
            "status":        "false_positive",
            "blocked":       False,
            "false_positive": True,
        }}
    )

    # Remove from in-memory set so it won't be re-blocked this session
    blocked_ips.discard(ip)

    now = datetime.now(timezone.utc).isoformat()

    # Log the rollback event to firewall_events.json
    event = {
        "event":     "IP_UNBLOCKED",
        "ip":        ip,
        "reason":    "false_positive",
        "timestamp": now,
    }
    with open(EVENTS_PATH, "a") as ef:
        ef.write(json.dumps(event) + "\n")

    logger.warning("Rollback: unblocked %s — marked as false_positive in MongoDB.", ip)
    return True


def enforce() -> int:
    """
    Main enforcement pass — read DB and block all active high-risk IPs.
    Returns count of IPs blocked in this pass.
    """
    total = 0
    try:
        for threat in threats_collection.find(
            {"status": "active", "risk_score": {"$gte": 70}}
        ):
            ip         = threat.get("indicator")
            risk_score = threat.get("risk_score", 70)

            if not ip or ip in blocked_ips:
                continue

            if block_ip(ip, risk_score):
                blocked_ips.add(ip)
                total += 1

    except Exception as exc:
        logger.error("Enforcer: unexpected error: %s", exc)
        sys.exit(1)

    logger.info("Enforcer: pass complete — %d IPs blocked.", total)
    return total


def run_daemon(interval: int = 60) -> None:
    """
    Continuous daemon mode — runs enforce() every `interval` seconds.
    New threats added to MongoDB between passes are picked up automatically.

    Usage:
        sudo venv/bin/python main.py --daemon
        sudo venv/bin/python main.py --daemon --interval 120
    """
    import time
    logger.info("Daemon: starting — polling every %ds. Press Ctrl+C to stop.", interval)
    try:
        while True:
            logger.info("Daemon: running enforcement pass...")
            enforce()
            logger.info("Daemon: sleeping %ds...", interval)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Daemon: stopped by user.")


if __name__ == "__main__":
    enforce()
