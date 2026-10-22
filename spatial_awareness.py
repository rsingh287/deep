import ctypes
from ctypes import wintypes
import time

def get_spatial_context():
    print("[SpatialAwareness] Enumerating multi-window spatial arrangement...")
    
    windows = []
    
    # Use native ctypes to iterate top-level windows
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
    GetWindowRect = ctypes.windll.user32.GetWindowRect
    
    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                title = buff.value
                
                # Filter out basic overlay/hidden windows
                if title and "Program Manager" not in title:
                    rect = wintypes.RECT()
                    GetWindowRect(hwnd, ctypes.byref(rect))
                    
                    windows.append({
                        "title": title,
                        "rect": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom
                        }
                    })
        return True
        
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    
    # Determine relationships based on screen coordinates (e.g., left vs right)
    analysis = "Spatial arrangement captured. "
    if len(windows) > 1:
        analysis += f"Detected {len(windows)} visible application windows across the spatial matrix."
        
    return {
        "status": "success",
        "visible_windows": windows,
        "spatial_analysis": analysis,
        "message": "Sol/Luna contextual spatial map updated."
    }
