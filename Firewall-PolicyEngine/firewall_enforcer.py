import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
from datetime import datetime
from database.mongo_handler import collection

# Track already blocked IPs (prevents duplicate rules)
blocked_ips = set()

# Log file path
LOG_FILE = "logs/firewall.log"

def log_action(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def block_ip(ip):
    try:
        # Check if IP already blocked (basic check)
        if ip in blocked_ips:
            return

        # Apply firewall rule
        command = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(command, check=True)

        blocked_ips.add(ip)

        print(f"[+] Blocked IP: {ip}")
        log_action(f"Blocked IP: {ip}")

    except subprocess.CalledProcessError:
        print(f"[!] Failed to block IP: {ip}")
        log_action(f"ERROR blocking IP: {ip}")

def main():
    print("[*] Starting Firewall Enforcer...")

    try:
        # Fetch high-risk threats
        threats = collection.find({"risk_score": {"$gt": 80}})

        for threat in threats:
            ip = threat.get("indicator")

            if ip:
                block_ip(ip)

    except Exception as e:
        print(f"[!] Error: {e}")
        log_action(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()
