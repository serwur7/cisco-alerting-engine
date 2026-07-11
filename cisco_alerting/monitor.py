import requests
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NetworkMonitor:
    def __init__(self, host, port, user, password, notifier):
        self.url = f"https://{host}:{port}/restconf/data/ietf-interfaces:interfaces-state"
        self.auth = (user, password)
        self.headers = {"Accept": "application/yang-data+json"}
        self.host = host
        self.notifier = notifier
        
        self.previous_state = {}
        self.is_reachable = True

    def check_network(self):
        """Polls RESTCONF API and evaluates interface states."""
        try:
            response = requests.get(self.url, auth=self.auth, headers=self.headers, verify=False, timeout=10)
            response.raise_for_status()
            
            if not self.is_reachable:
                logging.info(f"Target Node {self.host} Reconnected. Resuming monitoring.")
                self.is_reachable = True

            data = response.json()
            interfaces = data.get("ietf-interfaces:interfaces-state", {}).get("interface", [])
            
            for iface in interfaces:
                name = iface.get("name")
                current_status = iface.get("oper-status", "unknown")
                
                if name not in self.previous_state:
                    self.previous_state[name] = current_status
                    logging.info(f"Initialized monitoring: {name} (Status: {current_status})")
                    continue
                
                old_status = self.previous_state[name]
                if current_status != old_status:
                    logging.warning(f"STATE CHANGE: {name} ({old_status} -> {current_status})")
                    
                    if current_status == "down":
                        self.notifier.send_email_alert(name, old_status, current_status)
                    
                    self.previous_state[name] = current_status
                    
        except requests.exceptions.RequestException as e:
            if self.is_reachable:
                logging.critical(f"Target Node {self.host} Unreachable. Suppressing further connection errors.")
                self.is_reachable = False