"""
main.py  -  BankSec-TIP OSINT & MongoDB Branch
Chayan Soni
"""
import sys

def run():
    print("=" * 60)
    print("  BankSec-TIP  |  OSINT Ingestion + IOC Extraction")
    print("=" * 60)

    try:
        from feeds.alienvault import ingest as av_ingest
        av_ingest()
    except Exception as e:
        print(f"[!] AlienVault error: {e}")

    try:
        from feeds.abuseipdb import ingest as ab_ingest
        ab_ingest()
    except Exception as e:
        print(f"[!] AbuseIPDB error: {e}")

    try:
        from feeds.virustotal import enrich as vt_enrich
        vt_enrich(limit=10)
    except Exception as e:
        print(f"[!] VirusTotal error: {e}")

    try:
        from feeds.shodan_feed import ingest as shodan_ingest
        shodan_ingest()
    except Exception as e:
        print(f"[!] Shodan error: {e}")

    try:
        from ioc_extractor import extract_and_store
        extract_and_store()
    except Exception as e:
        print(f"[!] IOC Extractor error: {e}")
        sys.exit(1)

    print("=" * 60)
    print("  Pipeline complete. Threats stored in MongoDB.")
    print("=" * 60)

if __name__ == "__main__":
    run()
