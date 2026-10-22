"""
Desktop Pilot Engine for Antigravity Local AI PC Cockpit (Jarvis Tier - Phase 3)
Provides hands-free Windows automation: app launching, volume control, and window actions.
"""

import ctypes
import subprocess
import time
from typing import Any, Dict

user32 = ctypes.windll.user32

# Virtual key codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_LWIN = 0x5B
VK_D = 0x44
KEYEVENTF_KEYUP = 0x0002

SAFE_APPS = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "code": "code",
    "vscode": "code",
    "explorer": "explorer.exe",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "paint": "mspaint.exe",
    "taskmgr": "taskmgr.exe",
}


def _press_key(vk_code: int):
    user32.keybd_event(vk_code, 0, 0, 0)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def adjust_volume(action: str = "up", steps: int = 2) -> Dict[str, Any]:
    """Adjust master Windows audio volume."""
    action = action.lower().strip()
    try:
        if "mute" in action:
            _press_key(VK_VOLUME_MUTE)
            return {
                "status": "success",
                "action": "mute",
                "message": "Master audio volume toggled mute.",
            }
        elif "down" in action or "lower" in action or "decrease" in action:
            for _ in range(steps):
                _press_key(VK_VOLUME_DOWN)
                time.sleep(0.04)
            return {
                "status": "success",
                "action": "down",
                "steps": steps,
                "message": f"Volume lowered by {steps * 2}%.",
            }
        else:
            for _ in range(steps):
                _press_key(VK_VOLUME_UP)
                time.sleep(0.04)
            return {
                "status": "success",
                "action": "up",
                "steps": steps,
                "message": f"Volume raised by {steps * 2}%.",
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def toggle_show_desktop() -> Dict[str, Any]:
    """Toggles minimize all / show desktop (Win + D)."""
    try:
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        user32.keybd_event(VK_D, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_D, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
        return {"status": "success", "message": "Toggled desktop / window view."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def launch_application(app_name: str) -> Dict[str, Any]:
    """Launches an approved application from the safe whitelist."""
    app_key = app_name.lower().strip()
    target_exe = None
    for k, v in SAFE_APPS.items():
        if k in app_key:
            target_exe = v
            break

    if not target_exe:
        return {
            "status": "blocked",
            "message": f"Security Guardrail: '{app_name}' is not in the approved safe desktop application whitelist.",
        }

    try:
        # Launch non-blocking
        subprocess.Popen(target_exe, shell=True)
        return {
            "status": "success",
            "app": target_exe,
            "message": f"Launched {target_exe} successfully.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
