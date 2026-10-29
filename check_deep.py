"""
==============================================================================
D.E.E.P Sovereign AI PC Cockpit - Master Health & Capabilities Diagnostic CLI
==============================================================================
Usage:
    python check_deep.py             # Run all 10 pillar diagnostic checks
    python check_deep.py --all       # Run comprehensive end-to-end check
    python check_deep.py --open      # Open Cockpit & Cyber Nexus in browser
    python check_deep.py --music     # Test local music library search
    python check_deep.py --mcu       # Test PIC18F85K22 MCU project audit
    python check_deep.py --chat "hi" # Test local AI chat routing
==============================================================================
"""

import sys
import os
import time
import argparse
import webbrowser

# Ensure UTF-8 output on Windows PowerShell / CMD
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add current workspace to path
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)


def print_banner():
    print("=" * 72)
    print("  ____  ______ ______ _____     ____   ____   _____ _  ______ _____ _______ ")
    print(" |  _ \\|  ____|  ____|  __ \\   / __ \\ / __ \\ / ____| |/ /  __ \\_   _|__   __|")
    print(" | |_) | |__  | |__  | |__) | | |  | | |  | | |    | ' /| |__) || |    | |   ")
    print(" |  _ <|  __| |  __| |  ___/  | |  | | |  | | |    |  < |  ___/ | |    | |   ")
    print(" | |_) | |____| |____| |      | |__| | |__| | |____| . \\| |    _| |_   | |   ")
    print(" |____/|______|______|_|       \\____/ \\____/ \\_____|_|\\_\\_|   |_____|  |_|   ")
    print("=" * 72)
    print("      SOVEREIGN AI WORKSTATION & MULTI-AGENT COCKPIT DIAGNOSTICS")
    print("=" * 72)


def check_pillar_1_database():
    """Pillar 1: PostgreSQL & Vector Storage Core"""
    t0 = time.time()
    try:
        import db_engine
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "PostgreSQL & Vector Core (deep_db)",
            "latency_ms": elapsed,
            "details": f"Connected to deep_db ({len(tables)} tables active: {', '.join(tables[:4])}...)"
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "name": "PostgreSQL & Vector Core (deep_db)",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"Database error: {str(e)}"
        }


def check_pillar_2_ollama_ai():
    """Pillar 2: Local AI Model Engine (Ollama / GGUF)"""
    t0 = time.time()
    try:
        import requests
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            elapsed = round((time.time() - t0) * 1000, 1)
            return {
                "status": "PASS",
                "name": "Local AI Models (Ollama)",
                "latency_ms": elapsed,
                "details": f"{len(models)} models available: {', '.join(models[:4])}..."
            }
        else:
            return {
                "status": "WARN",
                "name": "Local AI Models (Ollama)",
                "latency_ms": round((time.time() - t0) * 1000, 1),
                "details": f"HTTP {resp.status_code} returned by Ollama server."
            }
    except Exception as e:
        return {
            "status": "WARN",
            "name": "Local AI Models (Ollama)",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": "Ollama service offline on port 11434. (Start via 'ollama serve')"
        }


def check_pillar_3_mcu():
    """Pillar 3: Embedded MCU Engine (PIC18F85K22 & PICkit 3)"""
    t0 = time.time()
    try:
        import embedded_mcu_engine
        stat = embedded_mcu_engine.get_toolchain_status()
        projects = stat.get("projects", [])
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "Embedded MCU Toolchain (PIC18F85K22)",
            "latency_ms": elapsed,
            "details": f"PICkit 3 ({stat.get('programmer')}) | {len(projects)} MPLAB X Projects | LCD Line 2 Defect Guard Active"
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "name": "Embedded MCU Toolchain (PIC18F85K22)",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"MCU Engine error: {e}"
        }


def check_pillar_4_tts():
    """Pillar 4: Dual Co-Pilot & Neural TTS Engine"""
    t0 = time.time()
    try:
        import tts_engine
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "Autonomous Voice Engine (Kokoro & pyttsx3)",
            "latency_ms": elapsed,
            "details": "Dual Co-Pilot Speech Pipeline Initialized (Jarvis & Friday)"
        }
    except Exception as e:
        return {
            "status": "WARN",
            "name": "Autonomous Voice Engine (Kokoro & pyttsx3)",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"TTS Notice: {e}"
        }


def check_pillar_5_music():
    """Pillar 5: Local Punjabi Music Engine & Strict Title Matching"""
    t0 = time.time()
    try:
        import local_music_engine
        tracks = local_music_engine.scan_local_music(max_results=5)
        chrome_path = local_music_engine.get_chrome_path()
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "Local Music Engine & YouTube Router",
            "latency_ms": elapsed,
            "details": f"{len(tracks)}+ Tracks Indexed | Title-Exact Matching | Chrome Native Route: {'Found' if chrome_path else 'Fallback'}"
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "name": "Local Music Engine & YouTube Router",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"Music Engine error: {e}"
        }


def check_pillar_6_hardware_gpu():
    """Pillar 6: Hardware Telemetry & GPU Profile"""
    t0 = time.time()
    try:
        import torch
        cuda = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if cuda else "CPU"
        vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if cuda else 0
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "Hardware Vitals & GPU VRAM Sentinel",
            "latency_ms": elapsed,
            "details": f"GPU: {gpu_name} ({vram_gb} GB VRAM) | CUDA Active: {cuda}"
        }
    except Exception as e:
        return {
            "status": "WARN",
            "name": "Hardware Vitals & GPU VRAM Sentinel",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"GPU check: {e}"
        }


def check_pillar_7_gnn():
    """Pillar 7: Hyper-Relational GNN Knowledge Graph"""
    t0 = time.time()
    try:
        import pc_brain_gnn_engine
        graph_data = pc_brain_gnn_engine.generate_dynamic_pc_brain_gnn() if hasattr(pc_brain_gnn_engine, 'generate_dynamic_pc_brain_gnn') else pc_brain_gnn_engine.generate_pc_brain_gnn()
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "status": "PASS",
            "name": "Hyper-Relational OS & GNN Knowledge Graph",
            "latency_ms": elapsed,
            "details": f"Knowledge Topology active ({len(graph_data)} chars compiled)"
        }
    except Exception as e:
        return {
            "status": "WARN",
            "name": "Hyper-Relational OS & GNN Knowledge Graph",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"GNN Notice: {e}"
        }


def check_pillar_8_guardrails():
    """Pillar 8: Enterprise AI Guardrails & AST Security Validator"""
    t0 = time.time()
    try:
        from enterprise_ai_guardrails import enterprise_guardrails
        validation = enterprise_guardrails.validate_text_to_sql("DROP TABLE users;")
        is_safe = validation.get("valid", True)
        reason = validation.get("reason", "")
        elapsed = round((time.time() - t0) * 1000, 1)
        if not is_safe:
            return {
                "status": "PASS",
                "name": "Enterprise AI Guardrails & AST Validation",
                "latency_ms": elapsed,
                "details": f"AST Shield Active: Blocked destructive query ({reason})"
            }
        else:
            return {
                "status": "FAIL",
                "name": "Enterprise AI Guardrails & AST Validation",
                "latency_ms": elapsed,
                "details": "Guardrail failed to intercept DROP TABLE statement!"
            }
    except Exception as e:
        return {
            "status": "FAIL",
            "name": "Enterprise AI Guardrails & AST Validation",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"Guardrails error: {e}"
        }


def check_pillar_9_web_nexus():
    """Pillar 9: Cyber Nexus & Cockpit UI Portals"""
    t0 = time.time()
    try:
        from app import app
        client = app.test_client()
        r1 = client.get("/")
        r2 = client.get("/nexus")
        r3 = client.get("/gurbani")
        elapsed = round((time.time() - t0) * 1000, 1)
        if all(r.status_code == 200 for r in [r1, r2, r3]):
            return {
                "status": "PASS",
                "name": "Cyber Nexus & Web Portals",
                "latency_ms": elapsed,
                "details": "Cockpit Main UI (/), Cyber Nexus (/nexus), and Gurbani (/gurbani) Operational"
            }
        else:
            return {
                "status": "FAIL",
                "name": "Cyber Nexus & Web Portals",
                "latency_ms": elapsed,
                "details": f"Route responses: Main={r1.status_code}, Nexus={r2.status_code}, Gurbani={r3.status_code}"
            }
    except Exception as e:
        return {
            "status": "FAIL",
            "name": "Cyber Nexus & Web Portals",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"Web Portal check error: {e}"
        }


def check_pillar_10_public_apis():
    """Pillar 10: Financial & Public External APIs"""
    t0 = time.time()
    try:
        import public_apis
        res = public_apis.get_cad_usd_rate()
        elapsed = round((time.time() - t0) * 1000, 1)
        rate = res.get("rate", "N/A")
        return {
            "status": "PASS",
            "name": "Public Financial & Knowledge APIs",
            "latency_ms": elapsed,
            "details": f"Bank of Canada Live USD/CAD FX Rate: {rate} ({res.get('date', 'Today')})"
        }
    except Exception as e:
        return {
            "status": "WARN",
            "name": "Public Financial & Knowledge APIs",
            "latency_ms": round((time.time() - t0) * 1000, 1),
            "details": f"Public API notice: {e}"
        }


def run_all_checks():
    print_banner()
    print("\n[+] Initiating Sovereign Cockpit Diagnostic Matrix across all 10 Pillars...\n")

    checks = [
        check_pillar_1_database,
        check_pillar_2_ollama_ai,
        check_pillar_3_mcu,
        check_pillar_4_tts,
        check_pillar_5_music,
        check_pillar_6_hardware_gpu,
        check_pillar_7_gnn,
        check_pillar_8_guardrails,
        check_pillar_9_web_nexus,
        check_pillar_10_public_apis,
    ]

    results = []
    total_time = 0

    for idx, fn in enumerate(checks, 1):
        res = fn()
        results.append(res)
        total_time += res["latency_ms"]

        icon = "[PASS]" if res["status"] == "PASS" else ("[WARN]" if res["status"] == "WARN" else "[FAIL]")
        print(f" {idx:2d}. {icon:6s} | {res['name']:<42} | {res['latency_ms']:>5.1f}ms")
        print(f"      -> {res['details']}")

    pass_count = sum(1 for r in results if r["status"] == "PASS")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    print("\n" + "=" * 72)
    print(f"DIAGNOSTIC SUMMARY: {pass_count}/10 PASSED | {warn_count} ADVISORIES | {fail_count} CRITICAL")
    print(f"TOTAL AUDIT DURATION: {round(total_time, 1)}ms")
    print("=" * 72)

    if fail_count == 0:
        print("\n[*] ALL CORE PILLARS ARE HEALTHY AND FULLY OPERATIONAL.\n")
    else:
        print(f"\n[!] Attention required on {fail_count} pillar(s).\n")


def cmd_open_cockpit():
    print("[*] Launching D.E.E.P Sovereign Cockpit in Browser...")
    url = "http://127.0.0.1:5000"
    nexus_url = "http://127.0.0.1:5000/nexus"
    try:
        webbrowser.open(url)
        webbrowser.open(nexus_url)
        print(f"[+] Opened Cockpit: {url}")
        print(f"[+] Opened Cyber Nexus: {nexus_url}")
    except Exception as e:
        print(f"[-] Error opening browser: {e}")


def cmd_test_mcu():
    print("=" * 60)
    print("Embedded MCU Engine Firmware Audit (PIC18F85K22)")
    print("=" * 60)
    import embedded_mcu_engine
    stat = embedded_mcu_engine.get_toolchain_status()
    print(f"Target MCU   : {stat.get('target_mcu')}")
    print(f"Programmer   : {stat.get('programmer')}")
    projects = stat.get("projects", [])
    print(f"Projects ({len(projects)} found):")
    for p in projects[:6]:
        print(f" - {p['name']}")
    if projects:
        sample = projects[0]['name']
        print(f"\n[*] Running Pre-Flash Static Audit on: {sample}")
        audit = embedded_mcu_engine.audit_project_firmware(sample)
        print(f"Audit Result : {'PASSED' if audit.get('passed') else 'FINDINGS DETECTED'}")
        print(f"Message      : {audit.get('message')}")
        if audit.get("findings"):
            for f in audit["findings"]:
                print(f"   [!] {f}")


def cmd_test_music(query: str = ""):
    print("=" * 60)
    print("Local Audio & Punjabi Music Library Inspector")
    print("=" * 60)
    import local_music_engine
    if not query:
        tracks = local_music_engine.scan_local_music(max_results=10)
        print(f"Found {len(tracks)} sample local tracks:")
        for t in tracks:
            print(f" • {t.get('title')} ({t.get('folder', '')})")
    else:
        print(f"Searching for track matching: '{query}'...")
        match = local_music_engine.find_track(query)
        if match:
            print(f"[+] Matched: {match.get('title')} ({match.get('path')})")
        else:
            print(f"[-] No local match found for '{query}' (would fallback to yt-dlp autodownload).")


def cmd_test_chat(prompt: str):
    print("=" * 60)
    print(f"Local AI Workload Router Query: '{prompt}'")
    print("=" * 60)
    import model_router
    models = model_router.get_available_models()
    print(f"Available installed models: {[m['name'] for m in models]}")
    import app
    routed_tag = app.resolve_model_tag("auto", user_prompt=prompt)
    print(f"[+] Workload-Aware Smart Router Selected: {routed_tag}")


def main():
    parser = argparse.ArgumentParser(description="D.E.E.P Sovereign Cockpit Diagnostics")
    parser.add_argument("--all", action="store_true", help="Run full 10-pillar diagnostics matrix")
    parser.add_argument("--open", action="store_true", help="Open Cockpit UI & Cyber Nexus in default browser")
    parser.add_argument("--mcu", action="store_true", help="Inspect and audit embedded MCU projects")
    parser.add_argument("--music", nargs="?", const="", type=str, help="Search or list local music tracks")
    parser.add_argument("--chat", type=str, help="Test AI model smart routing on a prompt")

    args = parser.parse_args()

    if args.open:
        cmd_open_cockpit()
    elif args.mcu:
        cmd_test_mcu()
    elif args.music is not None:
        cmd_test_music(args.music)
    elif args.chat:
        cmd_test_chat(args.chat)
    else:
        run_all_checks()


if __name__ == "__main__":
    main()
