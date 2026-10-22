import psutil

def toggle_acoustic_silence(enable_silence=True):
    print(f"[AcousticOrchestrator] Toggling dynamic fan silence: {enable_silence}")
    try:
        # Lower the priority of heavy processes
        target_processes = ["python", "chrome", "msedge", "electron", "node"]
        adjusted_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                is_heavy = any(t in name for t in target_processes)
                if is_heavy:
                    p = psutil.Process(proc.info['pid'])
                    if enable_silence:
                        # Set to IDLE priority to quiet fans
                        p.nice(psutil.IDLE_PRIORITY_CLASS)
                    else:
                        # Restore to NORMAL priority
                        p.nice(psutil.NORMAL_PRIORITY_CLASS)
                    adjusted_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return {
            "status": "success",
            "adjusted_processes": adjusted_count,
            "mode": "Whisper-Silent Voice Priority" if enable_silence else "Full Clock Speed Computing"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
