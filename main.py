"""
main.py  –  BankSec-TIP Firewall Policy Engine Branch
Sidharth Ranjan Moharatha

Runs:
  1. IOC Extractor  → writes firewall_events.json
  2. Firewall Enforcer  → applies iptables rules  (needs sudo)

Usage:
    sudo python main.py
"""
import os
import sys


def run():
    print("=" * 60)
    print("  BankSec-TIP  |  Firewall Policy Engine")
    print("=" * 60)

    # Step 1: Extract IOCs and write JSON logs
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                        "Firewall-PolicyEngine"))
        from Firewall_PolicyEngine.ioc_extractor import extract_and_log  # noqa
        extract_and_log()
    except Exception as e:
        print(f"[!] IOC Extractor error: {e}")

    # Step 2: Apply iptables rules
    try:
        from Firewall_PolicyEngine.firewall_enforcer import enforce  # noqa
        enforce()
    except Exception as e:
        print(f"[!] Firewall Enforcer error: {e}")

    print("=" * 60)
    print("  Firewall enforcement complete.")
    print("  Check blocked_ips.log and firewall_events.json")
    print("=" * 60)


if __name__ == "__main__":
    run()
