import smtplib
import logging
from email.mime.text import MIMEText

class AlertNotifier:
    def __init__(self, smtp_server, smtp_port, sender, password, receiver, host):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender = sender
        self.password = password
        self.receiver = receiver
        self.host = host

    def send_email_alert(self, interface_name, old_status, new_status):
        """Dispatches an immediate SMTP alert upon interface failure."""
        subject = f"[CRITICAL] Interface Failure: {interface_name} on {self.host}"
        body = f"Automated NetDevOps System detected an incident.\n\n" \
               f"Device: {self.host}\n" \
               f"Interface: {interface_name}\n" \
               f"State Change: {old_status.upper()} -> {new_status.upper()}\n\n" \
               f"Immediate engineering intervention required."
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.receiver

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, [self.receiver], msg.as_string())
            logging.info(f"Alert dispatched: {interface_name} -> {self.receiver}")
        except Exception as e:
            logging.error(f"SMTP Dispatch Error: {e}")