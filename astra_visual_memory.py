import os
import time
import ctypes
from datetime import datetime
import db_engine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THUMBNAILS_DIR = os.path.join(PROJECT_ROOT, "scratch", "astra_thumbnails")
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


def init_astra_memory_db():
    """Initializes PostgreSQL table for Astra continuous screen & visual memory."""
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS astra_screen_memory (
        id SERIAL PRIMARY KEY,
        captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        window_title TEXT,
        process_name TEXT,
        ocr_text TEXT,
        thumbnail_path TEXT,
        is_starred BOOLEAN DEFAULT FALSE
    );
    """)
    conn.commit()
    conn.close()


def get_active_window_info() -> dict:
    """Ultra-fast Win32 ctypes active window inspection."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value or "Active Desktop"

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pname = "Application"
        try:
            import psutil
            pname = psutil.Process(pid.value).name()
        except Exception:
            pass
        return {"title": title, "process": pname}
    except Exception:
        return {"title": "Active Desktop", "process": "explorer.exe"}


def capture_and_index_screen(extract_ocr: bool = True) -> dict:
    """
    Takes a lightweight compressed snapshot of the active screen,
    indexes active window title, extracts visible text, and stores in PostgreSQL.
    """
    init_astra_memory_db()
    win_info = get_active_window_info()
    timestamp = int(time.time())

    try:
        import screen_vision
        img, _, _ = screen_vision.capture_active_desktop(max_dim=640, quality=60)
        filename = f"thumb_{timestamp}.jpg"
        thumb_path = os.path.join(THUMBNAILS_DIR, filename)
        img.save(thumb_path, format="JPEG", quality=60)
    except Exception as e:
        return {"success": False, "error": f"Screenshot capture notice: {e}"}

    ocr_summary = f"Active application: {win_info['process']} ({win_info['title']})."

    # Optional fast OCR if tesseract / pytesseract is available, otherwise index window context
    try:
        import pytesseract
        text = pytesseract.image_to_string(img)
        if text.strip():
            ocr_summary += " " + text.strip()[:1000]
    except Exception:
        pass

    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO astra_screen_memory (window_title, process_name, ocr_text, thumbnail_path)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """, (win_info["title"], win_info["process"], ocr_summary, thumb_path))
    entry_id = c.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": entry_id,
        "window_title": win_info["title"],
        "process_name": win_info["process"],
        "thumbnail": f"/astra_thumbs/{filename}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def query_visual_memory(query_text: str, limit: int = 5) -> dict:
    """
    Project Astra 'Where did I see that?' visual memory query:
    Searches visual history in PostgreSQL by keyword, process, or window title.
    """
    init_astra_memory_db()
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    c = conn.cursor()

    search_term = f"%{query_text.lower()}%"
    c.execute("""
    SELECT id, captured_at, window_title, process_name, ocr_text, thumbnail_path
    FROM astra_screen_memory
    WHERE LOWER(window_title) LIKE %s 
       OR LOWER(process_name) LIKE %s 
       OR LOWER(ocr_text) LIKE %s
    ORDER BY captured_at DESC
    LIMIT %s;
    """, (search_term, search_term, search_term, limit))
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        thumb_name = os.path.basename(d.get("thumbnail_path", ""))
        d["thumbnail_url"] = f"/astra_thumbs/{thumb_name}" if thumb_name else None
        results.append(d)

    return {
        "success": True,
        "query": query_text,
        "matches_count": len(results),
        "results": results
    }


def get_recent_visual_timeline(limit: int = 8) -> dict:
    """Returns the visual timeline of recent screen states for the Astra HUD visual strip."""
    init_astra_memory_db()
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    c = conn.cursor()
    c.execute("""
    SELECT id, captured_at, window_title, process_name, thumbnail_path
    FROM astra_screen_memory
    ORDER BY captured_at DESC
    LIMIT %s;
    """, (limit,))
    rows = c.fetchall()
    conn.close()

    timeline = []
    for r in rows:
        d = dict(r)
        thumb_name = os.path.basename(d.get("thumbnail_path", ""))
        d["thumbnail_url"] = f"/astra_thumbs/{thumb_name}" if thumb_name else None
        timeline.append(d)

    return {
        "success": True,
        "count": len(timeline),
        "timeline": timeline
    }


if __name__ == "__main__":
    print("Testing Project Astra Continuous Visual Memory...")
    snap = capture_and_index_screen()
    print("Screen Indexed:", snap)
    mem = query_visual_memory("cmd")
    print("Query 'cmd':", mem["matches_count"], "matches found.")
    tl = get_recent_visual_timeline()
    print("Timeline entries:", tl["count"])
