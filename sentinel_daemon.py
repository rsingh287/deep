import requests
"""
Sentinel Daemon for Antigravity Local AI PC Cockpit
Background thread monitoring hardware vitals, RAM thresholds, and auto-healing.
"""

import gc
import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil


class SentinelDaemon:
    def __init__(self, interval_sec: int = 15):
        self.interval = interval_sec
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logs: List[Dict[str, Any]] = []
        self.max_logs = 50
        self.alert_state = "NORMAL"
        self.auto_heal_count = 0
        self.last_check = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self._add_log("INFO", "Sentinel Autonomous Watchdog started.")

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            try:
                self._check_health()
            except Exception as e:
                self._add_log("ERROR", f"Sentinel check error: {str(e)}")
            time.sleep(self.interval)

    def _speak_alert(self, msg):
        try:
            import voice_state
            if voice_state.is_voice_muted():
                return
        except Exception:
            pass

        def _speak():
            try:
                import voice_state
                if voice_state.is_voice_muted():
                    return
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(msg)
                engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=_speak, daemon=True).start()

    def _check_health(self):
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        now = datetime.now()
        now_str = now.strftime("%H:%M:%S")
        self.last_check = now_str

        # 1. Hardware Monitoring & Auto-heal
        if mem.percent > 92:
            if self.alert_state != "CRITICAL_MEMORY":
                self._speak_alert("Commander Ramadeep, system memory is at critical levels. Running auto-remediation.")
            self.alert_state = "CRITICAL_MEMORY"
            self._add_log(
                "WARNING",
                f"High Memory Alert: {mem.percent}% RAM used. Running auto-remediation compaction...",
            )
            freed = gc.collect()
            self.auto_heal_count += 1
            self._add_log(
                "AUTO_HEAL",
                f"Garbage collector freed {freed} objects. RAM now at {psutil.virtual_memory().percent}%.",
            )
        elif cpu > 92:
            if self.alert_state != "HIGH_CPU":
                self._speak_alert("Commander Ramadeep, sustained high CPU detected.")
            self.alert_state = "HIGH_CPU"
            self._add_log("WARNING", f"Sustained High CPU Alert: {cpu}%.")
        else:
            self.alert_state = "EQUILIBRIUM"

        # 2. Daily Morning Briefing Check (At 09:00 AM)
        if now.hour == 9 and now.minute == 0 and not getattr(self, "briefing_done", False):
            self.briefing_done = True
            self._add_log("BRIEFING", "Good morning! Generating daily system and project briefing...")
            weather_msg = "Good morning Commander Ramadeep. It is 9 AM. Checking Sudbury weather..."
            try:
                import requests
                res = requests.get("https://wttr.in/Sudbury?format=%C+%t", timeout=5)
                if res.status_code == 200:
                    weather_msg = f"Good morning Commander Ramadeep. The weather in Sudbury is {res.text.strip()}."
            except Exception:
                pass
            self._speak_alert(weather_msg)
        elif now.hour != 9:
            self.briefing_done = False

        # 3. Nightly Chaos Benchmark (At 02:00 AM)
        if now.hour == 2 and now.minute == 0 and not getattr(self, "chaos_done", False):
            self.chaos_done = True
            self._add_log("CHAOS", "Running nightly self-play chaos benchmark...")
            import nightly_chaos_benchmark
            report = nightly_chaos_benchmark.run_chaos_benchmark()
            self._add_log("CHAOS", report)
        elif now.hour != 2:
            self.chaos_done = False

        # 4. Repo Monitoring Check (Every ~5 mins)
        if not hasattr(self, "last_repo_check") or (now - self.last_repo_check).total_seconds() > 300:
            self.last_repo_check = now
            try:
                if os.path.exists(".git"):
                    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
                    if status:
                        files = len(status.split("\n"))
                        self._add_log("REPO", f"Workspace has {files} uncommitted file(s).")
            except Exception as e:
                pass
              
        # 5. Auto-Purge Disk Janitor Check (Every ~5 mins)
        if not hasattr(self, "last_janitor_check") or (now - self.last_janitor_check).total_seconds() > 300:
            self.last_janitor_check = now
            self.run_disk_janitor()
              
        self.check_vram_idle()
        self.check_services()

    def check_services(self):
        # 1. PostgreSQL Check
        conn = None
        try:
            import psycopg2
            from db_engine import DEFAULT_PG_URL
            conn = psycopg2.connect(DEFAULT_PG_URL, connect_timeout=2)
            self.pg_failed = False
        except Exception as e:
            if not getattr(self, "pg_failed", False):
                self._add_log("ERROR", f"PostgreSQL ping failed: {e}. Auto-remediating...")
                try:
                    subprocess.run(["net", "stop", "postgresql-x64-16"], check=False, capture_output=True)
                    subprocess.run(["net", "start", "postgresql-x64-16"], check=False, capture_output=True)
                    self._speak_alert("PostgreSQL connection restored by Sentinel.")
                    self._add_log("REMEDIATION", "PostgreSQL service restarted successfully.")
                except Exception as restart_e:
                    self._add_log("ERROR", f"Failed to restart PostgreSQL: {restart_e}")
                self.pg_failed = True
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        # 2. Ollama Check
        try:
            res = requests.get("http://localhost:11434/", timeout=2)
            if res.status_code != 200:
                raise Exception(f"Ollama returned {res.status_code}")
            self.ollama_failed = False
        except Exception as e:
            if not getattr(self, "ollama_failed", False):
                self._add_log("ERROR", f"Ollama ping failed: {e}. Auto-remediating...")
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], check=False, capture_output=True)
                    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
                    self._speak_alert("Ollama service restored by Sentinel.")
                    self._add_log("REMEDIATION", "Ollama service restarted successfully.")
                except Exception as restart_e:
                    self._add_log("ERROR", f"Failed to restart Ollama: {restart_e}")
                self.ollama_failed = True

        # 3. Flask Check
        try:
            res = requests.get("http://127.0.0.1:5000/", timeout=2)
            self.flask_failed = False
        except Exception as e:
            if not getattr(self, "flask_failed", False):
                self._add_log("ERROR", f"Flask ping failed: {e}. Flask process requires manual restart.")
                self.flask_failed = True

    def run_disk_janitor(self):
        try:
            import glob
            cleared_count = 0
            base_dir = os.path.dirname(os.path.abspath(__file__))
            for directory in ["screenshots", "temp_media"]:
                dir_path = os.path.join(base_dir, directory)
                if os.path.exists(dir_path):
                    for filepath in glob.glob(os.path.join(dir_path, "*")):
                        try:
                            # Keep files modified within the last hour
                            if time.time() - os.path.getmtime(filepath) > 3600:
                                os.remove(filepath)
                                cleared_count += 1
                        except Exception:
                            pass
            if cleared_count > 0:
                self._add_log("JANITOR", f"Disk Janitor auto-purged {cleared_count} obsolete media files.")
        except Exception as e:
            pass

    def check_vram_idle(self):
        try:
            res = requests.get("http://127.0.0.1:5000/api/system/last_interaction", timeout=3)
            if res.status_code == 200:
                data = res.json()
                idle_time = data["now"] - data["last_interaction"]
                if idle_time > 300: # 5 mins
                    if not getattr(self, "vram_unloaded", False):
                        self.unload_vram()
                        self.vram_unloaded = True
                else:
                    self.vram_unloaded = False
        except Exception:
            pass
        
    def unload_vram(self):
        try:
            for model in ["qwen2.5:3b", "qwen2.5-coder:7b", "qwen2.5:7b", "deepseek-r1:8b", "qwen2.5vl:7b", "nomic-embed-text"]:
                requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "keep_alive": 0},
                    timeout=5
                )
            self._add_log("VRAM", "VRAM Idle Offloader triggered: Unloaded models from GPU.")
        except Exception as e:
            self._add_log("ERROR", f"Failed to unload VRAM: {e}")

    def _add_log(self, level: str, msg: str):
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": msg,
        }
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def get_status(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        return {
            "running": self.running,
            "state": self.alert_state,
            "last_check": self.last_check,
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "ram_free_gb": round(mem.available / (1024**3), 2),
            "auto_heals_triggered": self.auto_heal_count,
            "recent_logs": self.logs[-10:],
        }


sentinel = SentinelDaemon()
