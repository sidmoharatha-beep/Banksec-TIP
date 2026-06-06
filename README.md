# BankSec-TIP — OSINT & MongoDB Branch
**Assigned to: Chayan Soni**
**Infotact Technical Internship Program | Finance & Banking Project**

---

## Overviews

This branch implements **OSINT & MongoDB** of the Advanced Threat Intelligence Platform (TIP).
It collects live threat intelligence from 4 OSINT sources, normalises and deduplicates
the data, and stores actionable IOCs (Indicators of Compromise) in MongoDB.

The output of this branch — the `threats` collection in MongoDB — feeds directly into:
- **Firewall-PolicyEngine branch** → dynamic iptables blocking
- **ELKStack-Visualization branch** → Kibana SIEM dashboards

---

## Pipeline Architecture

```
AlienVault OTX  ──┐
AbuseIPDB       ──┼──→  MongoDB: ioc_data (raw)
VirusTotal      ──┤          ↓
Shodan          ──┘    ioc_extractor.py
                             ↓
                     MongoDB: threats (normalised)
                             ↓
                  ┌──────────┴──────────┐
                  ↓                     ↓
        Firewall-PolicyEngine    ELKStack-Visualization
```
---

## Supported Threat Feeds

- AlienVault OTX
- AbuseIPDB
- VirusTotal
- Shodan

---

## Required Environment Variables

The following API keys are required for full OSINT feed integration:

- `SHODAN_API_KEY`
- `VIRUSTOTAL_API_KEY`
- `OTX_API_KEY`
- `ABUSEIPDB_API_KEY`

### Configuration

Create a `.env` file in the project root and add:

```env
SHODAN_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
OTX_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here
```

### Security Note

- Never commit the `.env` file to GitHub.
- Ensure `.env` is listed in `.gitignore`.
- Keep all API keys private.

---
## OSINT Sources

| # | Tool | What It Does | Risk Score |
|---|------|-------------|------------|
| 1 | **AlienVault OTX** | Pulls threat pulses — malicious IPs, domains, URLs | 80 |
| 2 | **AbuseIPDB** | Blacklist of reported malicious IPs (confidence ≥ 90%) | 90–100 |
| 3 | **VirusTotal** | Enriches IPs with multi-engine malware scan results | Dynamic |
| 4 | **Shodan** | Finds internet-exposed services (MongoDB, Elasticsearch, MySQL) | 70 |

---
## Current Feed Coverage

- AlienVault OTX: IOC ingestion
- AbuseIPDB: Malicious IP blacklist
- VirusTotal: Reputation enrichment
- Shodan: Internet-exposed asset discovery

---
## Project Structure

<<<<<<< Updated upstream
```
Banksec-TIP/
├── feeds/
│   ├── alienvault.py       # AlienVault OTX feed ingestion
│   ├── abuseipdb.py        # AbuseIPDB blacklist ingestion
│   ├── virustotal.py       # VirusTotal IP enrichment
│   ├── shodan_feed.py      # Shodan exposed-host scanner
│   └── __init__.py
├── database/
│   ├── mongo_handler.py    # MongoDB connection + collections
│   └── __init__.py
├── logs/
│   ├── logger.py           # Centralised logging config
│   └── __init__.py
├── ioc_extractor.py        # Normalises raw IOCs → threats collection
├── main.py                 # Pipeline entry point (run this)
├── requirements.txt
├── .env.example            # API key template
├── .gitignore
└── README.md
```
=======
Banksec-TIP/ ├── feeds/ │ ├── alienvault.p
y │ ├── abuseipdb.py │ ├── virustotal.py │ ├── shodan_feed.py │ └── init.py ├── database/ │ ├── mongo_handler.py │ └── init.py ├── logs/ │ └── init.py ├── screenshots/ │ ├── elasticsearch-running.png │ ├── kibana-home.png │ ├── kibana-discover.png │ ├── siem-dashboard.png │ └── docker-containers.png ├── elastic_sync.py ├── filebeat_logger.py ├── docker-compose.yml ├── filebeat.yml ├── main.py ├── requirements.txt ├── .env.example ├── .gitignore └── README.md


>>>>>>> Stashed changes
---
## MongoDB Collections

The platform stores threat intelligence data in the following collections:

- raw_iocs
- enriched_iocs
- threats

These collections support ingestion, enrichment, and IOC extraction workflows.

---
## Project Directory Structure

```text
Banksec-TIP/
│
├── database/
│   └── mongo_handler.py
│      Handles MongoDB connection and collection management.
│
├── feeds/
│   ├── alienvault_feed.py
│   ├── abuseipdb_feed.py
│   ├── virustotal_feed.py
│   └── shodan_feed.py
│      OSINT feed integrations and threat intelligence ingestion.
│
├── utils/
│   └── ioc_extractor.py
│      Extracts Indicators of Compromise (IOCs) from collected data.
│
├── main.py
│   Main pipeline entry point for OSINT ingestion and enrichment.
│
├── requirements.txt
│   Project dependencies.
│
├── .env
│   Stores API keys and environment variables (not committed to Git).
│
└── README.md
    Project documentation and setup instructions.
```
---
### Directory Overview

| Directory/File | Description |
|----------------|-------------|
| `database/` | MongoDB connection and database operations |
| `feeds/` | OSINT feed collectors and enrichment modules |
| `utils/` | IOC extraction and helper utilities |
| `main.py` | Executes the complete threat intelligence pipeline |
| `requirements.txt` | Python package dependencies |
| `.env` | API key configuration file |
| `README.md` | Project documentation |
---
## Setup & Installation

### Prerequisites
- Kali Linux (or Ubuntu 22.04+)
- Python 3.10+
- MongoDB
- API keys for all 4 OSINT tools (see below)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/sidmoharatha-beep/Banksec-TIP.git
cd Banksec-TIP
git checkout osint-MongoDB
```

### Step 2 — Install MongoDB

```bash
sudo apt update
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Verify MongoDB is running
sudo systemctl status mongodb
```

### Step 3 — Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure API Keys

```bash
cp .env.example .env
nano .env
```

Fill in your keys:

```env
OTX_API_KEY=your_alienvault_otx_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
VIRUSTOTAL_API_KEY=your_virustotal_key
SHODAN_API_KEY=your_shodan_key
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=threat_intelligence
```

> ⚠️ **Never commit the `.env` file.** It is already in `.gitignore`.

#### Where to Get API Keys

| Tool | URL |
|------|-----|
| AlienVault OTX | https://otx.alienvault.com/api |
| AbuseIPDB | https://www.abuseipdb.com/api |
| VirusTotal | https://www.virustotal.com/gui/my-apikey |
| Shodan | https://account.shodan.io/ |

### Step 6 — Run the Pipeline

```bash
python3 main.py
```

---

## Expected Output

```
============================================================
  BankSec-TIP  |  OSINT Ingestion + IOC Extraction
============================================================
[AlienVault] Starting ingestion...
  [+] IPv4        185.220.101.47
  [+] domain      malicious-domain.ru
  ...
[AlienVault] Done – 320 new IOCs inserted.

[AbuseIPDB] Starting ingestion...
  [+] 193.163.125.16    score=100
  [+] 202.145.0.18      score=100
  ...
[AbuseIPDB] Done – 500 new IPs inserted.

[VirusTotal] Starting enrichment (limit=10)...
  [~] Querying VT for 193.163.125.16 ...
      malicious=45  suspicious=3
[VirusTotal] Done – 10 records enriched.

[Shodan] Starting advanced OSINT scan...
  [~] Query: port:27017 MongoDB
      [+] 45.33.32.156:27017  (United States)
[Shodan] Done – 45 exposed hosts inserted.

[IOC Extractor] Starting extraction...
  [+] 185.220.101.47
  [+] 193.163.125.16
  ...
[IOC Extractor] Done – 525 threats stored.

============================================================
  Pipeline complete. Threats stored in MongoDB.
============================================================
```

---

## Verify Data in MongoDB

```bash
# Count total threats stored
mongo threat_intelligence --eval "db.threats.count()"

# View 5 sample threats
mongo threat_intelligence --eval "db.threats.find().limit(5).pretty()"

# Count by source
mongo threat_intelligence --eval "
db.ioc_data.aggregate([
  { \$group: { _id: '\$source', count: { \$sum: 1 } } }
]).forEach(printjson)"
```

---

## MongoDB Collections

| Collection | Contents |
|------------|----------|
| `ioc_data` | Raw data from all OSINT feeds |
| `threats` | Normalised, deduplicated IPv4 indicators ready for enforcement |

### Threat Document Schema

```json
{
  "indicator": "193.163.125.16",
  "type": "IPv4",
  "source": "AbuseIPDB",
  "risk_score": 100,
  "country": "RU",
  "status": "active"
}
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `mongod.service not found` | Use `sudo systemctl start mongodb` (not mongod) on Kali |
| `DuplicateKeyError on indicator_1` | Run: `mongo threat_intelligence --eval "db.threats.dropIndex('indicator_1')"` |
| `EnvironmentError: OTX_API_KEY not set` | Make sure `.env` file exists and has all keys filled in |
| `ModuleNotFoundError: feeds` | Run from project root: `cd ~/Banksec-TIP && python3 main.py` |

---

## Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Feed ingestion, IOC extraction |
| MongoDB | 7.0 | NoSQL storage for threat data |
| PyMongo | 4.17.0 | Python MongoDB driver |
| Requests | 2.34.2 | HTTP calls to OSINT APIs |
| Shodan SDK | 1.31.0 | Advanced OSINT scanning |
| python-dotenv | 1.2.2 | Secure API key management |
| BeautifulSoup4 | 4.14.3 | HTML parsing for feed scraping |
| Kali Linux | 2024+ | Security-focused OS |

---

## Git Commit Guidelines

```bash
# Feature
git commit -m "feat: add AbuseIPDB blacklist ingestion"

# Bug fix
git commit -m "fix: resolve duplicate IOC insertion in alienvault feed"

# Maintenance
git commit -m "chore: update requirements.txt with shodan dependency"
```

> ⚠️ Direct commits to `main` are forbidden. Always work on `osint-MongoDB` branch.
> Evaluation requires commits spread across all 4 weeks.

---

## Next Steps (Weeks 3 & 4)

- Dynamic risk scoring based on multi-source correlation
- Shodan cross-reference with AbuseIPDB for boosted confidence
- GeoIP enrichment (latitude/longitude for Kibana map)
- Weekly threat trend report generator

---

*Part of the Infotact Technical Internship Program — Finance & Banking Track*
*Bengaluru, Karnataka | 2026*
