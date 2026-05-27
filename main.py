from feeds.shodan_feed import enrich_ip
from database.mongo_handler import threats

def enrich_existing_ips():

    indicators = threats.find({"type": "ip"})

    for doc in indicators:

        ip = doc.get("indicator")

        print(f"[+] Enriching {ip}")

        shodan_data = enrich_ip(ip)

        if shodan_data:

            threats.update_one(
                {"indicator": ip},
                {
                    "$set": {
                        "shodan": shodan_data
                    }
                }
            )

            print(f"[✓] Updated {ip}")

if __name__ == "__main__":
    enrich_existing_ips()
