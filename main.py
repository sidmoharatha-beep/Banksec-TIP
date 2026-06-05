"""
main.py  -  BankSec-TIP OSINT & MongoDB Branch
Chayan Soni

Runs the full OSINT ingestion pipeline:
  1. AlienVault OTX  — threat pulses
  2. AbuseIPDB       — high-confidence malicious IPs
  3. VirusTotal      — enrichment of existing IPs
  4. Shodan          — exposed service discovery
  5. IOC Extractor   — normalise raw data → threats collection
"""

import sys
from logs.logs import get_logger

logger = get_logger("main")


def run():
    logger.info("=" * 60)
    logger.info("  BankSec-TIP  |  OSINT Ingestion + IOC Extraction")
    logger.info("=" * 60)

    try:
        from feeds.alienvault import ingest as av_ingest
        av_ingest()
    except Exception as e:
        logger.error("AlienVault error: %s", e)

    try:
        from feeds.abuseipdb import ingest as ab_ingest
        ab_ingest()
    except Exception as e:
        logger.error("AbuseIPDB error: %s", e)

    try:
        from feeds.virustotal import enrich as vt_enrich
        vt_enrich(limit=10)
    except Exception as e:
        logger.error("VirusTotal error: %s", e)

    try:
        from feeds.shodan_feed import ingest as shodan_ingest
        shodan_ingest()
    except Exception as e:
        logger.error("Shodan error: %s", e)

    try:
        from ioc_extractor import extract_and_store
        extract_and_store()
    except Exception as e:
        logger.error("IOC Extractor error: %s", e)
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("  Pipeline complete. Threats stored in MongoDB.")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
