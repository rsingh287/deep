"""
Live Error Watchdog (Autonomous Sentinel) for Antigravity Local AI PC Cockpit
Monitors the user workstation, detects software crashes, unhandled tracebacks,
and terminal errors, and provides instant audio alerts with solutions.
"""

import threading
import time
from typing import Any, Dict, List, Optional

OLLAMA_API_BASE = "http://localhost:11434"


class ErrorWatchdog:
    def __init__(self, check_interval_s: int = 15):
        self.interval = check_interval_s
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.detected_errors: List[Dict[str, Any]] = []
        self.last_checked_time: Optional[float] = None
        self.last_alert_time: float = 0.0

    def start(self) -> Dict[str, Any]:
        if self.is_running:
            return {
                "status": "already_running",
                "message": "Error Watchdog is already actively monitoring.",
            }

        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        return {
            "status": "started",
            "message": "🛡️ Error Watchdog Sentinel active. Monitoring active workstation for bugs, exceptions, and crashes.",
        }

    def stop(self) -> Dict[str, Any]:
        if not self.is_running:
            return {"status": "not_running", "message": "Error Watchdog is idle."}

        self.is_running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        return {"status": "stopped", "message": "Error Watchdog stopped."}

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            try:
                self.check_now()
            except Exception as e:
                print(f"[ErrorWatchdog] Loop error: {e}")
            self._stop_event.wait(self.interval)

    def check_now(self) -> Dict[str, Any]:
        """Runs an on-demand screen error diagnosis."""
        self.last_checked_time = time.time()
        try:
            import screen_vision

            res = screen_vision.analyze_desktop_screen(
                prompt="Check if any error, traceback, or warning is visible on this screen. If yes, state the error and fix in 2 sentences. If everything looks normal, respond: 'NO_ERROR_DETECTED'.",
                model="qwen2.5vl:7b",
                timeout_s=35,
            )
            analysis = res.get("analysis", "")
            if analysis and "NO_ERROR_DETECTED" not in analysis:
                record = {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "details": analysis,
                    "model": res.get("model", "qwen2.5vl:7b"),
                }
                self.detected_errors.append(record)
                if len(self.detected_errors) > 20:
                    self.detected_errors.pop(0)
                return {
                    "has_error": True,
                    "message": analysis,
                    "timestamp": record["timestamp"],
                }
            else:
                return {
                    "has_error": False,
                    "message": "No errors detected on active screen.",
                }
        except Exception as e:
            return {"has_error": False, "message": f"Watchdog check note: {e}"}

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "interval_seconds": self.interval,
            "last_checked": (
                time.strftime("%H:%M:%S", time.localtime(self.last_checked_time))
                if self.last_checked_time
                else "Never"
            ),
            "error_count": len(self.detected_errors),
            "recent_alerts": self.detected_errors[-3:],
        }


_WATCHDOG = ErrorWatchdog()


def start_watchdog() -> Dict[str, Any]:
    return _WATCHDOG.start()


def stop_watchdog() -> Dict[str, Any]:
    return _WATCHDOG.stop()


def check_errors_now() -> Dict[str, Any]:
    return _WATCHDOG.check_now()


def get_watchdog_status() -> Dict[str, Any]:
    return _WATCHDOG.get_status()
