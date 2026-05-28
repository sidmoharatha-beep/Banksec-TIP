# BankSec-TIP — Firewall Policy Engine Branch
**Assigned to: Sidharth Ranjan Moharatha**

## Overview
This branch handles **Firewall Policy Engine** of the project:
- Extract active threat IPs from MongoDB
- Apply iptables DROP rules dynamically
- Log all blocked IPs to `blocked_ips.log` and `firewall_events.json`
- Rollback mechanism for false positives

## Pipeline
```
MongoDB (threats)
      ↓
Firewall-PolicyEngine/ioc_extractor.py  →  firewall_events.json
      ↓
Firewall-PolicyEngine/firewall_enforcer.py  →  iptables + blocked_ips.log
      ↓
[ELK branch picks up firewall_events.json via Filebeat]
```

## Setup

```bash
# 1. Clone and switch branch
git clone <repo-url>
cd Banksec-TIP
git checkout firewall-policyengine

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure keys
cp .env.example .env
# Edit .env

# 4. Start MongoDB
sudo systemctl start mongod

# 5. Run enforcer (requires sudo for iptables)
sudo python main.py

# To rollback a specific IP:
# python -c "from Firewall-PolicyEngine.firewall_enforcer import rollback_ip; rollback_ip('1.2.3.4')"
```

## API Key Locations
| Key | File | Variable Name |
|-----|------|---------------|
| MongoDB URI | `.env` | `MONGO_URI` |

## Technologies
- Python 3.10+, PyMongo, subprocess
- Linux iptables
- Kali Linux
