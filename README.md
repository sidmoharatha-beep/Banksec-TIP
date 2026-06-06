# BankSec-TIP — Firewall Policy Engine Branch
**Assigned to: Sidharth Ranjan Moharatha**
**Infotact Technical Internship Program | Finance & Banking Project**

---

## Overview

This branch implements **Weeks 3 & 4** of the Advanced Threat Intelligence Platform (TIP).
It reads the normalised threat data produced by the **osint-MongoDB branch** from MongoDB
and dynamically enforces network-level firewall rulees using Linux iptables.

Every malicious IP with a risk score ≥ 70 is automatically blocked at the OS level,
with a complete audit trail written to structured JSON logs for the **ELKStack-Visualization
branch** to pick up via Filebeat.

**Week 4 additions:**
- `rollback.py` — SOC analyst false-positive recovery CLI tool
- Daemon mode — continuous polling via `--daemon` flag
- Centralised logging (`logs/logs.py`) replacing all `print()` calls
- MongoDB status tracking (`blocked`, `false_positive`) for Kibana visibility
- Timezone-aware timestamps (UTC ISO 8601)

---

## Pipeline Architecture

```
osint-MongoDB branch
        ↓
MongoDB: threats collection (active threats)
        ↓
Firewall-PolicyEngine/ioc_extractor.py
        ↓  (reports active threat count)
Firewall-PolicyEngine/firewall_enforcer.py
        ↓              ↓
  iptables DROP    firewall_events.json  →  Filebeat  →  Kibana
  blocked_ips.log  (audit trail)

SOC Analyst False Positive Flow:
  sudo python rollback.py <IP>
        ↓
  iptables -D (remove rule)  +  MongoDB status → "false_positive"
        ↓
  Kibana dashboard updated on next ELK sync
```

---

## Project Structure

```
Banksec-TIP/
├── Firewall-PolicyEngine/
│   ├── firewall_enforcer.py    # Applies iptables rules, rollback, daemon mode
│   └── ioc_extractor.py        # Reads MongoDB, reports threat counts
├── feeds/
│   ├── alienvault.py
│   ├── abuseipdb.py
│   ├── virustotal.py
│   └── __init__.py
├── database/
│   ├── mongo_handler.py        # MongoDB connection + indexes
│   └── __init__.py
├── logs/
│   ├── logs.py                 # Centralised logging config (Week 4)
│   ├── app.log                 # Runtime log (git-ignored)
│   └── __init__.py
├── main.py                     # Pipeline entry point (supports --daemon)
├── rollback.py                 # SOC analyst false-positive recovery tool (Week 4)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Prerequisites

- Kali Linux or Ubuntu 22.04+
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


### Step 2 — Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### Step 3 — Configure Environment Variables

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

### Step 4 — Run osint-MongoDB branch first

Make sure MongoDB has threat data:

```bash
git stash
git checkout osint-MongoDB
source venv/bin/activate
python3 main.py
git checkout Firewall-PolicyEngine
git stash pop
```

### Step 5a — Single Enforcement Pass

```bash
sudo venv/bin/python main.py
```

### Step 5b — Continuous Daemon Mode (Week 4)

```bash
# Poll MongoDB every 60 seconds (default)
sudo venv/bin/python main.py --daemon

# Poll every 2 minutes
sudo venv/bin/python main.py --daemon --interval 120
```

---

## Rollback — False Positive Recovery (Week 4)

If a legitimate IP was accidentally blocked, the SOC analyst uses `rollback.py`:

```bash
# Unblock a specific IP
sudo venv/bin/python rollback.py 185.220.101.47

# List all currently blocked IPs
sudo venv/bin/python rollback.py --list
```

**What rollback does:**
1. Removes the `iptables -D INPUT -s <IP> -j DROP` rule
2. Updates MongoDB `status` → `"false_positive"`, `blocked` → `False`
3. Writes an `IP_UNBLOCKED` event to `firewall_events.json` for Kibana

---

## Expected Output

```
============================================================
  BankSec-TIP  |  Firewall Policy Engine
============================================================
2026-06-05T10:00:00 [__main__] INFO: IOC Extractor: active=994  already_blocked=0  false_positives=0
2026-06-05T10:00:00 [firewall_enforcer] INFO: Enforcer: blocked 185.255.100.198 (risk=100)
2026-06-05T10:00:00 [firewall_enforcer] INFO: Enforcer: blocked 193.163.125.16 (risk=100)
...
2026-06-05T10:00:05 [firewall_enforcer] INFO: Enforcer: pass complete — 994 IPs blocked.
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

# Count firewall events
wc -l firewall_events.json

# View last 10 blocked IPs
tail -10 blocked_ips.log

# View last 5 JSON events
tail -5 firewall_events.json | python3 -m json.tool
```

---

## Log Files

| File | Contents | Committed to Git |
|------|----------|-----------------:|
| `blocked_ips.log` | Plain text audit trail — timestamp + IP per line | ❌ No |
| `firewall_events.json` | Structured JSON events for Filebeat/ELK | ❌ No |
| `logs/app.log` | Structured application log (all modules) | ❌ No |

All three are runtime files and are excluded by `.gitignore`.

---

## MongoDB Status Values

| `status` value | Meaning |
|---------------|---------|
| `"active"` | Threat ingested, not yet blocked |
| `"blocked"` | iptables DROP rule applied |
| `"false_positive"` | Rolled back by SOC analyst via `rollback.py` |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `mongod.service not found` | `sudo systemctl start mongodb` (Kali uses `mongodb`) |
| `No module named 'pymongo' with sudo` | Use `sudo venv/bin/python main.py` — never `sudo python` |
| `permission denied: blocked_ips.log` | `sudo chown $USER:$USER blocked_ips.log` |
| `0 IPs blocked` | MongoDB threats collection is empty — run osint-MongoDB branch first |
| `Rollback: IP not found in MongoDB` | IP was never ingested; check spelling |
| `iptables: No chain/target/match by that name` | Rule may not exist; verify with `sudo iptables -L INPUT -n` |

---

## Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Enforcement logic, rollback, daemon |
| PyMongo | 4.17.0 | MongoDB driver |
| Linux iptables | System | Network-level IP blocking |
| subprocess | Built-in | Execute iptables commands |
| python-dotenv | 1.2.2 | Secure environment variables |
| MongoDB | 7.0 | Source of normalised threat data |
| Kali Linux | 2024+ | Security OS |

---

## Git Commit Guidelines

```bash
git commit -m "feat: add rollback.py for SOC analyst false positive recovery"
git commit -m "feat: add daemon mode with --daemon and --interval flags"
git commit -m "feat: implement centralised logging in logs/logs.py"
git commit -m "fix: replace utcnow() with timezone-aware datetime.now(UTC)"
git commit -m "fix: update MongoDB status to blocked/false_positive on enforce/rollback"
git commit -m "docs: update README with Week 4 rollback and daemon usage"
```

> ⚠️ Direct commits to `main` are forbidden. Use the `Firewall-PolicyEngine` branch.
> All 4 weeks must have GitHub commits for evaluation.

---
## Future Enhancements

Planned improvements for the policy enforcement engine:

- Rule expiration and automatic cleanup
- Threat severity weighting
- Automated rollback suggestions
- Firewall rule analytics and reporting
*Part of the Infotact Technical Internship Program — Finance & Banking Track*
*Bengaluru, Karnataka | 2026*
