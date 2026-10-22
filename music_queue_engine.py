"""
Smart Music Queue & Playlist Engine
====================================
Manages an intelligent queue for PC media playback:
- "Play <song> next" -> Inserts track at the top of the queue.
- "Queue <song>" / "Add <song> to queue" -> Appends track to the queue.
- Adheres strictly to AGENTS.md:
  1. Checks local library (C:\\Users\\User\\Music) first.
  2. If missing, automatically downloads via yt-dlp to C:\\Users\\User\\Music and enqueues.
  3. Plays through PC Speakers (Realtek) without opening browser.
- Saves queue state to scratch/music_queue.json for persistence across sessions.
"""

import os
import json
import time
import threading
from typing import List, Dict, Any, Optional

import local_music_engine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(PROJECT_ROOT, "scratch", "music_queue.json")
os.makedirs(os.path.join(PROJECT_ROOT, "scratch"), exist_ok=True)


class MusicQueueEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.queue: List[Dict[str, Any]] = []
        self.current_track: Optional[Dict[str, Any]] = None
        self._load_queue()

    def _load_queue(self):
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.queue = data.get("queue", [])
                    self.current_track = data.get("current_track", None)
        except Exception:
            self.queue = []

    def _save_queue(self):
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "queue": self.queue,
                        "current_track": self.current_track,
                        "updated_at": time.time(),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception as e:
            print(f"[MusicQueue] Save queue error: {e}")

    def enqueue(self, query: str, priority: str = "end") -> Dict[str, Any]:
        """
        Resolves query against local library or downloads track, then queues it.
        priority: 'next' (inserted at index 0) or 'end' (appended).
        """
        clean_q = query.strip().rstrip(".?!;")

        # 1. Search Local Library
        track = local_music_engine.find_track(clean_q)
        if track:
            entry = {
                "title": track.get("clean_title") or track.get("title") or clean_q,
                "artist": track.get("artist") or "Local Library",
                "filename": track.get("filename"),
                "path": track.get("path"),
                "source": "local",
                "queued_at": time.time(),
            }
        else:
            # 2. Missing locally -> Trigger yt-dlp download in background to C:\Users\User\Music
            print(f"[MusicQueue] '{clean_q}' not found locally. Initiating background download...")
            dl_res = local_music_engine.download_song_ytdlp(clean_q)
            if dl_res.get("status") == "success" and dl_res.get("path"):
                entry = {
                    "title": dl_res.get("title") or clean_q,
                    "artist": "Downloaded Track",
                    "filename": dl_res.get("filename"),
                    "path": dl_res.get("path"),
                    "source": "downloaded",
                    "queued_at": time.time(),
                }
            else:
                return {
                    "status": "error",
                    "message": f"Could not find or download track '{clean_q}': {dl_res.get('message')}",
                }

        with self.lock:
            if priority == "next":
                self.queue.insert(0, entry)
                pos = 1
            else:
                self.queue.append(entry)
                pos = len(self.queue)
            self._save_queue()

        return {
            "status": "success",
            "message": f"Added '{entry['title']}' to playback queue (Position #{pos}).",
            "position": pos,
            "track": entry,
            "queue_length": len(self.queue),
        }

    def get_queue(self) -> Dict[str, Any]:
        """Returns the current queue and current track state."""
        with self.lock:
            return {
                "status": "success",
                "queue_length": len(self.queue),
                "current_track": self.current_track,
                "queue": list(self.queue),
            }

    def play_next(self) -> Dict[str, Any]:
        """Pops the first song from queue and begins playback."""
        with self.lock:
            if not self.queue:
                return {"status": "empty", "message": "The playback queue is currently empty."}

            next_track = self.queue.pop(0)
            self.current_track = next_track
            self._save_queue()

        # Play through local_music_engine
        res = local_music_engine.play_track(next_track["path"])
        return {
            "status": "success",
            "message": f"Now playing '{next_track['title']}' from queue.",
            "track": next_track,
            "play_result": res,
            "remaining_in_queue": len(self.queue),
        }

    def remove_at(self, index: int) -> Dict[str, Any]:
        """Removes a track at specific 0-based index."""
        with self.lock:
            if 0 <= index < len(self.queue):
                removed = self.queue.pop(index)
                self._save_queue()
                return {
                    "status": "success",
                    "message": f"Removed '{removed['title']}' from queue.",
                    "queue_length": len(self.queue),
                }
            return {"status": "error", "message": "Invalid queue index."}

    def clear(self) -> Dict[str, Any]:
        """Clears all queued items."""
        with self.lock:
            cnt = len(self.queue)
            self.queue.clear()
            self._save_queue()
            return {"status": "success", "message": f"Cleared {cnt} tracks from queue.", "queue_length": 0}


# Global Singleton Instance
QUEUE_ENGINE = MusicQueueEngine()
