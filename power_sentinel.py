import psutil
import time
import requests
import subprocess
import os
import db_engine

GUI_PORT = 5000

def lock_workstation():
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
    except:
        pass

def save_open_editors():
    print("[PowerSentinel] Saving open editor buffers...")
    try:
        import pyautogui
        # Send a generic Save All (Ctrl+Shift+S or Ctrl+K, S for VSCode)
        # Using simple Ctrl+S for now as a best-effort approach
        pyautogui.hotkey('ctrl', 's')
    except Exception as e:
        print(f"[PowerSentinel] Could not save editors: {e}")

def flush_postgres_wal():
    print("[PowerSentinel] Flushing PostgreSQL WAL transaction logs to disk...")
    try:
        # CHECKPOINT forces a WAL flush to disk in PostgreSQL
        db_engine.execute_query("CHECKPOINT;")
    except Exception as e:
        print(f"[PowerSentinel] Database flush failed: {e}")

def emergency_shutdown():
    print("[PowerSentinel] Emergency shutdown sequence initiated!")
    try:
        requests.post(f"http://127.0.0.1:{GUI_PORT}/api/deep/speak", json={
            "text": "Critical power threshold reached. Executing emergency graceful shutdown protocol. Flushing PostgreSQL WAL and locking workstation."
        }, timeout=2)
    except:
        pass
    
    save_open_editors()
    flush_postgres_wal()
    lock_workstation()

def main():
    print("[PowerSentinel] Initializing AC Power Grid & UPS Disconnection Sentinel...")
    was_plugged = True
    
    while True:
        try:
            battery = psutil.sensors_battery()
            if battery:
                is_plugged = battery.power_plugged
                percent = battery.percent
                secsleft = battery.secsleft
                
                # Check for AC disconnect
                if was_plugged and not is_plugged:
                    mins = "unknown"
                    if secsleft != psutil.POWER_TIME_UNKNOWN:
                        mins = secsleft // 60
                    
                    print("[PowerSentinel] AC Grid Disconnected.")
                    try:
                        requests.post(f"http://127.0.0.1:{GUI_PORT}/api/deep/speak", json={
                            "text": f"Commander, AC grid power disconnected. Running on UPS battery. Estimated runtime: {mins} minutes."
                        }, timeout=2)
                    except:
                        pass
                        
                # Check for critical threshold
                if not is_plugged and percent < 15:
                    emergency_shutdown()
                    time.sleep(300) # prevent spamming
                
                was_plugged = is_plugged
        except Exception as e:
            pass
            
        time.sleep(10)

if __name__ == "__main__":
    main()
