import os
import re
import time
import socket
import threading
import subprocess
import urllib.request
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
import db_engine

cyber_bp = Blueprint("cyber", __name__)

PENDING_ALERTS = []
PENDING_ALERTS_LOCK = threading.Lock()

# Offline OUI cache for top hardware vendors
KNOWN_OUIS = {
    "0c:ac:8a": "Sagemcom (Home Gateway / Modem)",
    "48:68:4a": "Intel Corporate (PC / Laptop)",
    "a0:e7:ae": "Commscope (AP / Gateway)",
    "98:fa:2e": "Sony Interactive Entertainment (PlayStation)",
    "f0:18:98": "Apple Inc. (iPhone / Mac)",
    "bc:d0:74": "Apple Inc.",
    "ac:bc:32": "Apple Inc.",
    "3c:22:fb": "Apple Inc.",
    "28:cf:e9": "Apple Inc.",
    "dc:a9:04": "Apple Inc.",
    "e0:b9:e5": "Apple Inc.",
    "50:ed:3c": "Apple Inc.",
    "5c:95:ae": "Apple Inc.",
    "88:66:5a": "Apple Inc.",
    "b8:78:2e": "Apple Inc.",
    "38:f9:d3": "Apple Inc.",
    "d0:03:df": "Apple Inc.",
    "60:f4:45": "Apple Inc.",
    "70:3e:ac": "Apple Inc.",
    "a4:83:e7": "Apple Inc.",
    "54:60:09": "Google LLC (Pixel / Nest)",
    "f4:f5:d8": "Google LLC (Chromecast / Home)",
    "d8:6c:63": "Google LLC",
    "b8:27:eb": "Raspberry Pi Foundation",
    "dc:a6:32": "Raspberry Pi Foundation",
    "e4:5f:01": "Raspberry Pi Foundation",
    "28:cd:c1": "Raspberry Pi Foundation",
    "2c:cf:67": "Raspberry Pi Foundation",
    "00:0c:29": "VMware Virtual Machine",
    "00:50:56": "VMware Virtual Machine",
    "00:15:5d": "Microsoft Hyper-V",
    "08:00:27": "Oracle VirtualBox",
    "52:54:00": "QEMU / KVM Virtual Machine",
    "b0:a7:37": "Samsung Electronics",
    "34:14:b5": "Samsung Electronics",
    "24:fc:e5": "Samsung Electronics",
    "88:36:5f": "Samsung Electronics",
    "cc:07:ab": "Samsung Electronics",
    "a4:70:d6": "Samsung Electronics",
    "00:26:37": "Samsung Electronics",
    "74:a3:4a": "Samsung Electronics",
    "94:65:2d": "Samsung Electronics",
    "68:db:ca": "Amazon Technologies (Echo / Kindle)",
    "fc:65:de": "Amazon Technologies",
    "74:c2:46": "Amazon Technologies",
    "40:b4:cd": "Amazon Technologies",
    "50:dc:e7": "Amazon Technologies",
    "b4:7c:9c": "Amazon Technologies",
    "00:fc:8b": "Amazon Technologies",
    "3c:5a:37": "Amazon Technologies",
    "a0:02:dc": "Amazon Technologies",
    "2c:3a:e8": "Espressif Inc. (ESP32 / ESP8266 IoT)",
    "30:ae:a4": "Espressif Inc. (ESP32 IoT)",
    "24:0a:c4": "Espressif Inc. (ESP32 IoT)",
    "84:0d:8e": "Espressif Inc. (Smart Device)",
    "e8:31:cd": "Espressif Inc. (Smart Device)",
    "cc:50:e3": "Espressif Inc. (Smart Device)",
    "ec:fa:bc": "Espressif Inc. (Smart Device)",
    "18:fe:34": "Espressif Inc. (Smart Device)",
    "44:17:93": "TP-Link Technologies",
    "50:c7:bf": "TP-Link Technologies",
    "c0:06:c3": "TP-Link Technologies",
    "70:4f:57": "TP-Link Technologies",
    "98:48:27": "TP-Link Technologies",
    "e8:48:b8": "TP-Link Technologies",
    "00:1d:0f": "TP-Link Technologies",
    "d8:07:b6": "TP-Link Technologies",
    "00:e0:4c": "Realtek Semiconductor",
    "54:ee:75": "Wistron InfoComm",
    "00:11:32": "Synology Inc.",
    "00:08:9b": "QNAP Systems",
    "b8:27:c5": "Sony Corporation",
    "00:04:1f": "Sony Interactive Entertainment",
    "00:13:15": "Sony Interactive Entertainment",
    "00:15:c1": "Sony Interactive Entertainment",
    "00:19:c5": "Sony Interactive Entertainment",
    "00:1d:0d": "Sony Interactive Entertainment",
    "00:24:8d": "Sony Interactive Entertainment",
    "28:0d:fc": "Sony Interactive Entertainment",
    "70:9e:29": "Sony Interactive Entertainment",
    "ac:36:13": "Sony Interactive Entertainment",
    "c8:63:f1": "Sony Interactive Entertainment",
    "e0:ae:5e": "Sony Interactive Entertainment",
    "fc:0f:e6": "Sony Interactive Entertainment",
    "40:99:22": "LG Electronics",
    "58:fc:db": "LG Electronics",
    "a8:23:fe": "LG Electronics",
    "c4:36:6c": "LG Electronics",
    "cc:2d:8c": "LG Electronics",
    "b8:bc:5b": "Roku Inc.",
    "d8:31:34": "Roku Inc.",
    "ac:3a:7a": "Roku Inc.",
    "dc:3a:5e": "Nintendo Co., Ltd. (Switch / Console)",
    "9c:e6:35": "Nintendo Co., Ltd.",
    "e8:4e:06": "Nintendo Co., Ltd.",
    "40:f4:07": "Netgear",
    "a0:04:60": "Netgear",
    "20:e5:2a": "Netgear",
    "28:80:88": "Netgear",
    "9c:3d:cf": "Netgear",
    "c0:ff:d4": "Netgear",
    "00:1f:33": "Netgear",
    "00:24:b2": "Netgear",
    "00:26:f2": "Netgear",
    "00:8e:f2": "Acer Incorporated",
    "00:03:7f": "Atheros Communications",
    "00:18:de": "Intel Corporation",
    "00:1b:21": "Intel Corporation",
    "00:21:6a": "Intel Corporation",
    "00:23:14": "Intel Corporation",
    "00:24:d7": "Intel Corporation",
    "00:27:0e": "Intel Corporation",
    "00:db:df": "Intel Corporation",
    "34:13:e8": "Intel Corporation",
    "3c:f8:62": "Intel Corporation",
    "48:51:b7": "Intel Corporation",
    "60:67:20": "Intel Corporation",
    "68:05:ca": "Intel Corporation",
    "78:0c:b8": "Intel Corporation",
    "7c:b0:c2": "Intel Corporation",
    "8c:ec:4b": "Intel Corporation",
    "a4:4e:31": "Intel Corporation",
    "c8:5b:76": "Intel Corporation",
    "e4:70:b8": "Intel Corporation",
    "ec:2e:98": "Intel Corporation",
    "f8:32:e4": "Intel Corporation",
    "fc:77:74": "Intel Corporation",
}


def init_cyber_tables():
    """Initializes tables for network sentinel devices and security incident logs."""
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS network_devices (
                id SERIAL PRIMARY KEY,
                mac_address TEXT UNIQUE NOT NULL,
                ip_address TEXT NOT NULL,
                hostname TEXT,
                vendor TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'UNKNOWN',
                open_ports TEXT DEFAULT ''
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                details TEXT NOT NULL,
                ip_address TEXT
            );
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CyberRoutes] DB init error: {e}")


init_cyber_tables()


def queue_alert(alert_data):
    """Enqueues an alert for frontend delivery."""
    with PENDING_ALERTS_LOCK:
        PENDING_ALERTS.append(alert_data)
        if len(PENDING_ALERTS) > 50:
            del PENDING_ALERTS[:-50]


def get_and_clear_pending_alerts():
    """Retrieves all pending alerts and clears the queue."""
    with PENDING_ALERTS_LOCK:
        alerts = list(PENDING_ALERTS)
        PENDING_ALERTS.clear()
        return alerts


def resolve_mac_vendor(mac_str):
    """Resolves manufacturer from MAC address with offline lookup and online fallback."""
    if not mac_str:
        return "Unknown Vendor"
    cleaned = mac_str.lower().replace("-", ":")
    prefix = cleaned[:8]
    if prefix in KNOWN_OUIS:
        return KNOWN_OUIS[prefix]
    
    # Quick online fallback via api.maclookup.app (2 second timeout)
    try:
        url = f"https://api.maclookup.app/v2/macs/{mac_str}"
        req = urllib.request.Request(url, headers={"User-Agent": "DEEP-Sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            company = data.get("company")
            if company:
                KNOWN_OUIS[prefix] = company
                return company
    except Exception:
        pass
    
    return "Local Network Device"


def resolve_ip_hostname(ip_str):
    """Resolves hostname for an IP address."""
    try:
        name, _, _ = socket.gethostbyaddr(ip_str)
        return name
    except Exception:
        return "Local Host"


def post_chat_message(content, title="Security & Network Sentinel"):
    """Inserts a system message directly into the current active chat session."""
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM chat_sessions ORDER BY updated_at DESC NULLS LAST LIMIT 1")
        row = cur.fetchone()
        if row:
            chat_id = row[0]
        else:
            chat_id = f"chat_{int(time.time()*1000)}"
            cur.execute("INSERT INTO chat_sessions (chat_id, title) VALUES (?, ?)", (chat_id, title))
            
        cur.execute("INSERT INTO chat_messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, "ai", content))
        cur.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        return chat_id
    except Exception as e:
        print(f"[CyberRoutes] Chat insert error: {e}")
        return None


def speak_alert_text(text):
    """Speaks alert text asynchronously using Windows SAPI if voice is not muted."""
    try:
        import voice_state
        if voice_state.is_voice_muted():
            print(f"[CyberRoutes] Voice is OFF (muted globally). Alert speech suppressed: '{text[:60]}...'")
            return
    except Exception:
        pass

    def _worker():
        try:
            import voice_state
            if voice_state.is_voice_muted():
                return
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            sp = win32com.client.Dispatch("SAPI.SpVoice")
            sp.Rate = 1
            sp.Volume = 100
            sp.Speak(text)
        except Exception as e:
            print(f"[CyberRoutes] SAPI speak error: {e}")
    threading.Thread(target=_worker, daemon=True).start()


def classify_network_device(ip, mac, vendor, hostname, interface=""):
    """
    Intelligently classifies a detected device to distinguish between:
    1. 'VIRTUAL_ADAPTER': Internal virtualization (Hyper-V, WSL2, Docker, VMware, VirtualBox)
    2. 'KNOWN_PHYSICAL': Recognized physical device manufacturer (Apple, Samsung, Intel, etc.)
    3. 'UNVERIFIED': Truly unknown / untrusted device on the local network

    Generates clear, concise spoken feedback strictly under 15 words for the Commander.
    """
    mac_clean = (mac or "").lower().replace("-", ":").strip()
    vendor_clean = (vendor or "").lower().strip()
    ip_clean = (ip or "").strip()
    host_clean = (hostname or "").lower().strip()

    # 1. Virtual Adapter Detection (Hyper-V, WSL2, Docker, VMware, VirtualBox, QEMU)
    is_hyperv_wsl = (
        mac_clean.startswith("00:15:5d") or 
        "hyper-v" in vendor_clean or 
        "wsl" in vendor_clean or 
        "wsl" in host_clean or
        (ip_clean.startswith("172.") and "microsoft" in vendor_clean)
    )
    is_vmware = (
        mac_clean.startswith(("00:0c:29", "00:50:56", "00:05:69")) or 
        "vmware" in vendor_clean
    )
    is_vbox = (
        mac_clean.startswith("08:00:27") or 
        "virtualbox" in vendor_clean
    )
    is_docker = (
        mac_clean.startswith("02:42") or 
        "docker" in vendor_clean or 
        "docker" in host_clean
    )
    is_qemu = (
        mac_clean.startswith("52:54:00") or 
        "qemu" in vendor_clean or 
        "kvm" in vendor_clean
    )

    spoken_text = ""
    operator_name = os.getenv("OPERATOR_NAME", "Commander")
    if is_hyperv_wsl or is_vmware or is_vbox or is_docker or is_qemu:
        if is_hyperv_wsl:
            friendly_label = "Microsoft Hyper-V / WSL2 Virtual Subsystem"
            device_insight = "This interface is an internal Windows virtual networking switch used by WSL2 or Hyper-V on this PC. It is not an outside intruder."
            spoken_text = f"{operator_name}, an internal Microsoft Hyper-V virtual connection was detected."
        elif is_vmware:
            friendly_label = "VMware Virtual Network Adapter"
            device_insight = "This interface is an internal virtual adapter used by VMware on this workstation."
            spoken_text = f"{operator_name}, an internal VMware virtual connection was detected."
        elif is_vbox:
            friendly_label = "Oracle VirtualBox Virtual Adapter"
            device_insight = "This interface is an internal virtual adapter used by VirtualBox on this workstation."
            spoken_text = f"{operator_name}, an internal VirtualBox virtual connection was detected."
        elif is_docker:
            friendly_label = "Docker Virtual Network Bridge"
            device_insight = "This interface is an internal virtual container bridge used by Docker on this PC."
            spoken_text = f"{operator_name}, an internal Docker virtual connection was detected."
        else:
            friendly_label = "Internal Virtual Subsystem"
            device_insight = "This is an internal virtual networking interface running locally on your computer."
            spoken_text = f"{operator_name}, an internal virtual connection was detected."

        return {
            "category": "VIRTUAL_ADAPTER",
            "is_virtual": True,
            "friendly_label": friendly_label,
            "device_insight": device_insight,
            "spoken_text": spoken_text,
            "status": "LOCAL VIRTUAL INTERFACE (SAFE)",
            "badge_text": "LOCAL SUBSYSTEM (SAFE)",
            "theme_color": "cyan",
            "header_icon": "💻",
            "header_title": "CYBER SENTINEL: INTERNAL VIRTUAL ADAPTER"
        }

    # 2. Known Physical Device Vendor
    unknown_vendor_tags = {"unknown vendor", "local network device", "unknown", ""}
    if vendor_clean and vendor_clean not in unknown_vendor_tags:
        if "apple" in vendor_clean:
            friendly_label = "Apple Mobile / Mac Device"
            device_insight = "A new Apple device joined your local Wi-Fi. Verify if this is your iPhone, iPad, or Mac."
            spoken_text = f"{operator_name}, a new Apple device connected to your local network."
        elif "samsung" in vendor_clean:
            friendly_label = "Samsung Galaxy / Smart Device"
            device_insight = "A new Samsung device joined your local Wi-Fi. Verify if this is your Galaxy phone or smart TV."
            spoken_text = f"{operator_name}, a new Samsung device joined the local network."
        elif "google" in vendor_clean:
            friendly_label = "Google Pixel / Nest Smart Device"
            device_insight = "A Google device (Pixel or Nest) joined your local Wi-Fi network."
            spoken_text = f"{operator_name}, a Google smart device connected to the network."
        elif "sony" in vendor_clean:
            friendly_label = "Sony PlayStation / Audio Device"
            device_insight = "A Sony entertainment or PlayStation console connected to your local network."
            spoken_text = f"{operator_name}, a Sony entertainment device joined your network."
        elif "raspberry" in vendor_clean:
            friendly_label = "Raspberry Pi Single-Board Computer"
            device_insight = "A Raspberry Pi IoT or server node joined your local network."
            spoken_text = f"{operator_name}, a Raspberry Pi device connected to your network."
        elif any(k in vendor_clean for k in ("intel", "dell", "hp", "lenovo", "acer", "asus")):
            brand = vendor.split()[0]
            friendly_label = f"{vendor} Workstation / PC"
            device_insight = f"A personal computer or laptop manufactured by {vendor} joined your local network."
            spoken_text = f"{operator_name}, a new {brand} computer joined your network."
        elif any(k in vendor_clean for k in ("cisco", "netgear", "tp-link", "commscope", "sagemcom")):
            brand = vendor.split()[0]
            friendly_label = f"{vendor} Gateway / Access Point"
            device_insight = f"A networking router, switch, or access point from {vendor} was detected on the LAN."
            spoken_text = f"{operator_name}, a new {brand} network device was detected."
        else:
            brand = vendor.split()[0]
            friendly_label = f"{vendor} Hardware"
            device_insight = f"A device manufactured by {vendor} has connected to your local network."
            spoken_text = f"{operator_name}, a new {brand} device joined the local network."

        return {
            "category": "KNOWN_PHYSICAL",
            "is_virtual": False,
            "friendly_label": friendly_label,
            "device_insight": device_insight,
            "spoken_text": spoken_text,
            "status": "NEW LOCAL DEVICE (VERIFY)",
            "badge_text": "RECOGNIZED VENDOR",
            "theme_color": "amber",
            "header_icon": "📡",
            "header_title": f"CYBER SENTINEL: NEW DEVICE DETECTED ({vendor})"
        }

    # 3. Truly Unverified Device
    last_octet = ip_clean.split(".")[-1] if "." in ip_clean else ip_clean
    return {
        "category": "UNVERIFIED",
        "is_virtual": False,
        "friendly_label": "Unverified Network Hardware",
        "device_insight": "An unrecognized physical hardware device joined your local network. Deploy a port scan or inspect the MAC address to identify it.",
        "spoken_text": f"{operator_name}, an unverified device connected at IP ending in dot {last_octet}.",
        "status": "UNVERIFIED (QUARANTINE)",
        "badge_text": "UNKNOWN HARDWARE",
        "theme_color": "red",
        "header_icon": "🚨",
        "header_title": "CYBER SENTINEL: UNVERIFIED DEVICE DETECTED"
    }


def generate_alert_card(ip, mac, vendor, hostname, detected_time, classification=None):
    """Generates an interactive, tactical cyber defense card HTML."""
    if not classification:
        classification = classify_network_device(ip, mac, vendor, hostname)

    sanitized_ip = ip.replace(".", "_")
    theme = classification.get("theme_color", "red")

    if theme == "cyan":
        border_style = "border:1px solid rgba(56,189,248,0.4); background:rgba(2,132,199,0.08); box-shadow:0 0 20px rgba(2,132,199,0.18);"
        header_color = "#38bdf8"
        dot_color = "#38bdf8"
        badge_style = "background:rgba(2,132,199,0.25); color:#7dd3fc; border:1px solid rgba(56,189,248,0.4);"
        callout_style = "background:rgba(2,132,199,0.14); border-left:3px solid #38bdf8; color:#bae6fd;"
        status_color = "#38bdf8"
        trust_btn_text = "✅ Auto-Trust Subsystem"
        scan_btn_text = "🔍 Inspect Virtual Ports"
    elif theme == "amber":
        border_style = "border:1px solid rgba(245,158,11,0.4); background:rgba(245,158,11,0.08); box-shadow:0 0 20px rgba(245,158,11,0.18);"
        header_color = "#fbbf24"
        dot_color = "#f59e0b"
        badge_style = "background:rgba(245,158,11,0.2); color:#fde68a; border:1px solid rgba(245,158,11,0.4);"
        callout_style = "background:rgba(245,158,11,0.14); border-left:3px solid #f59e0b; color:#fef3c7;"
        status_color = "#fde047"
        trust_btn_text = "✅ Mark as Trusted"
        scan_btn_text = "🔍 Deploy Port Scan"
    else:
        border_style = "border:1px solid #ef4444; background:rgba(239,68,68,0.08); box-shadow:0 0 20px rgba(239,68,68,0.2);"
        header_color = "#ef4444"
        dot_color = "#ef4444"
        badge_style = "background:rgba(239,68,68,0.2); color:#fca5a5; border:1px solid rgba(239,68,68,0.4);"
        callout_style = "background:rgba(239,68,68,0.14); border-left:3px solid #ef4444; color:#fecaca;"
        status_color = "#f87171"
        trust_btn_text = "✅ Mark as Trusted"
        scan_btn_text = "🔍 Deploy Port Scan"

    return f"""<div class="cockpit-tactical-alert tactical-device-alert" id="tactical-alert-{sanitized_ip}" data-ip="{ip}" data-mac="{mac}" style="{border_style} border-radius:12px; padding:14px; margin:10px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <div style="font-weight:800; color:{header_color}; font-size:0.92rem; display:flex; align-items:center; gap:8px;">
      <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{dot_color}; box-shadow:0 0 10px {dot_color};"></span>
      {classification['header_icon']} {classification['header_title']}
    </div>
    <span style="font-size:0.7rem; font-family:'JetBrains Mono', monospace; {badge_style} padding:2px 8px; border-radius:4px;">{classification['badge_text']}</span>
  </div>
  <div style="display:grid; grid-template-columns:auto 1fr; gap:6px 14px; font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#e2e8f0; background:rgba(0,0,0,0.3); padding:10px 14px; border-radius:8px; border:1px solid rgba(255,255,255,0.06);">
    <span style="color:#94a3b8;">IP Address:</span><span style="font-weight:700; color:#38bdf8;">{ip}</span>
    <span style="color:#94a3b8;">MAC Address:</span><span style="color:#cbd5e1;">{mac}</span>
    <span style="color:#94a3b8;">Manufacturer:</span><span style="color:#fde047; font-weight:600;">{vendor}</span>
    <span style="color:#94a3b8;">Classification:</span><span style="color:#7dd3fc; font-weight:600;">{classification['friendly_label']}</span>
    <span style="color:#94a3b8;">Hostname:</span><span style="color:#cbd5e1;">{hostname}</span>
    <span style="color:#94a3b8;">Detected At:</span><span style="color:#94a3b8;">{detected_time}</span>
    <span style="color:#94a3b8;">Defense Status:</span><span id="device-status-{sanitized_ip}" style="color:{status_color}; font-weight:700;">{classification['status']}</span>
  </div>
  <div style="margin-top:10px; padding:8px 12px; {callout_style} border-radius:6px; font-size:0.78rem; line-height:1.45;">
    💡 <strong>Intelligence Brief:</strong> {classification['device_insight']}
  </div>
  <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
    <button onclick="trustNetworkDevice('{mac}', '{ip}')" class="btn-tactical-trust" style="display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.15); color:#34d399; border:1px solid #10b981; padding:6px 14px; border-radius:6px; font-size:0.78rem; font-weight:700; cursor:pointer; transition:all 0.2s;">
      {trust_btn_text}
    </button>
    <button onclick="scanNetworkDevice('{ip}')" class="btn-tactical-scan" style="display:inline-flex; align-items:center; gap:6px; background:#0284c7; color:#fff; border:1px solid #38bdf8; padding:6px 14px; border-radius:6px; font-size:0.78rem; font-weight:700; cursor:pointer; transition:all 0.2s;">
      {scan_btn_text}
    </button>
    <button onclick="blockNetworkDevice('{ip}')" class="btn-tactical-block" style="display:inline-flex; align-items:center; gap:6px; background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.4); padding:6px 14px; border-radius:6px; font-size:0.78rem; font-weight:700; cursor:pointer; transition:all 0.2s;">
      🛡️ Block IP at Firewall
    </button>
  </div>
  <div id="scan-results-{sanitized_ip}" style="margin-top:10px; display:none; font-family:'JetBrains Mono', monospace; font-size:0.75rem; background:rgba(0,0,0,0.4); padding:10px; border-radius:6px; border:1px solid rgba(56,189,248,0.2);"></div>
</div>"""


def run_fast_port_scan(ip):
    """Scans common network ports quickly using multi-threaded sockets."""
    port_map = {
        21: "FTP (File Transfer)",
        22: "SSH (Secure Shell)",
        23: "Telnet (Unencrypted CLI)",
        53: "DNS (Domain Name Service)",
        80: "HTTP (Web Server)",
        135: "MS-RPC (Windows RPC)",
        139: "NetBIOS (Session Service)",
        443: "HTTPS (Encrypted Web)",
        445: "SMB (Windows File Sharing)",
        3389: "RDP (Remote Desktop Protocol)",
        5000: "UPnP / Local AI / Flask",
        5432: "PostgreSQL Database",
        8000: "HTTP-Alt / Web Service",
        8080: "HTTP-Proxy / Alternate Web",
        8443: "HTTPS-Alt",
        9000: "Portainer / Media Server"
    }
    open_ports = []
    
    def check_p(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.35)
        try:
            if s.connect_ex((ip, p)) == 0:
                return {"port": p, "service": port_map.get(p, "Custom Service")}
        except Exception:
            pass
        finally:
            s.close()
        return None

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(check_p, list(port_map.keys()))
        for r in results:
            if r:
                open_ports.append(r)
                
    return open_ports


# -------------------------------------------------------------
# REST ENDPOINTS
# -------------------------------------------------------------

@cyber_bp.route("/api/cyber/network_alert", methods=["POST"])
def cyber_network_alert():
    """Receives detection event from Network Sentinel daemon with smart classification."""
    data = request.json or {}
    ip = data.get("ip", "").strip()
    mac = data.get("mac", "").strip().lower()
    should_speak = data.get("speak", True)
    interface = data.get("interface", "")
    
    if not ip or not mac:
        return jsonify({"success": False, "error": "IP and MAC address are required"}), 400

    vendor = data.get("vendor") or resolve_mac_vendor(mac)
    hostname = data.get("hostname") or resolve_ip_hostname(ip)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Perform intelligent device classification
    classification = classify_network_device(ip, mac, vendor, hostname, interface)
    initial_status = "LOCAL VIRTUAL INTERFACE" if classification["is_virtual"] else "UNKNOWN"

    # 1. Upsert device into database
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO network_devices (mac_address, ip_address, hostname, vendor, first_seen, last_seen, status)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
            ON CONFLICT (mac_address) DO UPDATE SET
                ip_address = EXCLUDED.ip_address,
                hostname = EXCLUDED.hostname,
                vendor = EXCLUDED.vendor,
                last_seen = CURRENT_TIMESTAMP;
        """, (mac, ip, hostname, vendor, initial_status))
        
        # 2. Log security event with appropriate severity
        severity = "INFO" if classification["is_virtual"] else "WARNING"
        log_event = "VIRTUAL_ADAPTER_DETECTED" if classification["is_virtual"] else "UNKNOWN_DEVICE"
        cur.execute("""
            INSERT INTO security_logs (event_type, severity, details, ip_address)
            VALUES (?, ?, ?, ?);
        """, (log_event, severity, f"{classification['friendly_label']}: {vendor} at {ip} (MAC {mac})", ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CyberRoutes] DB upsert error: {e}")

    # 3. Generate HTML card and post to active chat session
    html_card = generate_alert_card(ip, mac, vendor, hostname, now_str, classification)
    post_chat_message(html_card, title="🚨 Network Sentinel Security")

    # 4. Queue alert for Cockpit UI banner
    alert_payload = {
        "id": f"alert_{int(time.time()*1000)}",
        "type": "UNKNOWN_DEVICE",
        "title": classification["friendly_label"],
        "ip": ip,
        "mac": mac,
        "vendor": vendor,
        "hostname": hostname,
        "timestamp": now_str,
        "category": classification["category"],
        "is_virtual": classification["is_virtual"],
        "html_card": html_card,
        "spoken_text": classification["spoken_text"]
    }
    queue_alert(alert_payload)

    # 5. Speak concise, natural voice announcement
    if should_speak:
        speak_alert_text(classification["spoken_text"])

    return jsonify({
        "success": True,
        "message": f"Alert generated and dispatched for device {ip}",
        "ip": ip,
        "mac": mac,
        "vendor": vendor,
        "hostname": hostname,
        "category": classification["category"],
        "is_virtual": classification["is_virtual"],
        "spoken_text": classification["spoken_text"]
    })


@cyber_bp.route("/api/cyber/devices", methods=["GET"])
def cyber_get_devices():
    """Returns all recorded network devices, deduplicated by IP address to prevent virtual MAC duplicates."""
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, mac_address, ip_address, hostname, vendor, first_seen, last_seen, status, open_ports
            FROM network_devices
            ORDER BY last_seen DESC;
        """)
        rows = cur.fetchall()
        conn.close()
        
        devices = []
        seen_ips = set()
        for r in rows:
            ip = r[2]
            # Deduplicate by IP to ensure rotated virtual MACs (e.g. Hyper-V / WSL) never show duplicate entries
            if ip in seen_ips:
                continue
            seen_ips.add(ip)
            devices.append({
                "id": r[0],
                "mac": (r[1] or "").lower().replace("-", ":"),
                "ip": ip,
                "hostname": r[3] or "Unknown",
                "vendor": r[4] or "Unknown Vendor",
                "first_seen": str(r[5]) if r[5] else "",
                "last_seen": str(r[6]) if r[6] else "",
                "status": r[7] or "UNKNOWN",
                "open_ports": r[8] or ""
            })
        return jsonify({"success": True, "devices": devices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cyber_bp.route("/api/cyber/rescan", methods=["POST"])
def cyber_rescan():
    """Immediately performs an ARP scan and registers/updates all local LAN devices without duplicates."""
    try:
        output = subprocess.check_output(['arp', '-a']).decode('utf-8', errors='ignore')
        detected = []
        for line in output.split('\n'):
            match = re.search(r'([0-9]{1,3}(?:\.[0-9]{1,3}){3})\s+([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})', line)
            if match:
                ip, mac = match.groups()
                mac = mac.lower().replace("-", ":")
                if not ip.endswith('.255') and not ip.startswith(('224.', '239.', '127.')):
                    vendor = resolve_mac_vendor(mac)
                    hostname = resolve_ip_hostname(ip)
                    detected.append({"ip": ip, "mac": mac, "vendor": vendor, "hostname": hostname})

        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        for d in detected:
            # Prune stale records where the IP is the same but MAC address changed (e.g. Hyper-V virtual adapter reset)
            cur.execute("DELETE FROM network_devices WHERE ip_address = ? AND mac_address != ?;", (d['ip'], d['mac']))
            cur.execute("""
                INSERT INTO network_devices (mac_address, ip_address, hostname, vendor, first_seen, last_seen, status)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'UNKNOWN')
                ON CONFLICT (mac_address) DO UPDATE SET
                    ip_address = EXCLUDED.ip_address,
                    hostname = EXCLUDED.hostname,
                    vendor = EXCLUDED.vendor,
                    last_seen = CURRENT_TIMESTAMP;
            """, (d['mac'], d['ip'], d['hostname'], d['vendor']))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "count": len(detected), "devices": detected})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cyber_bp.route("/api/cyber/port_scan", methods=["POST"])
def cyber_port_scan():
    """Deploys a multi-threaded socket port scan on target IP and posts findings to chat."""
    data = request.json or {}
    ip = data.get("ip", "").strip()
    if not ip:
        return jsonify({"success": False, "error": "Target IP required"}), 400

    open_ports = run_fast_port_scan(ip)
    ports_summary = ", ".join([f"{p['port']} ({p['service']})" for p in open_ports]) if open_ports else "No common services exposed"

    # Update open_ports in network_devices
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE network_devices SET open_ports = ? WHERE ip_address = ?", (ports_summary, ip))
        cur.execute("""
            INSERT INTO security_logs (event_type, severity, details, ip_address)
            VALUES (?, ?, ?, ?);
        """, ("PORT_SCAN", "INFO", f"Port scan completed for {ip}. Open ports: {ports_summary}", ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CyberRoutes] DB port scan update error: {e}")

    # Generate Report Card
    ports_html = "".join([f"<li style='margin-bottom:3px;'><strong>Port {p['port']}</strong>: <span style='color:#38bdf8;'>{p['service']}</span></li>" for p in open_ports])
    if not open_ports:
        ports_html = "<li style='color:#4ade80;'>All standard ports filtered or closed. No exposed services found.</li>"

    scan_card = f"""<div class="cockpit-port-scan tactical-device-alert" style="border:1px solid #0284c7; background:rgba(2,132,199,0.08); border-radius:10px; padding:12px; margin:8px 0;">
  <div style="font-weight:700; color:#38bdf8; font-size:0.88rem; margin-bottom:8px;">
    🔍 PORT SCAN AUDIT REPORT: <code>{ip}</code>
  </div>
  <div style="font-family:'JetBrains Mono', monospace; font-size:0.78rem;">
    <ul style="padding-left:18px; color:#e2e8f0; margin:0;">
      {ports_html}
    </ul>
  </div>
</div>"""

    post_chat_message(scan_card)
    return jsonify({
        "success": True,
        "ip": ip,
        "open_ports": open_ports,
        "summary": ports_summary,
        "html": scan_card
    })


@cyber_bp.route("/api/cyber/block_device", methods=["POST"])
def cyber_block_device():
    """Blocks an IP address using Windows Firewall rule."""
    data = request.json or {}
    ip = data.get("ip", "").strip()
    if not ip or ip.startswith("127."):
        return jsonify({"success": False, "error": "Invalid IP address provided"}), 400

    try:
        rule_name = f"DEEP_Block_{ip.replace('.', '_')}"
        cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)

        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE network_devices SET status = 'BLOCKED' WHERE ip_address = ?", (ip,))
        cur.execute("""
            INSERT INTO security_logs (event_type, severity, details, ip_address)
            VALUES (?, ?, ?, ?);
        """, ("FIREWALL_BLOCK", "WARNING", f"Windows Firewall inbound block rule created for IP {ip}", ip))
        conn.commit()
        conn.close()

        block_msg = f"🛡️ **DEFENSIVE ACTION EXECUTED:** Remote IP `{ip}` has been blocked at the Windows Defender Firewall layer."
        post_chat_message(block_msg)
        return jsonify({"success": True, "message": f"Successfully blocked IP {ip}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cyber_bp.route("/api/cyber/trust_device", methods=["POST"])
def cyber_trust_device():
    """Marks a device as verified/trusted in the database."""
    data = request.json or {}
    mac = data.get("mac", "").strip().lower()
    ip = data.get("ip", "").strip()
    
    if not mac and not ip:
        return jsonify({"success": False, "error": "MAC or IP address required"}), 400

    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        if mac:
            cur.execute("UPDATE network_devices SET status = 'TRUSTED' WHERE mac_address = ?", (mac,))
        else:
            cur.execute("UPDATE network_devices SET status = 'TRUSTED' WHERE ip_address = ?", (ip,))
            
        cur.execute("""
            INSERT INTO security_logs (event_type, severity, details, ip_address)
            VALUES (?, ?, ?, ?);
        """, ("DEVICE_TRUSTED", "INFO", f"Device marked as TRUSTED: MAC {mac} / IP {ip}", ip))
        conn.commit()
        conn.close()

        trust_msg = f"✅ **DEVICE VERIFIED:** Host `{ip or mac}` has been marked as a trusted authorized device."
        post_chat_message(trust_msg)
        return jsonify({"success": True, "message": "Device marked as trusted"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cyber_bp.route("/api/cyber/pending_alerts", methods=["GET"])
def cyber_pending_alerts():
    """Returns any unread alerts and clears the queue."""
    alerts = get_and_clear_pending_alerts()
    return jsonify({"success": True, "alerts": alerts})
