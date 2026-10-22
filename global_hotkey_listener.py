"""
Global Desktop Hotkey Listener for Antigravity Local AI PC Cockpit
Native Windows API (user32.RegisterHotKey) background hook.

Hotkeys:
- Alt + Space (Primary Quick Assistant / Spotlight Omnibar)
- Ctrl + Shift + Space (Secondary Omnibar fallback)
- Ctrl + Shift + D (Legacy Desktop Agentic hook)
"""

import ctypes
import ctypes.wintypes
import threading
import time
from typing import Callable, Optional

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

VK_SPACE = 0x20
VK_D = 0x44
VK_J = 0x4A

HOTKEY_ID_ALT_SPACE = 7780
HOTKEY_ID_CTRL_SHIFT_SPACE = 7781
HOTKEY_ID_D = 7788
HOTKEY_ID_J = 7789

user32 = ctypes.windll.user32

class GlobalHotkeyListener:
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        self.last_trigger = 0.0
        self.registered_ids = []

    def start(self, callback: Optional[Callable] = None):
        if self.running:
            return
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(
            target=self._hotkey_loop, daemon=True, name="DeepGlobalHotkeyThread"
        )
        self.thread.start()

    def stop(self):
        self.running = False

    def _hotkey_loop(self):
        self.registered_ids = []

        # 1. Register Alt + Space
        succ_alt_sp = user32.RegisterHotKey(None, HOTKEY_ID_ALT_SPACE, MOD_ALT | MOD_NOREPEAT, VK_SPACE)
        if not succ_alt_sp:
            succ_alt_sp = user32.RegisterHotKey(None, HOTKEY_ID_ALT_SPACE, MOD_ALT, VK_SPACE)
        if succ_alt_sp:
            self.registered_ids.append(HOTKEY_ID_ALT_SPACE)

        # 2. Register Ctrl + Shift + Space
        succ_cs_sp = user32.RegisterHotKey(None, HOTKEY_ID_CTRL_SHIFT_SPACE, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_SPACE)
        if not succ_cs_sp:
            succ_cs_sp = user32.RegisterHotKey(None, HOTKEY_ID_CTRL_SHIFT_SPACE, MOD_CONTROL | MOD_SHIFT, VK_SPACE)
        if succ_cs_sp:
            self.registered_ids.append(HOTKEY_ID_CTRL_SHIFT_SPACE)

        # 3. Register Ctrl + Shift + D
        succ_d = user32.RegisterHotKey(None, HOTKEY_ID_D, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_D)
        if not succ_d:
            succ_d = user32.RegisterHotKey(None, HOTKEY_ID_D, MOD_CONTROL | MOD_SHIFT, VK_D)
        if succ_d:
            self.registered_ids.append(HOTKEY_ID_D)

        print(
            f"[DeepHotkey] Global Hotkeys registered: "
            f"Alt+Space: {bool(succ_alt_sp)}, "
            f"Ctrl+Shift+Space: {bool(succ_cs_sp)}, "
            f"Ctrl+Shift+D: {bool(succ_d)}."
        )

        msg = ctypes.wintypes.MSG()
        while self.running:
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                if msg.message == 0x0312:  # WM_HOTKEY
                    now = time.time()
                    if now - self.last_trigger > 0.35:
                        self.last_trigger = now
                        hk_id = msg.wParam
                        print(f"[DeepHotkey] Triggered (ID: {hk_id})! Toggling Floating AI Omnibar...")
                        try:
                            import omnibar_hud
                            omnibar_hud.toggle_hud()
                        except Exception as e:
                            print(f"[DeepHotkey] Omnibar HUD error: {e}")

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.04)

        for hid in self.registered_ids:
            try:
                user32.UnregisterHotKey(None, hid)
            except Exception:
                pass


def default_deep_hotkey_action():
    """Default fallback action for hotkey."""
    try:
        import omnibar_hud
        omnibar_hud.toggle_hud()
    except Exception as ex:
        print(f"[DeepHotkeyActionError]: {ex}")


default_jarvis_hotkey_action = default_deep_hotkey_action
hotkey_listener = GlobalHotkeyListener()

if __name__ == "__main__":
    print("Testing Global Hotkey Listener for 3 seconds...")
    hotkey_listener.start(default_deep_hotkey_action)
    time.sleep(3)
    hotkey_listener.stop()
    print("Test finished.")
