import subprocess
import sys
import os
from datetime import datetime

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.mongo_handler import collection

print("[*] Starting Firewall Enforcer...")

blocked_ips = set()

try:
    threats = collection.find()

    for threat in threats:
        ip = threat.get("indicator")

        # Skip if no IP or already blocked
        if not ip or ip in blocked_ips:
            continue

        blocked_ips.add(ip)

        command = f"iptables -A INPUT -s {ip} -j DROP"
        subprocess.run(command, shell=True)

        print(f"[+] Blocked IP: {ip}")

        # ✅ Logging
        with open("blocked_ips.log", "a") as f:
            f.write(f"{datetime.now()} - Blocked: {ip}\n")

except Exception as e:
    print("Error:", e)

import json
from datetime import datetime

log = {
    "event": "IP_BLOCKED",
    "ip": ip,
    "risk_score": threat.get("risk_score", 0),
    "timestamp": datetime.now().isoformat()
}

with open("/home/sidharth/Banksec-TIP/firewall_events.json", "a") as f:
    f.write(json.dumps(log) + "\n")
