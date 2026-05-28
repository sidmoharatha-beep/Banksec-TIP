import re, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.mongo_handler import threats_collection

def extract_and_log():
    print("[IOC Extractor] Reading active threats from MongoDB...")
    count = threats_collection.count_documents({"status": "active"})
    print(f"[IOC Extractor] Found {count} active threats ready for enforcement.\n")
    return count

if __name__ == "__main__":
    extract_and_log()
