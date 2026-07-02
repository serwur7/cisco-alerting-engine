import os
import time
import logging
import smtplib
import requests
import urllib3
from email.mime.text import MIMEText
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler

# Load environment variables from .env file
load_dotenv()

# Disable SSL warnings for Cisco Sandbox (Lab environment)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= CONFIGURATION =================
HOST = os.getenv("DEVICE_HOST")
PORT = os.getenv("DEVICE_PORT", "443")
USER = os.getenv("DEVICE_USER")
PASS = os.getenv("DEVICE_PASS")
URL = f"https://{HOST}:{PORT}/restconf/data/ietf-interfaces:interfaces-state"
HEADERS = {"Accept": "application/yang-data+json"}

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# Enforce full control over the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define enterprise-grade logging format
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Brutally clear any hidden default handlers that might block the stream
if logger.hasHandlers():
    logger.handlers.clear()

# 1. Rotating File Handler: Executes a clean cut at midnight and archives (keeps 7 days)
file_handler = TimedRotatingFileHandler(
    filename="network_monitor.log",
    when="midnight",
    interval=1,
    backupCount=7,  # Adjust as needed - retention policy in days
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y-%m-%d" # Files will be saved as e.g., network_monitor.log.2026-07-02

# 2. Stream Handler: Live standard output for terminal viewing
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Attach handlers to the main alerting engine
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
class NetworkMonitor:
    def __init__(self):
        self.previous_state = {}

    def send_email_alert(self, interface_name, old_status, new_status):
        """Dispatches an immediate SMTP alert upon interface failure."""
        subject = f"[CRITICAL] Interface Failure: {interface_name} on {HOST}"
        body = f"Automated NetDevOps System detected an incident.\n\n" \
               f"Device: {HOST}\n" \
               f"Interface: {interface_name}\n" \
               f"State Change: {old_status.upper()} -> {new_status.upper()}\n\n" \
               f"Immediate engineering intervention required."
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
            logging.info(f"Alert dispatched: {interface_name} -> {EMAIL_RECEIVER}")
        except Exception as e:
            logging.error(f"SMTP Dispatch Error: {e}")

    def check_network(self):
        """Polls RESTCONF API and evaluates interface states."""
        try:
            response = requests.get(URL, auth=(USER, PASS), headers=HEADERS, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            interfaces = data.get("ietf-interfaces:interfaces-state", {}).get("interface", [])
            
            for iface in interfaces:
                name = iface.get("name")
                current_status = iface.get("oper-status", "unknown")
                
                # Register base state on first run
                if name not in self.previous_state:
                    self.previous_state[name] = current_status
                    logging.info(f"Initialized monitoring: {name} (Status: {current_status})")
                    continue
                
                # Evaluate state change
                old_status = self.previous_state[name]
                if current_status != old_status:
                    logging.warning(f"STATE CHANGE: {name} ({old_status} -> {current_status})")
                    
                    if current_status == "down":
                        self.send_email_alert(name, old_status, current_status)
                    
                    self.previous_state[name] = current_status
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"RESTCONF API Connection Error: {e}")

if __name__ == "__main__":
    # Validate environment payload
    if not all([HOST, USER, PASS, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        logging.error("Missing configuration in .env file. Please check .env.example.")
        exit(1)
        
    logging.info(f"Starting Event-Driven Alerting Engine on host {HOST}...")
    monitor = NetworkMonitor()
    
    try:
        while True:
            monitor.check_network()
            time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Monitoring system halted by operator.")
