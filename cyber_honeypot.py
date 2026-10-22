import socket
import threading
import subprocess
import requests
import time
import db_engine

GUI_PORT = 5000
DECOY_PORTS = [2222, 8088]  # SSH decoy + HTTP decoy
BLOCKED_IPS = set()

def init_db():
    db_engine.execute_query("""
        CREATE TABLE IF NOT EXISTS honeypot_intrusions (
            id SERIAL PRIMARY KEY,
            ip_address TEXT,
            port INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def block_ip(ip):
    if ip in BLOCKED_IPS:
        return
    BLOCKED_IPS.add(ip)
    print(f"[CyberHoneypot] Executing defensive firewall rule against {ip}...")
    try:
        cmd = f"New-NetFirewallRule -DisplayName 'D.E.E.P Honeypot Auto-Block {ip}' -Direction Inbound -Action Block -RemoteAddress {ip}"
        subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    except Exception as e:
        print(f"[CyberHoneypot] Firewall error: {e}")

def alert_commander(ip, port):
    try:
        requests.post(f"http://127.0.0.1:{GUI_PORT}/api/deep/speak", json={
            "text": f"Warning Commander. A hostile network intrusion attempt was detected from IP {ip} on decoy port {port}. I have permanently blocked this address via the Windows Defender Firewall."
        }, timeout=2)
    except Exception:
        pass

def handle_connection(conn, addr, port):
    ip = addr[0]
    print(f"[CyberHoneypot] Intrusion detected from {ip} on port {port}!")
    try:
        conn.sendall(b"D.E.E.P Security Sentinel: Unauthorized Access Logged.\n")
    except:
        pass
    conn.close()
    
    # Alert, log, and block
    if ip not in BLOCKED_IPS:
        try:
            db_engine.execute_query("INSERT INTO honeypot_intrusions (ip_address, port) VALUES (%s, %s)", (ip, port))
        except Exception as e:
            print(f"[CyberHoneypot] DB Log error: {e}")
            
        alert_commander(ip, port)
        block_ip(ip)

def start_listener(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # SO_REUSEPORT is not available on Windows but is on Linux/macOS
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
    try:
        s.bind(('0.0.0.0', port))
        s.listen(5)
        print(f"[CyberHoneypot] Decoy port {port} active and listening.")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_connection, args=(conn, addr, port))
            t.daemon = True
            t.start()
    except OSError as e:
        print(f"[CyberHoneypot] Port {port} already in use (prior instance still active) — skipping.")
        s.close()
    except Exception as e:
        print(f"[CyberHoneypot] Failed to bind port {port}: {e}")
        s.close()

def main():
    print("[CyberHoneypot] Initializing Active Decoy Security Sentry...")
    init_db()
    for p in DECOY_PORTS:
        t = threading.Thread(target=start_listener, args=(p,))
        t.daemon = True
        t.start()
        
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
