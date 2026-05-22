import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.mongo_handler import collection

print("[*] Starting IOC Extraction...")

try:
    threats = collection.find()

    for threat in threats:
        text = threat.get("name", "")

        # Extract IPs
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)

        for ip in ips:
            print("Found IP:", ip)

            collection.update_one(
                {"_id": threat["_id"]},
                {"$set": {"indicator": ip}}
            )

except Exception as e:
    print("Error:", e)
