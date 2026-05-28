"""
main.py  –  BankSec-TIP ELK Stack & Visualization Branch
Aditya Tamakhuwala

Runs the full ELK pipeline:
  1. Sync MongoDB threats → Elasticsearch (direct index)
  2. Write firewall_events.json for Filebeat ingestion

Usage:
    python main.py
"""


def run():
    print("=" * 60)
    print("  BankSec-TIP  |  ELK Stack Visualization Pipeline")
    print("=" * 60)

    # 1. Direct MongoDB → Elasticsearch sync
    try:
        from elastic_sync import sync
        sync()
    except Exception as e:
        print(f"[!] Elasticsearch sync error: {e}")

    # 2. Write firewall_events.json (for Filebeat)
    try:
        from filebeat_logger import write_events
        write_events()
    except Exception as e:
        print(f"[!] Filebeat logger error: {e}")

    print("=" * 60)
    print("  ELK pipeline complete.")
    print("  Open Kibana at http://localhost:5601")
    print("=" * 60)


if __name__ == "__main__":
    run()
