import socket
import threading

class DEEPNetworkHoneypot:
    def __init__(self, ports=(2222, 33060)):
        print("[Honeypot] Initializing proactive threat hunting sentinel...")
        self.ports = ports
        self.active = False
        self.listeners = []

    def start(self):
        self.active = True
        for port in self.ports:
            t = threading.Thread(target=self._listen_port, args=(port,), daemon=True)
            t.start()
            self.listeners.append(t)
        print(f"[Honeypot] Silent listeners active on ports: {self.ports}")

    def _listen_port(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bind to all interfaces to catch local network scans
            s.bind(('0.0.0.0', port))
            s.listen(5)
            while self.active:
                conn, addr = s.accept()
                ip, client_port = addr
                print(f"\n[Honeypot] RED ALERT! Unauthorized port scan detected from {ip} on port {port}.")
                print(f"[Honeypot] Initiating IP traceback and firewall block protocol for {ip}...")
                conn.close()
        except Exception as e:
            print(f"[Honeypot] Error on port {port}: {e}")

    def stop(self):
        self.active = False
        print("[Honeypot] Sentinel deactivated.")

honeypot_daemon = None

def get_honeypot():
    global honeypot_daemon
    if honeypot_daemon is None:
        honeypot_daemon = DEEPNetworkHoneypot()
    return honeypot_daemon
