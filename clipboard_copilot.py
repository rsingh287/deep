"""
Smart Clipboard Copilot for Antigravity Local AI PC Cockpit
Inspects, formats, and auto-fixes code and stack traces stored on the Windows clipboard.
"""

import json
import re
from typing import Any, Dict

import requests

try:
    import win32clipboard
    import win32con

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

OLLAMA_API_BASE = "http://localhost:11434"


def get_clipboard_text() -> str:
    """Reads raw text from the Windows clipboard."""
    if not HAS_WIN32:
        return ""
    try:
        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data or ""
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        pass
    return ""


def set_clipboard_text(text: str) -> bool:
    """Sets text on the Windows clipboard."""
    if not HAS_WIN32:
        return False
    try:
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            return True
        finally:
            win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"[ClipboardCopilot] Write error: {e}")
    return False


def analyze_clipboard() -> Dict[str, Any]:
    """Inspects clipboard contents and identifies content type."""
    raw = get_clipboard_text().strip()
    if not raw:
        return {
            "status": "empty",
            "message": "Clipboard is empty or contains non-text data.",
        }

    # Detect JSON
    if (raw.startswith("{") and raw.endswith("}")) or (
        raw.startswith("[") and raw.endswith("]")
    ):
        try:
            parsed = json.loads(raw)
            return {
                "status": "success",
                "type": "json",
                "length": len(raw),
                "summary": f"Valid JSON data with {len(parsed) if isinstance(parsed, (dict, list)) else 1} top-level entries.",
                "preview": raw[:200],
            }
        except Exception:
            pass

    # Detect Error / Traceback
    if any(
        k in raw.lower()
        for k in [
            "traceback (most recent call last)",
            "error:",
            "exception:",
            "syntaxerror",
            "typeerror",
            "nullpointerexception",
            "failed with exit code",
        ]
    ):
        return {
            "status": "success",
            "type": "error_traceback",
            "length": len(raw),
            "summary": "Stack trace / Error log detected on clipboard. Say 'fix clipboard' to automatically generate a solution.",
            "preview": raw[:300],
        }

    # Detect Code
    if any(
        k in raw
        for k in [
            "def ",
            "class ",
            "import ",
            "function ",
            "const ",
            "let ",
            "var ",
            "public static",
            "SELECT ",
            "FROM ",
        ]
    ):
        return {
            "status": "success",
            "type": "code",
            "length": len(raw),
            "summary": "Source code detected on clipboard. Say 'fix clipboard' or 'format clipboard' to process.",
            "preview": raw[:200],
        }

    # Plain text summary
    words = len(raw.split())
    return {
        "status": "success",
        "type": "text",
        "length": len(raw),
        "words": words,
        "summary": f"Text content ({words} words, {len(raw)} chars).",
        "preview": raw[:200],
    }


def format_clipboard() -> Dict[str, Any]:
    """Auto-formats JSON or code on clipboard."""
    raw = get_clipboard_text().strip()
    if not raw:
        return {"status": "empty", "message": "Clipboard is empty."}

    # Try format JSON
    try:
        parsed = json.loads(raw)
        formatted = json.dumps(parsed, indent=2)
        set_clipboard_text(formatted)
        return {
            "status": "success",
            "type": "json",
            "message": "JSON on clipboard was formatted with 2-space indentation and copied back to clipboard.",
        }
    except Exception:
        pass

    return {
        "status": "notice",
        "message": "Content on clipboard is not structured JSON.",
    }



import threading
import time

PRECOMPUTED_FIXES = {}

class ClipboardDaemon:
    def __init__(self, interval_sec: float = 4.0):
        self.interval = interval_sec
        self.running = False
        self.thread = None
        self.last_clipboard = ""

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True, name="ClipboardCopilotDaemon")
        self.thread.start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            try:
                current_text = get_clipboard_text().strip()
                if current_text and current_text != self.last_clipboard:
                    self.last_clipboard = current_text
                    # Check if it's an error
                    analysis = analyze_clipboard()
                    if analysis.get("type") == "error_traceback":
                        if current_text not in PRECOMPUTED_FIXES:
                            # Precompute
                            print(f"[ClipboardCopilot] Error detected on clipboard. Pre-computing fix in background...")
                            fix = fix_clipboard_with_ai_logic(current_text)
                            PRECOMPUTED_FIXES[current_text] = fix
            except Exception as e:
                print(f"[ClipboardCopilot] Daemon loop error: {e}")
            time.sleep(self.interval)

clipboard_daemon = ClipboardDaemon()

def fix_clipboard_with_ai_logic(raw_text: str) -> Dict[str, Any]:
    prompt = (
        "You are an expert software engineer. Review the following code or error traceback from the user's clipboard. "
        "Diagnose the issue and provide the corrected, working code. "
        "Keep explanation concise (max 2 sentences) followed by the complete code block.\n\n"
        "```\n" + raw_text[:3000] + "\n```"
    )

    try:
        res = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 400},
            },
            timeout=25,
        )
        if res.status_code == 200:
            ai_text = res.json().get("response", "").strip()

            code_match = re.search(r"```(?:[a-zA-Z0-9_\-]+)?\n([\s\S]*?)```", ai_text)
            if code_match:
                clean_code = code_match.group(1).strip()
                return {
                    "status": "success",
                    "explanation": ai_text[:300],
                    "clean_code": clean_code,
                    "clipboard_updated": True,
                    "message": "Fixed code was copied directly to your clipboard! Ready to paste (Ctrl + V).",
                }
            else:
                return {
                    "status": "success",
                    "explanation": ai_text,
                    "clipboard_updated": False,
                    "message": ai_text,
                }
    except Exception as e:
        return {"status": "error", "message": f"AI repair failed: {e}"}
    return {"status": "error", "message": "Could not generate fix."}


def fix_clipboard_with_ai() -> Dict[str, Any]:
    raw = get_clipboard_text().strip()
    if not raw:
        return {"status": "empty", "message": "Clipboard is empty."}
        
    if raw in PRECOMPUTED_FIXES:
        fix = PRECOMPUTED_FIXES[raw]
        if fix.get("clipboard_updated") and "clean_code" in fix:
            set_clipboard_text(fix["clean_code"])
        fix["message"] = "(Pre-Computed Instantly) " + fix["message"]
        return fix
        
    fix = fix_clipboard_with_ai_logic(raw)
    if fix.get("clipboard_updated") and "clean_code" in fix:
        set_clipboard_text(fix["clean_code"])
    return fix


