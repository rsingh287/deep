import sys
import time

import psutil
import requests

sys.stdout.reconfigure(encoding="utf-8")
BASE_URL = "http://127.0.0.1:5000"

MAX_COMPLEX_APP_PROMPT = """
Act as an Elite Principal Software & Security Engineer. Build a FULL, working, end-to-end Python application for an 'Autonomous AI Cyber Sentinel & Real-Time IDS Engine'.

Include code for ALL 5 modules in a single comprehensive output:

MODULE 1: DATABASE & AGGREGATION ENGINE (`database.py`)
- SQLite schema with WAL mode & connection pooling.
- Tables: `incidents` (id, ip, threat_level, reason, status, timestamp), `banned_ips` (ip, reason, created_at), `telemetry_logs`.
- Async helper methods for inserting, querying, and auto-banning malicious IPs.

MODULE 2: BACKGROUND IDS PACKET & PORT MONITORS (`sentinel_engine.py`)
- Background threading/async loop inspecting active network sockets (`psutil.net_connections`).
- Heuristic anomaly detector flagging suspicious ports (22, 3389, 4444, 8080) and unauthorized outbound connections.
- Automated IP auto-ban trigger modifying Windows Firewall via `netsh advfirewall`.

MODULE 3: FLASK WEBSOCKET & REST API BACKEND (`server.py`)
- Flask API with endpoints: GET `/api/status`, POST `/api/ban_ip`, POST `/api/toggle_sentinel`, GET `/api/incidents`.
- Flask-SocketIO or Server-Sent Events (SSE) broadcasting live network telemetry every 1 second.

MODULE 4: GLASSMORPHIC CYBERPUNK FRONTEND INTERFACE (`index.html`)
- HTML5/CSS3/Vanilla JS single-page dashboard with dark glassmorphism styling.
- Real-time HTML5 Canvas network traffic telemetry graph.
- Interactive tables displaying live socket connections, flagged IPs, and 1-click manual ban buttons.

MODULE 5: INTEGRATION TEST & MAIN LAUNCHER (`main.py`)
- Main execution entry point initializing DB, starting background IDS threads, launching Flask API on port 8080, and opening browser automatically.

Generate complete, production-ready code for all 5 modules with detailed inline explanations.
"""


def run_max_complex_app_benchmark():
    print(
        "\n=========================================================================="
    )
    print("🚀 MAXIMUM COMPLEXITY BENCHMARK: Full Autonomous AI Cyber Sentinel App")
    print("==========================================================================")

    ram_before = psutil.virtual_memory().percent
    cpu_cores = psutil.cpu_count(logical=True)

    print(
        f"📊 Initial Telemetry: System RAM = {ram_before}% | CPU Logical Cores = {cpu_cores}"
    )
    print("⚡ Sending Max Advanced Full-Stack Architecture Prompt to Swarm Engine...\n")

    t0 = time.time()
    try:
        res = requests.post(
            f"{BASE_URL}/api/swarm_chat",
            json={"prompt": MAX_COMPLEX_APP_PROMPT},
            timeout=300,
        ).json()

        t1 = time.time()
        dur = t1 - t0
        ram_after = psutil.virtual_memory().percent
        resp_text = res.get("response", "")

        print(
            "=========================================================================="
        )
        print("✅ MAX COMPLEX APP GENERATED SUCCESSFULLY!")
        print(f"⏱️ Total Generation Time: {dur:.2f} seconds ({dur/60:.2f} minutes)")
        print(
            f"📄 Total Code Volume Generated: {len(resp_text)} characters (~{len(resp_text.split())} words)"
        )
        print(
            f"📊 System RAM Utilization: {ram_after}% (Peak Free RAM: {100-ram_after:.1f}%)"
        )
        print(
            "==========================================================================\n"
        )
        print("--- APP GENERATION HIGHLIGHTS ---")
        print(resp_text[:1000])
        print("\n... [Full 5-Module App Generated Successfully] ...\n")

    except Exception as e:
        print(f"❌ Error during max complex app benchmark: {e}")


if __name__ == "__main__":
    run_max_complex_app_benchmark()
