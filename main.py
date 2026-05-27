from feeds.shodan_feed import enrich_ip
from database.mongo_handler import threats

def calculate_risk_score(shodan_data):

    risk_score = 50

    ports = shodan_data.get("ports", [])
    vulnerabilities = shodan_data.get("vulnerabilities", [])

    # Dangerous ports
    if 22 in ports:
        risk_score += 10

    if 3389 in ports:
        risk_score += 25

    if 445 in ports:
        risk_score += 30

    # Vulnerabilities
    if vulnerabilities:
        risk_score += 40

    return min(risk_score, 100)


def enrich_existing_ips():

    indicators = threats.find({"type": "ip"})

    for doc in indicators:

        ip = doc.get("indicator")

        print(f"[+] Enriching {ip}")

        shodan_data = enrich_ip(ip)

        if shodan_data:

            risk_score = calculate_risk_score(shodan_data)

            threats.update_one(
                {"indicator": ip},
                {
                    "$set": {
                        "shodan": shodan_data,
                        "risk_score": risk_score
                    }
                }
            )

            print(f"[✓] Updated {ip} | Risk Score: {risk_score}")

if __name__ == "__main__":
    enrich_existing_ips()
