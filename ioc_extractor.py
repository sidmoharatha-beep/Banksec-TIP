import re
import json
from datetime import datetime
from pymongo import MongoClient

# 🔹 CONNECT TO MONGODB
client = MongoClient("mongodb://localhost:27017/")
db = client["threat_intelligence"]              # change if needed
collection = db["threats"]                # change if needed

print("[*] Starting IOC Extractor...")

# 🔹 REGEX FOR IP EXTRACTION
ip_pattern = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"

found = False

for doc in collection.find():
    text = doc.get("text", "") or doc.get("message", "") or str(doc)

    print("Processing:", text)

    match = re.search(ip_pattern, text)

    if match:
        ip = match.group()
        print(f"[+] Extracted IP: {ip}")

        found = True

        # 🔹 LOG EVENT (FOR FILEBEAT → KIBANA)
        log_entry = {
            "event": "IP_BLOCKED",
            "ip": ip,
            "risk_score": 90,
            "timestamp": datetime.now().isoformat()
        }

        with open("/home/sidharth/Banksec-TIP/firewall_events.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    else:
        print("[-] No IP found in this document")

if not found:
    print("[!] No IOCs extracted")

print("[✓] IOC Extraction Completed")
