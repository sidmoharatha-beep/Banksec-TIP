import re
from pymongo import MongoClient

print("[*] Starting IOC Extractor...")

client = MongoClient("mongodb://localhost:27017/")
db = client["threat_intelligence"]

source_collection = db["ioc_data"]
target_collection = db["threats"]

def extract_ips(text):
    return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)

existing_ips = set()
for doc in target_collection.find():
    if "indicator" in doc:
        existing_ips.add(doc["indicator"])

for doc in source_collection.find():
    text = str(doc)   # scan full document

    ips = extract_ips(text)

    for ip in ips:
        if ip in existing_ips:
            continue

        target_collection.insert_one({
            "indicator": ip,
            "risk_score": 90
        })

        existing_ips.add(ip)
        print(f"[+] Extracted IP: {ip}")

print("[✓] IOC Extraction Completed")
