import os
import shodan
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMlBfpAHANbvcUGWqDSXnWOdKLN20Fme")

api = shodan.Shodan(API_KEY)


def enrich_ip(ip):
    try:
        host = api.host(ip)

        enriched_data = {
            "indicator": ip,
            "organization": host.get("org"),
            "os": host.get("os"),
            "ports": host.get("ports", []),
            "country": host.get("country_name"),
            "hostnames": host.get("hostnames", []),
            "vulnerabilities": list(host.get("vulns", {}).keys())
        }

        return enriched_data

    except Exception as e:
        print(f"[Shodan Error] {ip}: {e}")
        return None
