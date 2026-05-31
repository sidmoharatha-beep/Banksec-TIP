# BankSec-TIP — Firewall Policy Engine Branch
**Assigned to: Sidharth Ranjan Moharatha**
**Infotact Technical Internship Program | Finance & Banking Project**h

-----------

## Overview

This branch implements **Week 3 & 4** of the Advanced Threat Intelligence Platform (TIP).
It reads the normalised threat data produced by the **osint-MongoDB branch** from MongoDB
and dynamically enforces network-level firewall rules using Linux iptables.

Every malicious IP with a risk score ≥ 70 is automatically blocked at the OS level,
with a complete audit trail written to structured JSON logs for the **ELKStack-Visualization
branch** to pick up via Filebeat.

---

## Pipeline Architecture

```
osint-MongoDB branch
        ↓
MongoDB: threats collection (999 active threats)
        ↓
Firewall-PolicyEngine/ioc_extractor.py
        ↓  (reads active threat count)
Firewall-PolicyEngine/firewall_enforcer.py
        ↓              ↓
  iptables DROP    firewall_events.json  →  Filebeat  →  Kibana
  blocked_ips.log  (audit trail)
```

---

## Project Structure

```
Banksec-TIP/
├── Firewall-PolicyEngine/
│   ├── firewall_enforcer.py    # Applies iptables rules, writes logs
│   └── ioc_extractor.py        # Reads MongoDB, counts active threats
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
│   ├── logs.py                 # Centralised logging config
│   └── __init__.py
├── main.py                     # Pipeline entry point
├── requirements.txt
├── .env.example                # API key template
├── .gitignore
└── README.md
```

---

## Prerequisites

- Kali Linux (or Ubuntu 22.04+)
- Python 3.10+
- MongoDB running
- **osint-MongoDB branch must have run first** (MongoDB must have threat data)
- Root/sudo access (required for iptables)

---

## Setup & Installation

### Step 1 — Clone and Switch Branch

```bash
git clone https://github.com/sidmoharatha-beep/Banksec-TIP.git
cd Banksec-TIP
git checkout Firewall-PolicyEngine
```

If already cloned:
```bash
cd ~/Banksec-TIP
git checkout Firewall-PolicyEngine
git pull origin Firewall-PolicyEngine
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

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Fill in your values:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=threat_intelligence
```

> ⚠️ **Never commit the `.env` file.** It is already in `.gitignore`.

### Step 6 — Run osint-MongoDB branch first

Make sure MongoDB has threat data before running the enforcer:

```bash
git stash
git checkout osint-MongoDB
source venv/bin/activate
python3 main.py
git stash
git checkout Firewall-PolicyEngine
```

### Step 7 — Run the Firewall Enforcer

```bash
# IMPORTANT: Always use venv python with sudo — never plain sudo python
sudo venv/bin/python main.py
```

---

## Expected Output

```
============================================================
  BankSec-TIP  |  Firewall Policy Engine
============================================================
[IOC Extractor] Reading active threats from MongoDB...
[IOC Extractor] Found 999 active threats ready for enforcement.

[*] Starting Firewall Enforcer...
  [+] Blocked: 185.255.100.198  (risk=100)
  [+] Blocked: 193.163.125.16   (risk=100)
  [+] Blocked: 202.145.0.18     (risk=100)
  [+] Blocked: 45.142.193.12    (risk=100)
  ...
[Firewall Enforcer] Done – 994 IPs blocked.

============================================================
  Firewall enforcement complete.
  Check blocked_ips.log and firewall_events.json
============================================================
```

---

## Verify Everything is Working

```bash
# Count iptables DROP rules applied
sudo iptables -L INPUT -n | grep DROP | wc -l

# Count blocked IPs in log
wc -l blocked_ips.log

# Count firewall events (should match blocked_ips.log)
wc -l firewall_events.json

# View last 10 blocked IPs
tail -10 blocked_ips.log

# View last 5 JSON events
tail -5 firewall_events.json
```

All three counts should match. ✅

---

## Rollback a False Positive

If a legitimate IP was accidentally blocked:

```bash
# Method 1 — Python rollback function
python3 -c "
import sys
sys.path.insert(0, 'Firewall-PolicyEngine')
from firewall_enforcer import rollback_ip
rollback_ip('1.2.3.4')
"

# Method 2 — Direct iptables removal
sudo iptables -D INPUT -s 1.2.3.4 -j DROP
```

---

## Log Files

| File | Contents | Committed to Git |
|------|----------|-----------------|
| `blocked_ips.log` | Plain text audit trail — one IP per line with timestamp | ❌ No (runtime file) |
| `firewall_events.json` | Structured JSON events for Filebeat/ELK pipeline | ❌ No (runtime file) |

> Both files are in `.gitignore` by design. They are generated at runtime and
> picked up by the ELK branch via Filebeat.

---

## Clearing Logs (Fresh Run)

```bash
# Fix ownership if files were created by sudo
sudo chown $USER:$USER blocked_ips.log firewall_events.json

# Clear for a fresh run
echo -n "" > blocked_ips.log
echo -n "" > firewall_events.json

# Run again
sudo venv/bin/python main.py
```

---

## Verified Results

| Metric | Count |
|--------|-------|
| Active threats in MongoDB | 999 |
| IPs blocked via iptables | 994 |
| Lines in blocked_ips.log | 994 |
| Lines in firewall_events.json | 994 |
| Risk score 100 IPs | ~467 |
| Risk score 80 IPs | ~527 |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `mongod.service not found` | `sudo systemctl start mongodb` (Kali uses `mongodb` not `mongod`) |
| `No module named 'pymongo' with sudo` | Use `sudo venv/bin/python main.py` — never `sudo python` |
| `permission denied: blocked_ips.log` | `sudo chown $USER:$USER blocked_ips.log` |
| `0 IPs blocked` | MongoDB threats collection is empty — run osint-MongoDB branch first |
| `DuplicateKeyError on indicator_1` | `mongo threat_intelligence --eval "db.threats.dropIndex('indicator_1')"` |
| `firewall_events.json duplicates` | Clear file: `echo -n "" > firewall_events.json` then re-run |

---

## Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Firewall enforcement logic |
| PyMongo | 4.17.0 | MongoDB driver |
| Linux iptables | System | Network-level IP blocking |
| subprocess | Built-in | Execute system iptables commands |
| python-dotenv | 1.2.2 | Secure environment variable management |
| MongoDB | 7.0 | Source of normalised threat data |
| Kali Linux | 2024+ | Security-focused operating system |

---

## Git Commit Guidelines

```bash
# Feature
git commit -m "feat: add rate-limited daemon mode to firewall enforcer"

# Bug fix
git commit -m "fix: resolve permission denied on blocked_ips.log"

# Maintenance
git commit -m "chore: clear stale firewall_events from previous test run"

# Testing
git commit -m "test: verify 994 IPs blocked with matching log counts"
```

> ⚠️ Direct commits to `main` are forbidden. Always work on `Firewall-PolicyEngine` branch.
> Evaluation requires commits spread across all 4 weeks — commit every meaningful change.

---

## Next Steps (Weeks 5 & 6)

- Continuous daemon mode — poll MongoDB every 5 minutes for new threats
- `rollback.py` CLI tool — `python rollback.py --ip 1.2.3.4`
- PCI-DSS compliance report generator
- GitHub Actions lint workflow

---

*Part of the Infotact Technical Internship Program — Finance & Banking Track*
*Bengaluru, Karnataka | 2026*
