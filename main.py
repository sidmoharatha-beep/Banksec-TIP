"""
main.py  –  BankSec-TIP ELK Stack & Visualization Branch
Aditya Tamakhuwala

Runs the full ELK pipeline:
  1. Sync MongoDB threats → Elasticsearch (direct index)
  2. Write firewall_events.json for Filebeat ingestion

Usage:
    python main.py
"""

from logs.logs import get_logger

logger = get_logger("main")


def run():
    logger.info("=" * 60)
    logger.info("  BankSec-TIP  |  ELK Stack Visualization Pipeline")
    logger.info("=" * 60)

    try:
        from elastic_sync import sync
        sync()
    except Exception as e:
        logger.error("Elasticsearch sync error: %s", e)

    try:
        from filebeat_logger import write_events
        write_events()
    except Exception as e:
        logger.error("Filebeat logger error: %s", e)

    logger.info("=" * 60)
    logger.info("  ELK pipeline complete.")
    logger.info("  Open Kibana at http://localhost:5601")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
