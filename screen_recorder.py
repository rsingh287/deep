import os
import threading
import time
from ctypes import windll
from typing import Any, Dict, Optional

import cv2
import numpy as np
from PIL import ImageGrab

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(PROJECT_DIR, "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)


def _ensure_interactive_desktop_context():
    try:
        WINSTA_ALL = 0x37F
        DESKTOP_ALL = 0x1FF
        hwinsta = windll.user32.OpenWindowStationW("WinSta0", False, WINSTA_ALL)
        if hwinsta:
            windll.user32.SetProcessWindowStation(hwinsta)
        hdesk = windll.user32.OpenDesktopW("Default", 0, False, DESKTOP_ALL)
        if hdesk:
            windll.user32.SetThreadDesktop(hdesk)
    except Exception:
        pass


class DesktopScreenRecorder:
    def __init__(self):
        self._is_recording = False
        self._thread: Optional[threading.Thread] = None
        self._current_file: Optional[str] = None
        self._start_time: float = 0.0
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self, fps: float = 10.0, max_duration_s: int = 1800) -> Dict[str, Any]:
        with self._lock:
            if self._is_recording:
                elapsed = round(time.time() - self._start_time, 1)
                return {
                    "status": "already_recording",
                    "file": self._current_file,
                    "elapsed_seconds": elapsed,
                    "message": f"Screen recording is already in progress ({elapsed}s).",
                }

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self._current_file = os.path.join(
                RECORDINGS_DIR, f"recording_{timestamp}.mp4"
            )
            self._is_recording = True
            self._start_time = time.time()
            self._stop_event.clear()

            self._thread = threading.Thread(
                target=self._record_loop,
                args=(self._current_file, fps, max_duration_s),
                daemon=True,
            )
            self._thread.start()

            return {
                "status": "recording_started",
                "file": self._current_file,
                "fps": fps,
                "message": f"Desktop screen recording started. Saving to {os.path.basename(self._current_file)}",
            }

    def _record_loop(self, output_path: str, fps: float, max_duration_s: int):
        _ensure_interactive_desktop_context()
        try:
            try:
                initial_screen = ImageGrab.grab(all_screens=True)
            except Exception:
                initial_screen = ImageGrab.grab()

            orig_w, orig_h = initial_screen.size

            target_w = 1280
            target_h = int(orig_h * (target_w / orig_w))
            target_w = target_w if target_w % 2 == 0 else target_w + 1
            target_h = target_h if target_h % 2 == 0 else target_h + 1

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

            interval = 1.0 / fps

            while not self._stop_event.is_set():
                frame_start = time.time()
                if frame_start - self._start_time > max_duration_s:
                    break

                try:
                    screen_img = ImageGrab.grab(all_screens=True)
                except Exception:
                    screen_img = ImageGrab.grab()

                if screen_img.mode in ("RGBA", "P"):
                    screen_img = screen_img.convert("RGB")

                img_np = np.array(screen_img)
                frame_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                if (orig_w, orig_h) != (target_w, target_h):
                    frame_bgr = cv2.resize(
                        frame_bgr, (target_w, target_h), interpolation=cv2.INTER_AREA
                    )

                writer.write(frame_bgr)

                elapsed = time.time() - frame_start
                sleep_time = max(0.001, interval - elapsed)
                time.sleep(sleep_time)

            writer.release()
        except Exception as e:
            print(f"[ScreenRecorder] Error during recording loop: {e}")
        finally:
            with self._lock:
                self._is_recording = False

    def stop(self) -> Dict[str, Any]:
        with self._lock:
            if not self._is_recording:
                return {
                    "status": "not_recording",
                    "message": "No active screen recording session to stop.",
                }

            self._stop_event.set()
            recorded_file = self._current_file

        if self._thread:
            self._thread.join(timeout=3.0)

        duration = round(time.time() - self._start_time, 1)
        size_mb = 0.0
        if recorded_file and os.path.exists(recorded_file):
            size_mb = round(os.path.getsize(recorded_file) / (1024 * 1024), 2)

        return {
            "status": "recording_saved",
            "file": recorded_file,
            "duration_seconds": duration,
            "size_mb": size_mb,
            "message": f"Screen recording saved ({duration}s, {size_mb} MB) to {os.path.basename(recorded_file or '')}.",
        }

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            if self._is_recording:
                elapsed = round(time.time() - self._start_time, 1)
                return {
                    "status": "recording",
                    "file": self._current_file,
                    "elapsed_seconds": elapsed,
                    "message": f"Recording in progress ({elapsed}s elapsed).",
                }
            return {"status": "idle", "message": "Screen recorder is idle."}


_RECORDER = DesktopScreenRecorder()


def start_recording(fps: float = 10.0) -> Dict[str, Any]:
    return _RECORDER.start(fps=fps)


def stop_recording() -> Dict[str, Any]:
    return _RECORDER.stop()


def get_recording_status() -> Dict[str, Any]:
    return _RECORDER.get_status()
