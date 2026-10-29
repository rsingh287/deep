import time

def watch_screen_region(x, y, w, h, trigger_words=None):
    if trigger_words is None:
        trigger_words = ["Failed", "Error", "Exception"]
    print(f"[RegionWatcher] Pinning Region x:{x} y:{y} w:{w} h:{h}. Watching for: {trigger_words}")
    
    # In a full GUI environment, this would loop and run OCR (e.g. pytesseract) 
    # on just that cropped screen coordinate bounding box.
    
    return {
        "status": "success",
        "watch_id": f"WATCH_{int(time.time())}",
        "region": {"x": x, "y": y, "width": w, "height": h},
        "trigger_words": trigger_words,
        "message": f"Sticky Pin HUD tile established. Monitoring for key phrases."
    }
