import ctypes
import ctypes.wintypes
import psutil
import time

# Definitions for Windows API
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100

def deflate_memory():
    """
    Scans all running processes and attempts to flush their working sets 
    into the paging pool using EmptyWorkingSet.
    Returns the amount of memory freed in bytes.
    """
    print("[KernelDeflator] Initiating Windows Kernel Memory Deflation...")
    psapi = ctypes.WinDLL('psapi.dll')
    kernel32 = ctypes.WinDLL('kernel32.dll')

    initial_memory = psutil.virtual_memory().used
    cleared_count = 0
    failed_count = 0

    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            pid = proc.info['pid']
            if pid <= 4:
                continue

            # Open process with PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA
            h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
            if h_process:
                result = psapi.EmptyWorkingSet(h_process)
                if result:
                    cleared_count += 1
                else:
                    failed_count += 1
                kernel32.CloseHandle(h_process)
            else:
                failed_count += 1
        except Exception:
            failed_count += 1

    time.sleep(1) # Allow memory to settle
    final_memory = psutil.virtual_memory().used
    freed_memory = initial_memory - final_memory

    print(f"[KernelDeflator] Deflation complete. Processes cleared: {cleared_count}. Freed: {max(0, freed_memory) / (1024**2):.2f} MB")
    
    return {
        "status": "success",
        "freed_bytes": max(0, freed_memory),
        "processes_cleared": cleared_count
    }

if __name__ == '__main__':
    deflate_memory()
