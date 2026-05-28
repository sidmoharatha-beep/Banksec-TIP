"""
main.py  -  BankSec-TIP Firewall Policy Engine Branch
Sidharth Ranjan Moharatha
Usage: sudo venv/bin/python main.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "Firewall-PolicyEngine"))

def run():
    print("=" * 60)
    print("  BankSec-TIP  |  Firewall Policy Engine")
    print("=" * 60)

    try:
        from ioc_extractor import extract_and_log
        extract_and_log()
    except Exception as e:
        print(f"[!] IOC Extractor error: {e}")

    try:
        from firewall_enforcer import enforce
        enforce()
    except Exception as e:
        print(f"[!] Firewall Enforcer error: {e}")

    print("=" * 60)
    print("  Firewall enforcement complete.")
    print("  Check blocked_ips.log and firewall_events.json")
    print("=" * 60)

if __name__ == "__main__":
    run()
