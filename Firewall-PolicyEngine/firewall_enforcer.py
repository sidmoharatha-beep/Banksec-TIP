"""
Firewall-PolicyEngine/firewall_enforcer.py
Dynamic Security Policy Enforcer  –  BankSec-TIP
Sidharth Ranjan Moharatha

Reads active threats from MongoDB, blocks them via iptables,
and logs each action to blocked_ips.log.

Pipeline position:
  MongoDB (threats)  →  Firewall Enforcer  →  iptables + blocked_ips.log

IMPORTANT: Must be run with sudo (iptables requires root).
"""

import subprocess
import sys
import os
import json
from datetime import datetime

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.mongo_handler import threats_collection

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_PATH     = os.path.join(PROJECT_ROOT, "blocked_ips.log")
EVENTS_PATH  = os.path.join(PROJECT_ROOT, "firewall_events.json")

print("[*] Starting Firewall Enforcer...")

blocked_ips = set()

# ── Collect already-blocked IPs from log (rollback-friendly) ─────────────────
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as lf:
        for line in lf:
            # Lines look like: "2026-05-23T10:00:00 - Blocked: 1.2.3.4"
            if " - Blocked: " in line:
                blocked_ips.add(line.strip().split(" - Blocked: ")[-1])


def block_ip(ip: str, risk_score: int) -> bool:
    """
    Add an iptables DROP rule for the given IP.
    Returns True if command succeeded.
    """
    # Guard: skip private/loopback ranges
    parts = list(map(int, ip.split(".")))
    if (parts[0] == 10
            or (parts[0] == 172 and 16 <= parts[1] <= 31)
            or (parts[0] == 192 and parts[1] == 168)
            or parts[0] == 127):
        print(f"  [skip] private IP: {ip}")
        return False

    cmd    = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [!] iptables error for {ip}: {result.stderr.strip()}")
        return False

    # ── Plain text log ────────────────────────────────────────────────────────
    with open(LOG_PATH, "a") as lf:
        lf.write(f"{datetime.utcnow().isoformat()} - Blocked: {ip}\n")

    # ── JSON log for Filebeat  ────────────────────────────────────────────────
    event = {
        "event":      "IP_BLOCKED",
        "ip":         ip,
        "risk_score": risk_score,
        "timestamp":  datetime.utcnow().isoformat(),
    }
    with open(EVENTS_PATH, "a") as ef:
        ef.write(json.dumps(event) + "\n")

    print(f"  [+] Blocked: {ip}  (risk={risk_score})")
    return True


def rollback_ip(ip: str) -> bool:
    """Remove an iptables DROP rule (false-positive recovery)."""
    cmd    = ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [~] Rolled back: {ip}")
        return True
    print(f"  [!] Rollback failed for {ip}: {result.stderr.strip()}")
    return False


def enforce():
    """Main loop – read DB and block all active high-risk IPs."""
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
        print(f"[!] Enforcer error: {exc}")
        sys.exit(1)

    print(f"\n[Firewall Enforcer] Done – {total} IPs blocked.\n")


if __name__ == "__main__":
    enforce()
