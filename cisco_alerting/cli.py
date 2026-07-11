import os
import time
import logging
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from cisco_alerting.notifier import AlertNotifier
from cisco_alerting.monitor import NetworkMonitor

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    if logger.hasHandlers():
        logger.handlers.clear()
        
    file_handler = TimedRotatingFileHandler("network_monitor.log", when="midnight", interval=1, backupCount=7, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def main():
    load_dotenv()
    setup_logger()

    HOST = os.getenv("DEVICE_HOST")
    PORT = os.getenv("DEVICE_PORT", "443")
    USER = os.getenv("DEVICE_USER")
    PASS = os.getenv("DEVICE_PASS")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

    if not all([HOST, USER, PASS, EMAIL_SENDER, EMAIL_PASS, EMAIL_RECEIVER]):
        logging.error("Missing configuration in .env file.")
        exit(1)

    notifier = AlertNotifier(SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASS, EMAIL_RECEIVER, HOST)
    monitor = NetworkMonitor(HOST, PORT, USER, PASS, notifier)

    logging.info(f"Starting Event-Driven Alerting Engine on host {HOST}...")
    try:
        while True:
            monitor.check_network()
            time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Monitoring system halted by operator.")

if __name__ == "__main__":
    main()