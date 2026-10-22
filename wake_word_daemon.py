import os
import sys
import json
import time
import queue
import requests

WAKE_WORD = "hey deep"
WAKE_WORDS = [
    "hey deep", "hey beep", "a deep", "hay deep", "hey dip", "deep",
    "hey jarvis", "jarvis", "hi jarvis",
    "hey friday", "friday", "hi friday",
    "time to work", "wake up deep"
]

def press_space_key():
    """Simulates a spacebar press using native Windows ctypes without third-party dependencies."""
    try:
        import ctypes
        # VK_SPACE = 0x20
        ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0x20, 0, 2, 0) # KEYEVENTF_KEYUP = 2
    except Exception as e:
        print(f"[Wake Word] Keypress error: {e}")

def bring_window_to_front(window_title="Antigravity Local AI PC Cockpit"):
    """Focuses the Antigravity AI Cockpit window and activates voice listening. Opens browser if not found."""
    found_window = False
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            found_window = True
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.3)
            press_space_key()
            print(f"[Wake Word] Cockpit window focused and spacebar triggered.")
    except Exception as e:
        print(f"[Wake Word] Window focus/pygetwindow error: {e}")

    if not found_window:
        print("[Wake Word] Cockpit window not found, launching App Mode UI...")
        try:
            import subprocess
            subprocess.Popen(["cmd.exe", "/c", "start", "msedge", "--app=http://127.0.0.1:5000"])
            time.sleep(2.0)
            
            # Optionally try to focus it now if pygetwindow is available
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    windows[0].activate()
                    time.sleep(0.5)
                    press_space_key()
            except:
                pass
        except Exception as e:
            print(f"[Wake Word] Error opening browser: {e}")
            press_space_key()

def main():
    try:
        import sounddevice as sd
        import vosk
    except ImportError:
        print("[Wake Word] Missing sounddevice or vosk. Install via pip.")
        sys.exit(1)

    print("[Wake Word] Initializing offline Vosk listener...")
    try:
        model = vosk.Model(lang="en-us")
    except Exception as me:
        print(f"[Wake Word] Could not load Vosk language model: {me}")
        return

    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            print(f"[Wake Word] Autonomous voice listener active. Say '{WAKE_WORD}'...")
            rec = vosk.KaldiRecognizer(model, 16000)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = (res.get('text') or '').lower().strip()
                    if text and any(ww in text for ww in WAKE_WORDS):
                        print(f"\n🌟 WAKE WORD DETECTED: '{text}'")
                        
                        # Audio acknowledgment beep
                        try:
                            import winsound
                            winsound.Beep(600, 150)
                            winsound.Beep(800, 200)
                        except:
                            pass
                            
                        bring_window_to_front()
    except Exception as audio_err:
        print(f"[Wake Word] Audio stream error: {audio_err}")

if __name__ == "__main__":
    main()
