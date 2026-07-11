
# Cisco Event-Driven Alerting Engine

An automated, event-driven network observability and alerting tool designed for Cisco IOS XE infrastructures. The application continuously monitors network interface states via the RESTCONF API (utilizing the `ietf-interfaces` YANG model) and dispatches immediate, secure SMTP email notifications upon detecting critical state changes.

Built with operational efficiency, modularity, and clean code practices suitable for enterprise network monitoring.

## Core Features

*   **Stateful Observability (Delta-Check):** Maintains a local in-memory cache of the infrastructure state. The engine performs edge-triggered delta analysis, triggering SMTP dispatch only upon critical state transitions (e.g., UP -> DOWN), eliminating alert fatigue.
*   **Target Node Reachability (Disaster Recovery):** Incorporates a state machine to track API target availability. In the event of a total node failure, the engine suppresses repetitive exceptions, logging the failure and subsequent recovery strictly once.
*   **Automated Log Rotation:** Implements a robust `TimedRotatingFileHandler`. Operational logs are autonomously archived at midnight with a strict 7-day retention policy.
*   **Modular Architecture:** Designed as a fully installable Python package with separated concerns (Monitoring, Alerting, CLI) and automated unit testing capabilities.
*   **12-Factor App Configuration:** Strict separation of sensitive credentials from source code via environment variable injection.

## Project Structure

```text
cisco-event-alerting-engine/
│
├── .venv/                  # Isolated Python Virtual Environment (Local only)
├── cisco_alerting/         # Core application package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface entry point
│   ├── monitor.py          # State machine and RESTCONF polling logic
│   └── notifier.py         # SMTP dispatch mechanisms
├── tests/                  # Unit testing directory
│   ├── __init__.py
│   └── test_monitor.py     # Component tests for the monitoring engine
├── pyproject.toml          # Package build and dependency configuration
├── .env                    # Production configuration containing credentials (Ignored by Git)
├── .env.example            # Template deployment file for configuration reference
├── .gitignore              # Version control exclusion rules
└── README.md               # Technical documentation
```

## Prerequisites

*   **Python:** Version 3.10 or higher.
*   **Target Node:** Cisco IOS XE instance with RESTCONF enabled on port 443.
*   **SMTP Gateway:** Dedicated service email account with App Passwords capability enabled.

## Configuration & Environment Setup

The application dynamically sources execution payloads from a secure environment file. Populate your local credentials by copying the provided infrastructure template:

```bash
cp .env.example .env
```

Ensure the generated `.env` file contains your target device and SMTP credentials:

```text
DEVICE_HOST=10.10.20.48
DEVICE_USER=developer
DEVICE_PASS=C1sco12345
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=projectalarmbot@gmail.com
EMAIL_PASS=yourclean16characterpassword
EMAIL_RECEIVER=target_operator@uczelnia.edu.pl
```

## Local Installation & Testing

Initialize and isolate your execution runtime space, then install the project as a local package:

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 2. Install testing frameworks and the package itself
pip install pytest
pip install -e .
```

Verify the structural integrity of the application by running the test suite:

```bash
pytest tests/ -v
```

## Execution

Thanks to the package configuration, you can launch the core automation observability loop using the newly registered system command:

```bash
cisco-monitor
```

## Verification & Audit Trails

Upon initial bootstrap, the engine takes a network infrastructure snapshot and stores it in the local runtime thread. Every operational event is recorded inside `network_monitor.log`.

To prevent unmanageable file growth, the engine enforces a daily cut-off at midnight. Archived logs receive a timestamped suffix (e.g., `network_monitor.log.2026-07-11`).

**Standard Audit Trail Example (Including Node Failure):**

```text
2026-07-11 22:00:00 [INFO] Starting network monitor on 10.10.20.48...
2026-07-11 22:00:02 [INFO] Started monitoring GigabitEthernet1 (Current: up)
2026-07-11 22:00:02 [INFO] Started monitoring Loopback10 (Current: up)
2026-07-11 22:05:30 [WARNING] State change on Loopback10: up -> down
2026-07-11 22:05:31 [INFO] Email alert sent to target_operator@uczelnia.edu.pl for Loopback10
2026-07-11 23:45:10 [ERROR] Cannot reach 10.10.20.48. Suppressing further errors until it's back.
2026-07-12 08:15:20 [INFO] Connection to 10.10.20.48 restored.
2026-07-12 08:30:05 [INFO] Script stopped by user.
```
