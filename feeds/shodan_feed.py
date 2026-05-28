import os
import time
import shodan
from dotenv import load_dotenv
from database.mongo_handler import ioc_data_collection

load_dotenv()
API_KEY = os.getenv("SHODAN_API_KEY")
api = shodan.Shodan(API_KEY)

QUERIES = [
    "port:27017 MongoDB",
    "port:9200 elasticsearch",
    "port:3306 country:IN",
]

def ingest(max_results=50):
    print("[Shodan] Starting scan...")
    inserted = 0
    for query in QUERIES:
        print(f"  [~] Query: {query}")
        try:
            results = api.search(query, limit=max_results)
            for match in results.get("matches", []):
                ip = match.get("ip_str")
                port = match.get("port")
                ioc = {
                    "source": "Shodan",
                    "indicator": ip,
                    "type": "IPv4",
                    "port": port,
                    "country": match.get("location", {}).get("country_name", ""),
                    "risk_score": 70,
                    "status": "exposed",
                }
                if not ioc_data_collection.find_one({"source": "Shodan", "indicator": ip, "port": port}):
                    ioc_data_collection.insert_one(ioc)
                    inserted += 1
                    print(f"      [+] {ip}:{port}")
            time.sleep(1)
        except shodan.APIError as e:
            print(f"  [!] Shodan error: {e}")
    print(f"[Shodan] Done – {inserted} hosts inserted.\n")
    return inserted
