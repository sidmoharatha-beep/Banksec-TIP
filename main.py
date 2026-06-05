"""
main.py  -  BankSec-TIP Firewall Policy Engine Branch
Sidharth Ranjan Moharatha

Usage:
    # Single enforcement pass (default):
    sudo venv/bin/python main.py

    # Continuous daemon mode (polls every 60s):
    sudo venv/bin/python main.py --daemon

    # Daemon with custom interval (seconds):
    sudo venv/bin/python main.py --daemon --interval 120

    # Rollback a false-positive IP:
    sudo venv/bin/python rollback.py 1.2.3.4
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Firewall-PolicyEngine"))

from logs.logs import get_logger

logger = get_logger("main")


def run(daemon: bool = False, interval: int = 60):
    logger.info("=" * 60)
    logger.info("  BankSec-TIP  |  Firewall Policy Engine")
    logger.info("=" * 60)

    try:
        from ioc_extractor import extract_and_log
        extract_and_log()
    except Exception as e:
        logger.error("IOC Extractor error: %s", e)

    try:
        from firewall_enforcer import enforce, run_daemon
        if daemon:
            run_daemon(interval=interval)
        else:
            enforce()
    except Exception as e:
        logger.error("Firewall Enforcer error: %s", e)

    if not daemon:
        logger.info("=" * 60)
        logger.info("  Firewall enforcement complete.")
        logger.info("  Check blocked_ips.log and firewall_events.json")
        logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BankSec-TIP Firewall Policy Engine")
    parser.add_argument(
        "--daemon", action="store_true",
        help="Run in continuous daemon mode (polls MongoDB at set interval)"
    )
    parser.add_argument(
        "--interval", type=int, default=60,
        help="Polling interval in seconds for daemon mode (default: 60)"
    )
    args = parser.parse_args()
    run(daemon=args.daemon, interval=args.interval)
