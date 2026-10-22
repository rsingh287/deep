import os
import hashlib

def reclaim_cache(target_dir):
    print(f"[CacheReclaimer] Scanning {target_dir} for duplicates and orphaned caches...")
    if not os.path.exists(target_dir):
        return {"status": "error", "message": "Directory not found."}
        
    freed_bytes = 0
    hashes = {}
    duplicates_removed = 0
    caches_removed = 0
    
    for root, dirs, files in os.walk(target_dir):
        # Remove caches (simulated for safety, would use shutil.rmtree in prod)
        if "node_modules" in dirs:
            caches_removed += 1
        if "__pycache__" in dirs:
            caches_removed += 1
            
        for file in files:
            filepath = os.path.join(root, file)
            try:
                # Basic duplicate finder
                if os.path.getsize(filepath) > 1024 * 1024 * 10: # >10MB
                    with open(filepath, 'rb') as f:
                        filehash = hashlib.sha256(f.read(4096)).hexdigest()
                    if filehash in hashes:
                        # Found duplicate
                        freed_bytes += os.path.getsize(filepath)
                        duplicates_removed += 1
                    else:
                        hashes[filehash] = filepath
            except:
                pass
                
    return {
        "status": "success",
        "potential_freed_mb": freed_bytes / (1024*1024),
        "duplicates_found": duplicates_removed,
        "caches_identified": caches_removed
    }
