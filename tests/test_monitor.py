from cisco_alerting.monitor import NetworkMonitor

class DummyNotifier:
    def send_email_alert(self, name, old, new):
        pass

def test_initial_state():
    notifier = DummyNotifier()
    monitor = NetworkMonitor("10.0.0.1", "443", "admin", "cisco", notifier)
    
    assert monitor.is_reachable == True
    assert len(monitor.previous_state) == 0
    assert monitor.host == "10.0.0.1"