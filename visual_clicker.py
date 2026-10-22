"""
Visual UI Auto-Clicker ("Click by Vision") for Antigravity Local AI PC Cockpit
Uses local Qwen 2.5-VL to locate visual UI elements and autonomously click them on screen.
"""

import ctypes
import json
import re
import time
from typing import Any, Dict

import requests

user32 = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

OLLAMA_API_BASE = "http://localhost:11434"


def click_screen_coordinate(x: int, y: int, clicks: int = 1) -> Dict[str, Any]:
    """Moves mouse to (x, y) and performs a native left click."""
    try:
        user32.SetCursorPos(x, y)
        time.sleep(0.05)
        for _ in range(clicks):
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            time.sleep(0.04)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            if clicks > 1:
                time.sleep(0.08)
        return {
            "status": "success",
            "x": x,
            "y": y,
            "message": f"Clicked at screen coordinate ({x}, {y}).",
        }
    except Exception as e:
        return {"status": "error", "message": f"Mouse click failed: {e}"}


def locate_and_click(target_element: str) -> Dict[str, Any]:
    """
    Captures live desktop, uses local Qwen 2.5-VL to find coordinates of target_element,
    and autonomously clicks it!
    """
    target = target_element.strip()
    if not target:
        return {"status": "error", "message": "No target element specified."}

    # Fast-path for screen regions
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)

    t_low = target.lower()
    if t_low in ["center", "screen center", "middle of screen"]:
        return click_screen_coordinate(screen_w // 2, screen_h // 2)
    elif t_low in ["top left", "top left corner"]:
        return click_screen_coordinate(100, 100)
    elif t_low in ["top right", "top right corner"]:
        return click_screen_coordinate(screen_w - 100, 100)
    elif t_low in ["bottom center"]:
        return click_screen_coordinate(screen_w // 2, screen_h - 100)

    # Capture live desktop
    try:
        import screen_vision

        _, b64_img, _ = screen_vision.capture_active_desktop(max_dim=1280)
    except Exception as e:
        import PIL.ImageGrab
        import base64
        from io import BytesIO

        try:
            img = PIL.ImageGrab.grab()
            img.thumbnail((1280, 1280))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            b64_img = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e2:
            return {"status": "error", "message": f"Screen capture failed: {e} and {e2}"}

    prompt = (
        f"Find the visual element '{target}' on the user's screen. "
        "Return ONLY a JSON object with the estimated center position in percentage of screen width and height (from 0 to 100): "
        '{"x_pct": float, "y_pct": float, "label": "description"}'
    )

    try:
        res = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": "qwen2.5vl:7b",
                "prompt": prompt,
                "images": [b64_img],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 120},
            },
            timeout=30,
        )
        if res.status_code == 200:
            text = res.json().get("response", "")
            # Look for JSON in response
            m_json = re.search(r'\{[^{}]*"x_pct"[^{}]*\}', text)
            if m_json:
                coords = json.loads(m_json.group(0))
                x_pct = float(coords.get("x_pct", 50))
                y_pct = float(coords.get("y_pct", 50))
                actual_x = int((x_pct / 100.0) * screen_w)
                actual_y = int((y_pct / 100.0) * screen_h)
                click_res = click_screen_coordinate(actual_x, actual_y)
                click_res["element"] = target
                click_res["message"] = (
                    f"Visual Auto-Clicker located '{target}' at ({actual_x}, {actual_y}) and executed click."
                )
                return click_res
            else:
                return {
                    "status": "not_found",
                    "message": f"Could not pinpoint exact visual coordinates for '{target}'.",
                }
    except Exception as e:
        return {"status": "error", "message": f"Vision element lookup failed: {e}"}

    return {"status": "error", "message": f"Could not find element '{target}'."}
