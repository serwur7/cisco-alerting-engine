# cisco-event-alerting-engine

An automated, event-driven network observability and alerting tool designed for Cisco IOS XE infrastructures. The application continuously monitors network interface states via **RESTCONF API** (utilizing the `ietf-interfaces` YANG model) and dispatches immediate, secure **SMTP email notifications** upon detecting critical state changes (e.g., link failures, `up` to `down` transitions).

Built with operational efficiency and secure development practices in mind.

## Core Features

* **Stateful Monitoring:** Maintains a local in-memory cache of the infrastructure state to perform edge-triggered delta analysis, avoiding repetitive alert spam.
* **Modern Telemetry Interface:** Utilizes structured programmatic RESTCONF API requests over HTTPS instead of legacy, insecure SNMP polling or heavy CLI screen scraping.
* **Production-Grade Logging:** Dual-destination logging infrastructure that outputs directly to the system console and appends detailed audit trails into a persistent local log file.
* **Decoupled Configuration:** Strict separation of sensitive credentials from source code using environment variable injection.

## Project Structure

```text
cisco-alert-engine/
│
├── .venv/                  # Isolated Python Virtual Environment (Local only)
├── .env                    # Production configuration containing credentials (Ignored by Git)
├── .env.example            # Template deployment file for configuration reference
├── .gitignore              # Version control exclusion rules
├── requirements.txt        # Third-party Python dependencies
├── net_alerting_engine.py  # Core engine source code
└── README.md               # Technical documentation

Prerequisites
Python: Version 3.10 or higher.

Target Node: Cisco IOS XE instance with RESTCONF enabled (Fully tested against Cisco DevNet Sandbox Always-On IOS XE Node).

SMTP Gateway: Dedicated service email account with App Passwords capability enabled.

Configuration & Environment Setup
The application dynamically sources execution payloads from a secure environment file. Populate your local credentials by copying the provided infrastructure template:

cp .env.example .env
Ensure the generated .env file contains contiguous string values without raw formatting spaces:

Ini, TOML
DEVICE_HOST=sandbox-iosxe-recomm-1.cisco.com
DEVICE_USER=developer
DEVICE_PASS=C1sco12345
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=projectalarmbot@gmail.com
EMAIL_PASS=yourclean16characterpassword
EMAIL_RECEIVER=target_operator@uczelnia.edu.pl
Local Installation
Initialize and isolate your execution runtime space:

Bash
python -m venv .venv
Activate the virtual container context:

Windows (PowerShell/CMD): .venv\Scripts\activate

Linux/macOS: source .venv/bin/activate

Execute dependency hydration via package manager:

Bash
pip install -r requirements.txt
Execution
Launch the core automation observability loop inside your active environment:

Bash
python net_alerting_engine.py
Verification & Audit Trails
Upon initial bootstrap, the engine takes a network infrastructure snapshot and stores it in the local runtime thread. Every operational log statement is transactionally recorded inside network_monitor.log:

Plaintext
2026-07-01 22:00:00 [INFO] Starting Event-Driven Alerting Engine on host sandbox-iosxe-recomm-1.cisco.com...
2026-07-01 22:00:02 [INFO] Initialized monitoring: GigabitEthernet1 (Status: up)
2026-07-01 22:00:02 [INFO] Initialized monitoring: Loopback0 (Status: up)
2026-07-01 22:05:30 [WARNING] STATE CHANGE: GigabitEthernet1 (up -> down)
2026-07-01 22:05:31 [INFO] Alert dispatched: GigabitEthernet1 -> target_operator@wsei.edu.pl