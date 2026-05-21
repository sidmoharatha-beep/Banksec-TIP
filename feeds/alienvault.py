import os
import requests
from dotenv import load_dotenv
from database.mongo_handler import collection

load_dotenv()

API_KEY = os.getenv("OTX_API_KEY")

headers = {
    "X-OTX-API-KEY": API_KEY
}

url = "https://otx.alienvault.com/api/v1/pulses/subscribed"

response = requests.get(url, headers=headers)

data = response.json()

for pulse in data.get("results", []):

    ioc = {
        "source": "AlienVault",
        "name": pulse.get("name"),
        "risk_score": 80,
        "status": "active"
    }

    existing = collection.find_one({
        "name": ioc["name"]
    })

    if not existing:
        collection.insert_one(ioc)
        print(f"Inserted: {ioc['name']}")

print("Threat ingestion completed")
