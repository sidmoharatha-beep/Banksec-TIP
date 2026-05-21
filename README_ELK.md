# ELK Stack Visualization Module

## Overview

This module focuses on integrating MongoDB-based threat intelligence data with Elasticsearch and visualizing it using Kibana dashboards.

The ELK stack enables real-time threat monitoring, IOC analysis, SIEM-style dashboards, and threat visualization for cybersecurity analytics.

---

# Project Architecture

Threat Feeds → MongoDB → Elasticsearch → Kibana

---

# Technologies Used

- Elasticsearch
- Kibana
- MongoDB
- Docker
- Python
- PyMongo
- Elasticsearch Python Client

---

# Features

- MongoDB to Elasticsearch synchronization
- IOC (Indicators of Compromise) indexing
- Threat intelligence visualization
- Dockerized ELK stack setup
- Kibana SIEM dashboards
- Threat analytics and monitoring
- Local ELK deployment environment

---

# My Contribution

This branch focuses on the ELK Stack integration and SIEM visualization pipeline.

### Responsibilities

- ELK Stack setup using Docker
- Elasticsearch configuration
- Kibana integration
- MongoDB to Elasticsearch synchronization
- IOC data indexing
- SIEM visualization pipeline
- Dashboard setup and analytics

---

# Project Structure

```text
Banksec-TIP/
│
├── feeds/
├── database/
├── logs/
│
├── elastic_sync.py
├── elastic_to_mongo.py
├── docker-compose.yml
├── README_ELK.md
├── .gitignore
│
├── screenshots/
│   ├── elasticsearch-running.png
│   ├── kibana-home.png
│   ├── kibana-discover.png
│   ├── siem-dashboard.png
│   └── docker-containers.png




