import re
from database.mongo_handler import ioc_data_collection, threats_collection

IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

def is_private(ip):
    p = list(map(int, ip.split(".")))
    return (p[0]==10 or (p[0]==172 and 16<=p[1]<=31)
            or (p[0]==192 and p[1]==168) or p[0]==127)

def extract_and_store():
    print("[IOC Extractor] Starting extraction...")
    existing = {d["indicator"] for d in threats_collection.find(
        {"indicator": {"$exists": True}}, {"indicator": 1, "_id": 0})}
    inserted = 0
    for doc in ioc_data_collection.find():
        ip = doc.get("indicator", "")
        candidates = [ip] if IP_PATTERN.match(ip) else IP_PATTERN.findall(str(doc))
        for ip in candidates:
            if ip in existing or is_private(ip):
                continue
            threats_collection.insert_one({
                "indicator": ip,
                "type": "IPv4",
                "source": doc.get("source", "unknown"),
                "risk_score": doc.get("risk_score", 80),
                "country": doc.get("country", ""),
                "status": "active",
            })
            existing.add(ip)
            inserted += 1
            print(f"  [+] {ip}")
    print(f"[IOC Extractor] Done – {inserted} threats stored.\n")
    return inserted
