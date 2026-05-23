## Banksec-TIP: Threat Intelligence & SIEM Pipeline

## Overview
Banksec-TIP is a cybersecurity project that builds a mini SIEM pipeline to detect, process, and visualize malicious indicators (IOCs) such as IP addresses.

The system integrates MongoDB, Python scripts, Filebeat, Elasticsearch, and Kibana to automate threat detection and monitoring.

## Architecture

MongoDB (IOC Feed)
↓
IOC Extractor (Python)
↓
Firewall Logging (JSON)
↓
Filebeat
↓
Elasticsearch
↓
Kibana Dashboard

## Tech Stack

- Python (IOC extraction, automation)
- MongoDB (IOC storage)
- Filebeat (log shipping)
- Elasticsearch (data storage & search)
- Kibana (visualization)
- Linux (Kali)

## Features

- Extracts malicious IPs from database
- Logs firewall events in real-time
- Ships logs to Elasticsearch via Filebeat
- Visualizes logs in Kibana
- End-to-end SIEM pipeline

## Project Structure

Banksec-TIP/
│
├── database/
│ └── mongo_handler.py
│
├── Firewall-PolicyEngine/
│ ├── ioc_extractor.py
│ └── firewall_enforcer.py
│
├── firewall_events.json
├── blocked_ips.log
└── README.md

## Setup Instructions

### 1. Clone Repo
```bash
git clone https://github.com/sidmoharatha-beep/Banksec-TIP.git
cd Banksec-TIP

### 2. Setup Virtual Environment

python3 -m venv venv
source venv/bin/activate
pip install pymongo

### 3. Start Elasticsearch & Kibana

sudo systemctl start elasticsearch
sudo systemctl start kibana

### 4. Run IOC Extractor

python ioc_extractor.py

### 5. View in Kibana

http://localhost:5601

## Sample Log

{
  "event": "IP_BLOCKED",
  "ip": "8.8.8.8",
  "risk_score": 90,
  "timestamp": "2026-05-23T04:45:01"
}

## Use Case

 Detect malicious IPs from OSINT feeds

 Automate firewall logging

 Monitor threats in real-time

 Demonstrate SIEM pipeline for academic/project use

## Contributors

 Adity Tamakhuwala

 Sidharth Ranjan Moharatha

 Chayan Soni


## Future Improvements

  Auto firewall blocking (iptables)

  Kibana dashboards & alerts

  Integration with live threat feeds

## Conclusion

This project demonstrates a working SIEM pipeline using open-source tools, 
providing hands-on experience in threat detection, log management, and security monitoring.
