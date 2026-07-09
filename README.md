# Cisco Event-Driven Alerting Engine

An automated, event-driven network observability and alerting tool designed for Cisco IOS XE infrastructures. The application continuously monitors network interface states via the RESTCONF API (utilizing the `ietf-interfaces` YANG model) and dispatches immediate, secure SMTP email notifications upon detecting critical state changes. 

Built with operational efficiency, zero-noise policies, and secure development practices required for Tier 0 production environments.

## Core Features

* **Stateful Observability (Delta-Check):** Maintains a local in-memory cache of the infrastructure state. The engine performs edge-triggered delta analysis, triggering SMTP dispatch *only* upon critical state transitions (e.g., `UP -> DOWN`), entirely eliminating alert fatigue.

* **Target Node Reachability (Disaster Recovery):** Incorporates an advanced state machine to track API target availability. In the event of a total node failure, the engine suppresses repetitive `Timeout/ConnectionError` exceptions, logging the catastrophic failure and subsequent recovery strictly once, guaranteeing Zero-Noise I/O even during complete infrastructure outages.

* **Zero-Noise I/O Policy:** Designed for maximum performance, the system writes to the disk exclusively when a state change is detected. Routine baseline checks bypass the disk layer, optimizing server I/O resources.

* **Automated Log Rotation:** Implements a robust `TimedRotatingFileHandler`. Operational logs are autonomously archived at midnight with a strict 7-day retention policy, ensuring the system footprint remains sustainable without manual intervention.

* **Model-Driven Programmability:** Utilizes structured programmatic RESTCONF API requests with JSON payloads over HTTPS, bypassing legacy, insecure SNMP polling or fragile CLI screen scraping.

* **12-Factor App Configuration:** Strict separation of sensitive credentials from source code via environment variable injection.

## Project Structure

```text
cisco-event-alerting-engine/
│
├── .venv/                  # Isolated Python Virtual Environment (Local only)
├── .env                    # Production configuration containing credentials (Ignored by Git)
├── .env.example            # Template deployment file for configuration reference
├── .gitignore              # Version control exclusion rules
├── requirements.txt        # Third-party Python dependencies
├── net_alerting_engine.py  # Core engine source code
└── README.md               # Technical documentation
```

## Prerequisites

* **Python:** Version 3.10 or higher.

* **Target Node:** Cisco IOS XE instance with RESTCONF enabled on port 443.

* **SMTP Gateway:** Dedicated service email account with App Passwords capability enabled (16-character string, no spaces).

## Configuration & Environment Setup

The application dynamically sources execution payloads from a secure environment file. Populate your local credentials by copying the provided infrastructure template:

```bash
cp .env.example .env
```

Ensure the generated `.env` file contains contiguous string values without raw formatting spaces:

```ini
DEVICE_HOST=10.10.20.48
DEVICE_USER=developer
DEVICE_PASS=C1sco12345

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=projectalarmbot@gmail.com
EMAIL_PASS=yourclean16characterpassword
EMAIL_RECEIVER=target_operator@uczelnia.edu.pl
```

## Local Installation

Initialize and isolate your execution runtime space:
```bash
python -m venv .venv
```

Activate the virtual container context:
* **Linux/macOS:** `source .venv/bin/activate`
* **Windows (PowerShell):** `.venv\Scripts\activate`

Execute dependency hydration via package manager:
```bash
pip install -r requirements.txt
```

## Execution

Launch the core automation observability loop inside your active environment:
```bash
python net_alerting_engine.py
```

## Verification & Audit Trails

Upon initial bootstrap, the engine takes a network infrastructure snapshot and stores it in the local runtime thread. Every operational event is transactionally recorded inside `network_monitor.log`.

To prevent unmanageable file growth, the engine enforces a daily cut-off at midnight. Archived logs receive a timestamped suffix:

```text
network_monitor.log
network_monitor.log.2026-07-01
network_monitor.log.2026-07-02
```

**Standard Audit Trail Example (Including Node Failure):**
```text
2026-07-02 22:00:00 [INFO] Starting Event-Driven Alerting Engine on host 10.10.20.48...
2026-07-02 22:00:02 [INFO] Initialized monitoring: GigabitEthernet1 (Status: up)
2026-07-02 22:00:02 [INFO] Initialized monitoring: Loopback10 (Status: up)
2026-07-02 22:05:30 [WARNING] STATE CHANGE: Loopback10 (up -> down)
2026-07-02 22:05:31 [INFO] Alert dispatched: Loopback10 -> target_operator@uczelnia.edu.pl
2026-07-02 23:45:10 [CRITICAL] Target Node 10.10.20.48 Unreachable. Suppressing further connection errors.
2026-07-03 08:15:20 [INFO] Target Node 10.10.20.48 Reconnected. Resuming monitoring.
```