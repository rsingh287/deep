"""
Global Voice State Synchronization Engine
Provides centralized, cross-process persistence for AI Voice Mute / Speech status across
the Cockpit Web UI, Windows SAPI, OmniVoice, and Sentinel Daemons.
"""

import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_state.json")

_cached_mtime = 0
_cached_state = False

def is_voice_muted() -> bool:
    """
    Returns True if Deep voice output is muted / turned OFF.
    Thread-safe and cross-process safe with mtime cache.
    """
    global _cached_mtime, _cached_state
    try:
        if os.path.exists(STATE_FILE):
            mtime = os.path.getmtime(STATE_FILE)
            if mtime != _cached_mtime:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    _cached_state = bool(data.get("muted", False))
                _cached_mtime = mtime
            return _cached_state
    except Exception:
        pass
    return _cached_state


def set_voice_muted(muted: bool) -> bool:
    """
    Sets global voice mute state and atomically persists to disk.
    Notifies all local daemons and GUI processes instantly.
    """
    global _cached_mtime, _cached_state
    try:
        muted_bool = bool(muted)
        data = {
            "muted": muted_bool,
            "enabled": not muted_bool,
            "updated_at": time.time()
        }
        temp_file = STATE_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, STATE_FILE)
        _cached_state = muted_bool
        _cached_mtime = os.path.getmtime(STATE_FILE)
        return True
    except Exception as e:
        print(f"[VoiceState] Error persisting state: {e}")
        return False


def is_voice_enabled() -> bool:
    """Returns True if Deep voice replies and broadcasts are active (not muted)."""
    return not is_voice_muted()


def set_voice_enabled(enabled: bool) -> bool:
    """Sets voice enabled state."""
    return set_voice_muted(not enabled)
