"""
Workspace Arranger for Antigravity Local AI PC Cockpit
Native Windows window management: snap left, snap right, maximize, tile coding layout.
"""

import ctypes
import time
from typing import Any, Dict

user32 = ctypes.windll.user32

VK_LWIN = 0x5B
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_UP = 0x26
VK_DOWN = 0x28
VK_D = 0x44
KEYEVENTF_KEYUP = 0x0002


def _send_win_combo(vk_key: int):
    user32.keybd_event(VK_LWIN, 0, 0, 0)
    user32.keybd_event(vk_key, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_key, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)


def snap_left() -> Dict[str, Any]:
    """Snaps the currently focused window to the left 50% of the screen."""
    _send_win_combo(VK_LEFT)
    return {
        "status": "success",
        "action": "snap_left",
        "message": "Snapped active window to the left half.",
    }


def snap_right() -> Dict[str, Any]:
    """Snaps the currently focused window to the right 50% of the screen."""
    _send_win_combo(VK_RIGHT)
    return {
        "status": "success",
        "action": "snap_right",
        "message": "Snapped active window to the right half.",
    }


def maximize_window() -> Dict[str, Any]:
    """Maximizes the currently focused window."""
    _send_win_combo(VK_UP)
    return {
        "status": "success",
        "action": "maximize",
        "message": "Maximized active window.",
    }


def restore_or_minimize() -> Dict[str, Any]:
    """Restores down or minimizes the active window."""
    _send_win_combo(VK_DOWN)
    return {
        "status": "success",
        "action": "minimize_window",
        "message": "Restored or minimized active window.",
    }


def show_desktop() -> Dict[str, Any]:
    """Toggles desktop view (minimizes/restores all windows)."""
    _send_win_combo(VK_D)
    return {
        "status": "success",
        "action": "show_desktop",
        "message": "Toggled desktop display.",
    }


def arrange_coding_layout() -> Dict[str, Any]:
    """
    Arranges the workstation for coding:
    Snaps active window to left, and suggests tiling browser on right.
    """
    _send_win_combo(VK_LEFT)
    return {
        "status": "success",
        "action": "coding_layout",
        "message": "Workspace arranged: Active editor snapped to Left (50%). Ready for split-screen workflow.",
    }


def move_deep_to_screen(screen_index: int) -> Dict[str, Any]:
    """Moves the Deep 3D AI Workstation window to the specified physical monitor."""
    try:
        import win32api
        import win32con
        import win32gui
    except ImportError:
        return {
            "status": "error",
            "message": "pywin32 library is required for multi-monitor management.",
        }

    # screen_index is 1-based (1 for screen 1, 2 for screen 2, etc.)
    monitors = win32api.EnumDisplayMonitors()
    if screen_index < 1 or screen_index > len(monitors):
        return {
            "status": "error",
            "message": f"Screen {screen_index} not found. Only {len(monitors)} screens available.",
        }

    # Get monitor info
    monitor_info = win32api.GetMonitorInfo(monitors[screen_index - 1][0])
    work_area = monitor_info["Work"]  # (left, top, right, bottom)

    # Find the target window
    target_hwnd = None

    def enum_windows_proc(hwnd, lParam):
        nonlocal target_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if (
                "3D AI Workstation Cockpit" in title
                or "Deep - 3D AI" in title
                or "D.E.E.P" in title
            ):
                target_hwnd = hwnd
                return False  # Stop enumeration
        return True

    try:
        win32gui.EnumWindows(enum_windows_proc, 0)
    except Exception:
        pass

    if not target_hwnd:
        return {
            "status": "error",
            "message": "Could not find the Deep AI 3D Workstation window.",
        }

    # Get current window rect to keep its size, just move it
    rect = win32gui.GetWindowRect(target_hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    # Place it at the bottom right corner of the target monitor's work area
    x = work_area[2] - w - 20
    y = work_area[3] - h - 20

    # Ensure it's not off-screen left/top
    x = max(x, work_area[0])
    y = max(y, work_area[1])

    # Move window
    win32gui.SetWindowPos(
        target_hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOZORDER
    )
    win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)

    return {
        "status": "success",
        "action": "move_to_screen",
        "screen": screen_index,
        "message": f"Moved 3D Buddy to Screen {screen_index}.",
    }
