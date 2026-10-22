import os
import time
import subprocess
import re
import requests

GUI_PORT = 5000

def get_arp_table():
    """Parses local ARP table for active IPv4 devices with interface attribution."""
    try:
        output = subprocess.check_output(['arp', '-a']).decode('utf-8', errors='ignore')
        devices = []
        current_interface = ""
        for line in output.split('\n'):
            line_str = line.strip()
            if line_str.startswith("Interface:"):
                if_match = re.search(r'Interface:\s*([0-9.]+)', line_str)
                if if_match:
                    current_interface = if_match.group(1)
                continue

            match = re.search(r'([0-9]{1,3}(?:\.[0-9]{1,3}){3})\s+([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})', line)
            if match:
                ip, mac = match.groups()
                mac = mac.lower().replace("-", ":")
                # Exclude broadcast and multicast ranges
                if not ip.endswith('.255') and not ip.startswith(('224.', '239.', '127.')):
                    devices.append({"ip": ip, "mac": mac, "interface": current_interface})
        return devices
    except Exception as e:
        print(f"[NetworkSentinel] ARP Error: {e}")
        return []

def fetch_known_macs():
    """Retrieves already registered and known MACs from the backend."""
    try:
        res = requests.get(f"http://127.0.0.1:{GUI_PORT}/api/cyber/devices", timeout=3)
        if res.status_code == 200:
            data = res.json()
            return {d['mac'].lower() for d in data.get('devices', []) if d.get('mac')}
    except Exception:
        pass
    return set()

def classify_fallback_speech(ip, mac):
    """Generates clear, concise fallback speech strictly under 15 words for the operator."""
    operator_name = os.getenv("OPERATOR_NAME", "Commander")
    mac_clean = (mac or "").lower().replace("-", ":")
    if mac_clean.startswith("00:15:5d"):
        return f"{operator_name}, an internal Microsoft Hyper-V virtual connection was detected."
    elif mac_clean.startswith(("00:0c:29", "00:50:56", "08:00:27", "02:42")):
        return f"{operator_name}, an internal virtual connection was detected."
    elif mac_clean.startswith(("f0:18:98", "bc:d0:74", "ac:bc:32", "3c:22:fb", "28:cf:e9")):
        return f"{operator_name}, a new Apple device connected to your local network."
    elif mac_clean.startswith(("b0:a7:37", "34:14:b5", "24:fc:e5", "88:36:5f")):
        return f"{operator_name}, a new Samsung device joined the local network."
    else:
        last_octet = ip.split(".")[-1] if "." in ip else ip
        return f"{operator_name}, an unverified device connected at IP ending in dot {last_octet}."

def main():
    print("[NetworkSentinel] Initializing Autonomous Local LAN Sentinel...")
    known_macs = set()
    first_run = True

    # Allow Flask main server 4 seconds to start before first check
    time.sleep(4)

    while True:
        try:
            # Sync with database known devices
            db_macs = fetch_known_macs()
            known_macs.update(db_macs)

            devices = get_arp_table()

            if first_run:
                # If database was empty, register current devices as initial baseline
                if not db_macs and devices:
                    try:
                        requests.post(f"http://127.0.0.1:{GUI_PORT}/api/cyber/rescan", timeout=5)
                    except Exception:
                        pass
                for d in devices:
                    known_macs.add(d['mac'])
                print(f"[NetworkSentinel] Baseline established with {len(known_macs)} authorized devices.")
                first_run = False
            else:
                for d in devices:
                    mac = d['mac']
                    ip = d['ip']
                    if mac not in known_macs:
                        print(f"[NetworkSentinel] 🚨 INTRUSION/NEW DEVICE: {mac} at {ip}")
                        known_macs.add(mac)
                        
                        # Dispatch rich alert: Text Card in Chat, HUD Banner, and Spoken Audio
                        try:
                            res = requests.post(f"http://127.0.0.1:{GUI_PORT}/api/cyber/network_alert", json={
                                "ip": ip,
                                "mac": mac,
                                "interface": d.get("interface", ""),
                                "speak": True
                            }, timeout=5)
                            print(f"[NetworkSentinel] Alert dispatched successfully: {res.status_code}")
                        except Exception as post_err:
                            print(f"[NetworkSentinel] Alert dispatch error: {post_err}")
                            # Fallback direct speak with clear, natural pronunciation
                            try:
                                fallback_text = classify_fallback_speech(ip, mac)
                                requests.post(f"http://127.0.0.1:{GUI_PORT}/api/deep/speak", json={
                                    "text": fallback_text
                                }, timeout=2)
                            except Exception:
                                pass

        except Exception as loop_err:
            print(f"[NetworkSentinel] Loop error: {loop_err}")

        time.sleep(60) # Scan cycle every 60 seconds

if __name__ == '__main__':
    main()
