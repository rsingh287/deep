from multiprocessing import shared_memory
import numpy as np

def init_shared_buffer(name="deep_vision_buffer", size=1024*1024*20): # 20MB buffer
    print(f"[ZeroCopyRingBuffer] Initializing shared physical RAM buffer '{name}' ({size} bytes)...")
    try:
        shm = shared_memory.SharedMemory(create=True, name=name, size=size)
        return {"status": "success", "name": name, "size": size}
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=name)
        return {"status": "success", "name": name, "size": shm.size, "message": "Already exists, attached."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cleanup_shared_buffer(name="deep_vision_buffer"):
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.close()
        shm.unlink()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
