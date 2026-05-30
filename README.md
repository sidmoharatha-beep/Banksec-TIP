# BankSec-TIP — ELK Stack & Visualization Branch
**Assigned to: Aditya Tamakhuwala**
**Infotact Technical Internship Program | Finance & Banking Project**

---

## Overview

This branch implements "ELK Stack & Visualization" of the Advanced Threat Intelligence Platform (TIP).
It takes the normalised threat data produced by the osint-MongoDB branch and makes it
visible through a full SIEM stack — Elasticsearch, Kibana, and Filebeat.

Every blocked IP from the Firewall-PolicyEngine branch is streamed into Elasticsearch
via Filebeat and visualised on a real-time Kibana dashboard for SOC analysts.

---
## ELK Data Flow Architecture

The ELK visualization layer provides centralized visibility into collected threat intelligence.

```text
OSINT Feeds
     │
     ▼
 MongoDB
     │
     ▼
Elasticsearch
     │
     ▼
  Kibana
```

### Data Flow

1. OSINT feeds (AlienVault OTX, AbuseIPDB, VirusTotal, Shodan) collect threat indicators.
2. Threat indicators are normalized and stored in MongoDB.
3. Elasticsearch indexes threat data for efficient searching and aggregation.
4. Kibana visualizes threat intelligence through dashboards and charts.

### Dashboard Objectives

* Threat source distribution
* Malicious IP tracking
* IOC trend analysis
* Risk score visualization
* Security event monitoring

## Pipeline Architecture

MongoDB (threats) | elastic_sync.py ──────────────────> Elasticsearch (index: threat-intelligence) | filebeat_logger.py ──> firewall_events.json | Filebeat | Elasticsearch (index: firewall-events-*) | Kibana Dashboard http://localhost:5601


Note: elastic_to_mongo.py has been removed. Data flows MongoDB -> Elasticsearch only.

---

## Project Structure

Banksec-TIP/ ├── feeds/ │ ├── alienvault.py │ ├── abuseipdb.py │ ├── virustotal.py │ ├── shodan_feed.py │ └── init.py ├── database/ │ ├── mongo_handler.py │ └── init.py ├── logs/ │ └── init.py ├── screenshots/ │ ├── elasticsearch-running.png │ ├── kibana-home.png │ ├── kibana-discover.png │ ├── siem-dashboard.png │ └── docker-containers.png ├── elastic_sync.py ├── filebeat_logger.py ├── docker-compose.yml ├── filebeat.yml ├── main.py ├── requirements.txt ├── .env.example ├── .gitignore └── README.md


---

## Prerequisites

- Kali Linux or Ubuntu 22.04+
- Python 3.10+
- Docker and Docker Compose
- osint-MongoDB branch must have run first — MongoDB must have threat data

---

## Setup & Installation

### Step 1 — Clone and Switch Branch

```bash
git clone https://github.com/sidmoharatha-beep/Banksec-TIP.git
cd Banksec-TIP
git checkout ELKStack-Visualization
```

If already cloned:
```bash
cd ~/Banksec-TIP
git checkout ELKStack-Visualization
git pull origin ELKStack-Visualization
```

### Step 2 — Install Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

Verify:
```bash
docker --version
docker-compose --version
```

### Step 3 — Install MongoDB

```bash
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Step 4 — Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Fill in your values:

OTX_API_KEY=your_alienvault_key ABUSEIPDB_API_KEY=your_abuseipdb_key VIRUSTOTAL_API_KEY=your_virustotal_key SHODAN_API_KEY=your_shodan_key MONGO_URI=mongodb://localhost:27017/ MONGO_DB=threat_intelligence ES_HOST=http://localhost:9200


Never commit the .env file. It is already in .gitignore.

### Step 6 — Start the ELK Stack

```bash
docker-compose up -d
```

Wait 60 seconds then verify:

```bash
curl http://localhost:9200
```

### Step 7 — Run the Pipeline

```bash
python3 main.py
```

### Step 8 — Open Kibana

http://localhost:5601

---

## Kibana SIEM Dashboard Setup

### Create Index Patterns

Stack Management -> Index Patterns -> Create index pattern

| Index Pattern       | Time Field  |
|---------------------|-------------|
| threat-intelligence | synced_at   |
| firewall-events-*   | timestamp   |

### Dashboard Panels

Analytics -> Dashboard -> Create dashboard -> Add panel

| Panel Type | Field     | Title                          |
|-----------|-----------|-------------------------------|
| Map        | country   | Attack Origins by Country      |
| Bar chart  | indicator | Top 10 Blocked IPs             |
| Line chart | timestamp | Threat Volume Over Time        |
| Data table | All       | Latest Firewall Events         |
| Metric     | COUNT     | Total IPs Blocked Today        |
| Pie chart  | source    | Threats by OSINT Source        |

---

## Kibana Dashboard Features

- Real-time event monitoring — live stream of blocked IPs
- Blocked IP visualization — geographic map of attack origins
- Threat timeline analysis — hourly/daily trend of threats
- Risk score analytics — distribution of low/medium/high risk indicators
- Top risky IP tracking — ranked list of highest-confidence threats
- Live security event monitoring — SIEM-style event feed from Filebeat

---

## Filebeat Integration

Filebeat ships firewall_events.json into Elasticsearch in real time.

Advantages:
- Realistic enterprise SIEM pipeline
- Centralised log ingestion
- Better scalability than direct API writes
- Real-time event streaming with minimal latency
- Decouples log generation from log storage

Filebeat watches: firewall_events.json
Ships to: Elasticsearch index firewall-events-YYYY.MM.DD

---

## Verify Elasticsearch Data

```bash
curl http://localhost:9200/_cat/indices?v
curl http://localhost:9200/threat-intelligence/_count
curl http://localhost:9200/firewall-events-*/_count
curl http://localhost:9200/threat-intelligence/_search?size=1&pretty
```

---

## Expected Output

============================================================ BankSec-TIP | ELK Stack Visualization Pipeline

[ES Sync] Starting MongoDB -> Elasticsearch sync...
[ES] Index 'threat-intelligence' created.
[ES Sync] Indexed: 525  Errors: 0
[ES Sync] Done.

[Filebeat Logger] Writing events to firewall_events.json ...
[Filebeat Logger] Done - 531 events written.
============================================================ ELK pipeline complete. Open Kibana at http://localhost:5601


---

## Docker Services

| Service       | Container Name        | Port | Purpose                    |
|--------------|-----------------------|------|---------------------------|
| Elasticsearch | banksec_elasticsearch | 9200 | Search and analytics       |
| Kibana        | banksec_kibana        | 5601 | SIEM visualization         |
| Filebeat      | banksec_filebeat      | —    | Ships logs to Elasticsearch|
| MongoDB       | banksec_mongo         | 27017| Threat data source         |

### Useful Docker Commands

```bash
docker ps
docker logs banksec_elasticsearch
docker logs banksec_kibana
docker logs banksec_filebeat
docker-compose down
docker-compose restart
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| curl localhost:9200 times out | Wait 60s after docker-compose up -d |
| elasticsearch module not found | pip install elasticsearch==8.13.0 |
| Kibana shows server not ready | Wait 2-3 min for Elasticsearch to be healthy |
| No data in Kibana | Index pattern must be exactly threat-intelligence |
| Filebeat not shipping | wc -l firewall_events.json must be > 0 |
| Docker permission denied | sudo usermod -aG docker $USER then newgrp docker |
| Port 9200 in use | sudo lsof -i :9200 to find and kill the process |
| elastic_to_mongo.py errors | File removed — use elastic_sync.py instead |

---

## My Contribution

- ELK Stack setup using Docker Compose
- Elasticsearch configuration and index mapping
- Kibana SIEM dashboard setup
- MongoDB to Elasticsearch synchronisation via elastic_sync.py
- IOC data indexing into Elasticsearch
- Filebeat integration for log shipping
- firewall_events.json generation via filebeat_logger.py
- Removed broken elastic_to_mongo.py (wrong data direction)

---

## Technologies Used

| Technology      | Version | Purpose                        |
|----------------|---------|-------------------------------|
| Python          | 3.10+   | Sync scripts and pipeline      |
| Elasticsearch   | 8.13.0  | Search and indexing engine     |
| Kibana          | 8.13.0  | SIEM visualization dashboard   |
| Filebeat        | 8.13.0  | Log shipper to Elasticsearch   |
| MongoDB         | 7.0     | Source of normalised threat data|
| Docker & Compose| Latest  | Container orchestration        |
| PyMongo         | 4.17.0  | Python MongoDB driver          |
| elasticsearch-py| 8.13.0  | Python Elasticsearch client    |
| python-dotenv   | 1.2.2   | Secure key management          |
| Kali Linux      | 2024+   | Security-focused OS            |

---

## Git Commit Guidelines

```bash
git commit -m "feat: add Kibana dashboard export as ndjson"
git commit -m "fix: correct Elasticsearch index mapping for risk_score"
git commit -m "chore: update docker-compose healthcheck for elasticsearch"
git commit -m "docs: update README with Filebeat integration steps"
```

Direct commits to main are forbidden. Always work on ELKStack-Visualization branch.
Evaluation requires commits spread across all 4 weeks.

---

## Next Steps (Weeks 5 & 6)

- MongoDB Change Stream for real-time sync
- Kibana alerting rule — trigger when 5+ critical IPs indexed in 10 minutes
- Slack webhook notification for risk_score >= 95
- Export Kibana dashboard as dashboard.ndjson

---

*Part of the Infotact Technical Internship Program — Finance & Banking Track*
*Bengaluru, Karnataka | 2026*
