import winreg

def list_startup_items():
    print("[StartupOptimizer] Scanning Windows Registry for startup bloat...")
    items = []
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        for i in range(1000):
            try:
                name, value, _ = winreg.EnumValue(key, i)
                items.append({"name": name, "value": value, "hive": "HKCU"})
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
        
    return {"status": "success", "startup_items": items}

def optimize_startup():
    print("[StartupOptimizer] Disabling known non-essential third-party startup updaters...")
    blacklist = ["BingWallpaperDaemon", "Logi Download Assistant", "OneDriveSetup", "Discord", "Steam"]
    disabled = []
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        for i in range(1000):
            try:
                name, value, _ = winreg.EnumValue(key, i)
                for bl in blacklist:
                    if bl.lower() in name.lower() or bl.lower() in value.lower():
                        winreg.DeleteValue(key, name)
                        disabled.append(name)
                        break
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass
        
    return {"status": "success", "disabled_items": disabled}
