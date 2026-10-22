import numpy as np

# Authorized profile baseline (mocked for Commander Singh)
AUTHORIZED_DWELL_MEAN = 105.0 # ms
AUTHORIZED_FLIGHT_MEAN = 150.0 # ms

def authenticate_keystrokes(dwell_times, flight_times):
    print("[Biometrics] Analyzing passive keystroke rhythm dynamics...")
    if not dwell_times or not flight_times:
        return {"status": "error", "message": "No keystroke data provided."}
        
    avg_dwell = np.mean(dwell_times)
    avg_flight = np.mean(flight_times)
    
    # 20% tolerance
    dwell_match = abs(avg_dwell - AUTHORIZED_DWELL_MEAN) / AUTHORIZED_DWELL_MEAN < 0.20
    flight_match = abs(avg_flight - AUTHORIZED_FLIGHT_MEAN) / AUTHORIZED_FLIGHT_MEAN < 0.20
    
    is_authorized = dwell_match and flight_match
    
    if not is_authorized:
        print("[Biometrics] Intruder detected! Initiating Cockpit Lock.")
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        except:
            pass
            
    return {
        "status": "success",
        "is_authorized": bool(is_authorized),
        "avg_dwell": float(avg_dwell),
        "avg_flight": float(avg_flight)
    }
