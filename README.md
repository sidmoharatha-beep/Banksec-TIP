# BankSec-TIP — ELK Stack & Visualization Branch
**Assigned to: Aditya Tamakhuwala**
**Infotact Technical Internship Program | Finance & Banking Project**

---

## Overview

This branch implements **Week 2 & 4** of the Advanced Threat Intelligence Platform (TIP).
It takes the normalised threat data produced by the **osint-MongoDB branch** and makes it
visible through a full SIEM stack — Elasticsearch, Kibana, and Filebeat.

Every blocked IP from the **Firewall-PolicyEngine branch** is streamed into Elasticsearch
via Filebeat and visualised on a real-time Kibana dashboard.

---

## Pipeline Architecture

```
MongoDB (threats)
        ↓
elastic_sync.py ──────────────→ Elasticsearch (index: threat-intelligence)
        ↓
filebeat_logger.py ──→ firewall_events.json
                              ↓
                          Filebeat
                              ↓
                    Elasticsearch (index: firewall-events-*)
                              ↓
                      Kibana Dashboard
                      http://localhost:5601
```

---

## Project Structure

```
Banksec-TIP/
├── feeds/
│   ├── alienvault.py           # AlienVault OTX feed (shared)
│   ├── abuseipdb.py            # AbuseIPDB feed (shared)
│   ├── virustotal.py           # VirusTotal enrichment (shared)
│   ├── shodan_feed.py          # Shodan scanner (shared)
│   └── __init__.py
├── database/
│   ├── mongo_handler.py        # MongoDB connection (shared)
│   └── __init__.py
├── logs/
│   └── __init__.py
├── elastic_sync.py             # MongoDB threats → Elasticsearch
├── filebeat_logger.py          # Writes firewall_events.json for Filebeat
├── docker-compose.yml          # Elasticsearch + Kibana + Filebeat + MongoDB
├── filebeat.yml                # Filebeat configuration
├── main.py                     # Pipeline entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Prerequisites

- Kali Linux (or Ubuntu 22.04+)
- Python 3.10+
- Docker & Docker Compose
- **osint-MongoDB branch must have run first** (MongoDB must have threat data)

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

Verify Docker is working:
```bash
docker --version
docker-compose --version
```

### Step 3 — Install MongoDB (if not already installed)

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

```env
OTX_API_KEY=your_alienvault_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
VIRUSTOTAL_API_KEY=your_virustotal_key
SHODAN_API_KEY=your_shodan_key
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=threat_intelligence
ES_HOST=http://localhost:9200
```

> ⚠️ **Never commit the `.env` file.** It is already in `.gitignore`.

### Step 6 — Start the ELK Stack

```bash
docker-compose up -d
```

Wait 60 seconds for Elasticsearch to fully start, then verify:

```bash
curl http://localhost:9200
```

You should see a JSON response like:
```json
{
  "name" : "banksec_elasticsearch",
  "cluster_name" : "docker-cluster",
  "version" : { "number" : "8.13.0" },
  "tagline" : "You Know, for Search"
}
```

### Step 7 — Run the Pipeline

```bash
python3 main.py
```

### Step 8 — Open Kibana

```
http://localhost:5601
```

---

## Kibana Dashboard Setup

### Create Index Patterns

```
Stack Management → Index Management → Index Patterns → Create index pattern
```

Create two patterns:

| Index Pattern | Time Field |
|--------------|-----------|
| `threat-intelligence` | `synced_at` |
| `firewall-events-*` | `timestamp` |

### Build Dashboard Panels

```
Analytics → Dashboard → Create dashboard → Add panel
```

Recommended panels:

| Panel Type | Field | Title |
|-----------|-------|-------|
| Map | `country` | Attack Origins by Country |
| Bar chart | `indicator` | Top 10 Blocked IPs |
| Line chart | `timestamp` | Threat Volume Over Time |
| Data table | All fields | Latest Firewall Events |
| Metric | COUNT | Total IPs Blocked Today |
| Pie chart | `source` | Threats by OSINT Source |

---

## Verify Elasticsearch Data

```bash
# Check all indices
curl http://localhost:9200/_cat/indices?v

# Count threat-intelligence documents
curl http://localhost:9200/threat-intelligence/_count

# Count firewall events
curl http://localhost:9200/firewall-events-*/_count

# View a sample document
curl http://localhost:9200/threat-intelligence/_search?size=1&pretty
```

---

## Expected Output

```
============================================================
  BankSec-TIP  |  ELK Stack Visualization Pipeline
============================================================
[ES Sync] Starting MongoDB → Elasticsearch sync...
[ES] Index 'threat-intelligence' created.
[ES Sync] Indexed: 525  Errors: 0
[ES Sync] Done.

[Filebeat Logger] Writing events to firewall_events.json ...
[Filebeat Logger] Done – 531 events written.

============================================================
  ELK pipeline complete.
  Open Kibana at http://localhost:5601
============================================================
```

---

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| Elasticsearch | 9200 | Search and analytics engine |
| Kibana | 5601 | Visualization dashboard |
| Filebeat | — | Ships logs to Elasticsearch |
| MongoDB | 27017 | Threat data source |

### Useful Docker Commands

```bash
# Check all containers running
docker ps

# View Elasticsearch logs
docker logs banksec_elasticsearch

# View Kibana logs
docker logs banksec_kibana

# Stop all services
docker-compose down

# Restart all services
docker-compose restart
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `curl http://localhost:9200` times out | Wait 60s after `docker-compose up -d` and retry |
| `elasticsearch` module not found | `pip install elasticsearch==8.13.0` |
| Kibana shows "Kibana server is not ready" | Wait 2-3 minutes, Kibana waits for Elasticsearch |
| No data in Kibana | Check index pattern name matches exactly — `threat-intelligence` not `threat_intelligence` |
| Filebeat not shipping logs | Check `firewall_events.json` exists and has content: `wc -l firewall_events.json` |
| Docker permission denied | `sudo usermod -aG docker $USER` then `newgrp docker` |
| Port 9200 already in use | `sudo lsof -i :9200` to find and kill the process |

---

## Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Sync scripts and pipeline |
| Elasticsearch | 8.13.0 | Search and indexing engine |
| Kibana | 8.13.0 | SIEM visualization dashboard |
| Filebeat | 8.13.0 | Log shipper to Elasticsearch |
| MongoDB | 7.0 | Source of normalised threat data |
| Docker & Compose | Latest | Container orchestration |
| PyMongo | 4.17.0 | Python MongoDB driver |
| elasticsearch-py | 8.13.0 | Python Elasticsearch client |
| python-dotenv | 1.2.2 | Secure key management |
| Kali Linux | 2024+ | Security-focused OS |

---

## Git Commit Guidelines

```bash
# Feature
git commit -m "feat: add Kibana dashboard export as ndjson"

# Bug fix
git commit -m "fix: correct Elasticsearch index mapping for risk_score"

# Maintenance
git commit -m "chore: update docker-compose with healthcheck for elasticsearch"
```

> ⚠️ Direct commits to `main` are forbidden. Always work on `ELKStack-Visualization` branch.
> Evaluation requires commits spread across all 4 weeks.

---

## Next Steps (Weeks 5 & 6)

- MongoDB Change Stream for real-time sync (no batch polling)
- Kibana alerting rule — trigger when 5+ critical IPs indexed in 10 minutes
- Slack webhook notification for risk_score ≥ 95
- Export Kibana dashboard as `dashboard.ndjson` for reproducible setup

---

*Part of the Infotact Technical Internship Program — Finance & Banking Track*
*Bengaluru, Karnataka | 2026*
