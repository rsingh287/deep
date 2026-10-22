import os
import sys
import json
import time
import queue
import socket
import subprocess
import re

# Set encoding to UTF-8
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Ensure stdout and stderr exist and handle encoding safely
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_sentinel.log")
log_file = None
try:
    log_file = open(log_path, "a", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = log_file
    if sys.stderr is None:
        sys.stderr = log_file
except Exception:
    pass

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    if log_file:
        try:
            log_file.write(line + "\n")
            log_file.flush()
        except Exception:
            pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
START_BAT = os.path.join(CURRENT_DIR, "start.bat")
STOP_BAT = os.path.join(CURRENT_DIR, "stop.bat")

START_WORDS = [
    "wake up", "back to work", "time to work",
    "wake up deep", "start deep", "systems on", "power on",
    "good morning", "good morning deep", "morning deep"
]

STOP_WORDS = [
    "good night", "go to sleep", "sleep deep",
    "stop agent", "turn off", "shut down", "goodnight"
]

INTERACT_WORDS = [
    "hey deep", "hey jarvis", "hey friday", "jarvis", "friday", "deep"
]

MEDIA_PLAY_PAUSE_PATTERNS = [
    "play music", "played music", "pause music", "pause the music", "play the music",
    "play pause", "play or pause", "pause or play", "toggle music", "resume music",
    "play song", "pause song", "stop music", "stop the music", "stop song",
    "unpause", "music play", "music pause"
]

MEDIA_NEXT_PATTERNS = [
    "play next", "next song", "next track", "skip song", "skip track",
    "the next", "play the next", "next music", "skip music",
    "skip drag", "next drag", "skip trap", "skip drad", "skip check"
]

MEDIA_PREV_PATTERNS = [
    "play prev", "play previous", "previous song", "previous track",
    "prev song", "prev track", "the previous", "in previous", "play the previous",
    "rewind song", "previous music", "back song"
]

def trigger_media_key(action):
    """Placeholder for external key dispatch; media actions are already executed cleanly in check_media_intent."""
    return True

def check_media_intent(text):
    t = text.strip().lower()
    for prefix in ["hey deep ", "hey jarvis ", "hey friday ", "deep ", "jarvis ", "friday ", "please ", "the "]:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()

    # Direct separate speaker / headphone / volume controls
    if any(k in t for k in ["volume", "speaker", "speakers", "headphone", "headphones", "headset", "sound", "louder", "quieter"]):
        try:
            import everyday_pc_actions
            res = everyday_pc_actions.handle_everyday_command(t)
            if res:
                markdown_msg = res[0]
                clean_voice = re.sub(r"[*_#`🔊🔉🔇]", "", markdown_msg).replace("→", "to").strip()
                speak(clean_voice)
                return "device_volume"
        except Exception as e:
            log(f"[Sentinel Volume Error]: {e}")

    # Direct shuffle music command (plays in standalone DJ & AutoMix engine on PC Speakers)
    shuffle_synonyms = ["shuffle", "shovel", "shuffel", "shuffled", "shoffle", "shaffal", "shavel", "shuffler"]
    if any(s in t for s in shuffle_synonyms):
        try:
            import local_music_engine
            res = local_music_engine.play_shuffle()
            if res and res.get("status") == "success" and "track" in res:
                track = res["track"]
                speak(f"Playing {track['title']} on shuffle with AutoMix active.")
                return "shuffle"
        except Exception as e:
            log(f"[Sentinel Shuffle Error]: {e}")

    # Direct song / YouTube command (voice dispatched to everyday_pc_actions)
    if (t.startswith("play ") or "youtube" in t or t.startswith("open youtube")) and not any(s in t for s in shuffle_synonyms) and t not in [
        "play", "play music", "play the music", "play song", "play or pause", "play pause"
    ]:
        try:
            import everyday_pc_actions
            res = everyday_pc_actions.handle_everyday_command(t)
            if res:
                markdown_msg = res[0]
                clean_voice = re.sub(r"[*_#`▶️🎵⬇️🌐]", "", markdown_msg).split("\n")[0].strip()
                if clean_voice:
                    speak(clean_voice)
                return "everyday_song_or_youtube"
        except Exception as e:
            log(f"[Sentinel Music/YT Error]: {e}")

    # Dedicated PAUSE command & common Vosk phonetic homophones ('bars', 'both music', 'boss music', etc.)
    pause_exact_phrases = [
        "pause", "pause music", "pause the music", "pause song", "pause the song",
        "stop music", "stop the music", "stop song", "stop playback", "pause playback",
        "bars", "both music", "boss music", "bar music", "bars music",
        "buzz", "buzz music", "pass music", "paws", "paws music", "cause music",
        "parse", "parse music", "pos", "pose", "post music", "hold music",
        "rok do", "gana roko", "gana rok do", "gana band karo", "band karo"
    ]
    if t in pause_exact_phrases or any(t == p for p in pause_exact_phrases) or any(t.startswith(p) for p in ["pause ", "stop music", "stop song"]):
        try:
            import local_music_engine
            local_music_engine.control_media("pause")
            speak("Music paused.")
            return "pause"
        except Exception as e:
            log(f"[Sentinel Pause Error]: {e}")
            return "pause"

    # Dedicated PLAY / RESUME command
    play_exact_phrases = [
        "play", "resume", "unpause", "play music", "play the music", "resume music",
        "resume song", "play song", "unpause music", "continue music", "start music",
        "chalao", "gana chalao", "gana shuru karo"
    ]
    if t in play_exact_phrases or any(t == p for p in play_exact_phrases):
        try:
            import local_music_engine
            local_music_engine.control_media("play")
            speak("Music playing.")
            return "play"
        except Exception as e:
            log(f"[Sentinel Play Error]: {e}")
            return "play"

    if t in ["play or pause", "pause or play", "toggle music", "play pause"]:
        try:
            import local_music_engine
            local_music_engine.control_media("play_pause")
            return "play_pause"
        except Exception:
            return "play_pause"

    # DJ Crossfade toggle commands
    if any(k in t for k in ["dj mode", "enable dj", "start dj", "dj mix", "crossfade mode", "turn on dj", "dj crossfade"]):
        try:
            import local_music_engine
            local_music_engine.toggle_dj_mode(True)
            speak("DJ Crossfade mode activated. Mixing tracks seamlessly.")
            return "enable_dj"
        except Exception as e:
            log(f"[Sentinel DJ Error]: {e}")
            return "enable_dj"

    if any(k in t for k in ["disable dj", "turn off dj", "stop dj", "exit dj"]):
        try:
            import local_music_engine
            local_music_engine.toggle_dj_mode(False)
            speak("DJ mode turned off. Switched back to standard player.")
            return "disable_dj"
        except Exception as e:
            log(f"[Sentinel DJ Error]: {e}")
            return "disable_dj"

    # Apple Music-style AutoMix toggle commands
    if any(k in t for k in ["automix", "enable automix", "turn on automix", "start automix", "apple music mode"]):
        try:
            import local_music_engine
            local_music_engine.send_standalone_dj_action("enable_automix")
            speak("AutoMix mode activated. Beat matching, phrase syncing, and cue points enabled.")
            return "enable_automix"
        except Exception as e:
            log(f"[Sentinel AutoMix Error]: {e}")
            return "enable_automix"

    if any(k in t for k in ["disable automix", "turn off automix", "stop automix"]):
        try:
            import local_music_engine
            local_music_engine.send_standalone_dj_action("disable_automix")
            speak("AutoMix mode disabled. Standard crossfade active.")
            return "disable_automix"
        except Exception as e:
            log(f"[Sentinel AutoMix Error]: {e}")
            return "disable_automix"

    if t in ["next", "skip", "next song", "next track", "skip song", "skip track", "change song"] or any(p in t for p in MEDIA_NEXT_PATTERNS):
        try:
            import local_music_engine
            local_music_engine.control_media("next")
            speak("Playing next track.")
            return "next"
        except Exception as e:
            log(f"[Sentinel Next Error]: {e}")
            return "next"

    if t in ["prev", "previous", "rewind", "previous song", "previous track"] or any(p in t for p in MEDIA_PREV_PATTERNS):
        try:
            import local_music_engine
            local_music_engine.control_media("prev")
            speak("Previous track.")
            return "prev"
        except Exception as e:
            log(f"[Sentinel Prev Error]: {e}")
            return "prev"

    if t in ["stop"]:
        try:
            import local_music_engine
            local_music_engine.control_media("stop")
            speak("Playback stopped.")
            return "stop"
        except Exception:
            return "stop"

    if t in ["mute", "unmute"]:
        return "mute"


    # Smart Playback Queue Voice Commands
    if t.startswith("play ") and t.endswith(" next"):
        q_target = t[5:-5].strip()
        if q_target:
            try:
                import music_queue_engine
                res = music_queue_engine.QUEUE_ENGINE.enqueue(q_target, priority="next")
                if res.get("status") == "success":
                    speak(f"Enqueued {res['track']['title']} to play next.")
                return "queue_next"
            except Exception as e:
                log(f"[Sentinel Queue Error]: {e}")

    if any(p in t for p in MEDIA_PLAY_PAUSE_PATTERNS):
        try:
            import local_music_engine
            local_music_engine.control_media("play_pause")
            speak("Media toggled.")
            return "play_pause"
        except Exception:
            return "play_pause"
    if any(p in t for p in ["volume up", "turn it up", "turn up", "louder"]):
        return "vol_up"
    if any(p in t for p in ["volume down", "turn it down", "turn down", "lower volume"]):
        return "vol_down"

    return None

def speak(text):
    """Speaks text using DEEPOmniVoice (offline TTS) asynchronously so it doesn't block audio listening."""
    try:
        import voice_state
        if voice_state.is_voice_muted():
            log(f"[Sentinel] Voice is OFF (muted globally). Suppressing voice output: '{text[:50]}...'")
            return
    except Exception:
        pass

    def _run():
        try:
            import voice_state
            if voice_state.is_voice_muted():
                return
            from omni_voice import get_voice_engine
            v = get_voice_engine()
            if v.active:
                v.speak(text)
        except Exception as e:
            log(f"[Sentinel Voice Error]: {e}")
    import threading
    threading.Thread(target=_run, daemon=True).start()

def play_tone(action="start"):
    try:
        import voice_state
        if voice_state.is_voice_muted():
            return
    except Exception:
        pass
    try:
        import winsound
        if action == "start":
            winsound.Beep(523, 100) # C5
            winsound.Beep(659, 100) # E5
            winsound.Beep(784, 150) # G5
        elif action == "stop":
            winsound.Beep(784, 100) # G5
            winsound.Beep(659, 100) # E5
            winsound.Beep(523, 200) # C5
        elif action == "interact":
            winsound.Beep(700, 100)
            winsound.Beep(900, 120)
    except Exception:
        pass

def is_agent_online(port=5000):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def press_space_key():
    try:
        import ctypes
        ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0x20, 0, 2, 0)
    except Exception as e:
        log(f"[Sentinel] Keypress error: {e}")

def open_or_focus_ui():
    titles = [
        "Deep - 3D AI Workstation Cockpit",
        "Antigravity Local AI PC Cockpit",
        "Local AI Cockpit",
        "Deep - 3D AI Workstation"
    ]
    try:
        import pygetwindow as gw
        for t in titles:
            windows = gw.getWindowsWithTitle(t)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.3)
                press_space_key()
                return
    except Exception:
        pass
    
    # Launch borderless app mode via MS Edge if not found
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "msedge", "--app=http://127.0.0.1:5000"])
    except Exception as e:
        log(f"[Sentinel] Error opening browser: {e}")

def start_all_systems(phrase_heard=""):
    log(f"\n[Sentinel] START TRIGGERED ('{phrase_heard}'): Starting all AI systems...")
    play_tone("start")
    
    if "good morning" in phrase_heard or "morning" in phrase_heard:
        speak("Good morning! Initializing systems.")
    else:
        speak("Waking up systems.")

    subprocess.Popen([START_BAT], shell=True, cwd=CURRENT_DIR)
    
    # Wait until port 5000 comes alive (up to 25 seconds)
    log("[Sentinel] Waiting for AI server to initialize...")
    for _ in range(25):
        time.sleep(1)
        if is_agent_online(5000):
            log("[Sentinel] AI Agent is online! Opening Cockpit UI...")
            play_tone("interact")
            speak("All systems online, Commander.")
            open_or_focus_ui()
            break

def close_all_ui_and_service_windows():
    titles = [
        "Deep - 3D AI Workstation Cockpit",
        "Antigravity Local AI PC Cockpit",
        "Local AI Cockpit",
        "Deep - 3D AI Workstation",
        "Ollama Server",
        "AI Skills Brain API",
        "Telegram AI Bot",
        "Main AI Agent"
    ]
    try:
        import pygetwindow as gw
        for t in titles:
            try:
                for w in gw.getWindowsWithTitle(t):
                    try:
                        w.close()
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception as e:
        log(f"[Sentinel] Error closing windows: {e}")

def stop_all_systems():
    log("\n[Sentinel] STOP TRIGGERED: Putting all AI systems to sleep...")
    play_tone("stop")
    speak("Good night! Putting systems to sleep.")
    close_all_ui_and_service_windows()
    subprocess.Popen([STOP_BAT], shell=True, cwd=CURRENT_DIR)

def main():
    try:
        import sounddevice as sd
        import vosk
    except ImportError:
        log("[Sentinel] Missing sounddevice or vosk.")
        sys.exit(1)

    log("=" * 60)
    log("[Sentinel] D.E.E.P. MASTER VOICE SENTINEL ACTIVE (Always-Listening)")
    log("=" * 60)
    log("Commands supported:")
    log(" - Wake/Start: 'good morning', 'wake up deep', 'time to work', 'wake up'")
    log(" - Sleep/Stop: 'good night', 'go to sleep', 'sleep deep', 'shut down'")
    log(" - Media:      'play or pause', 'play music', 'pause', 'play next', 'play prev', 'skip', 'rewind'")
    log(" - Volume:     'volume up', 'volume down', 'mute'")
    log(" - Interact:   'hey deep', 'hey jarvis', 'friday'")
    log("=" * 60)

    try:
        model = vosk.Model(lang="en-us")
    except Exception as me:
        log(f"[Sentinel] Could not load Vosk model: {me}")
        return

    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            pass
        q.put(bytes(indata))

    while True:
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                   channels=1, callback=callback):
                log("[Sentinel] Microphone stream open. Listening for voice commands...")
                rec = vosk.KaldiRecognizer(model, 16000)
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = (res.get('text') or '').lower().strip()
                        if not text:
                            continue
                        
                        log(f"[Sentinel] Heard: '{text}'")

                        # Check for MEDIA PLAYBACK command (music control)
                        media_action = check_media_intent(text)
                        if media_action:
                            log(f"[Sentinel] 🎵 Media action triggered: {media_action}")
                            trigger_media_key(media_action)
                            play_tone("interact")
                            continue

                        # Check for START / WAKE command
                        if any(w in text for w in START_WORDS):
                            if not is_agent_online(5000):
                                start_all_systems(text)
                            else:
                                log("[Sentinel] Already running. Focusing UI...")
                                play_tone("interact")
                                open_or_focus_ui()

                        # Check for STOP / SLEEP command
                        elif any(w in text for w in STOP_WORDS):
                            stop_all_systems()

                        # Check for INTERACT / FOCUS command
                        elif any(w in text for w in INTERACT_WORDS):
                            if is_agent_online(5000):
                                play_tone("interact")
                                open_or_focus_ui()
                            else:
                                log("[Sentinel] Systems currently asleep. Say 'wake up deep' or 'good morning' to start.")

        except Exception as e:
            log(f"[Sentinel] Audio stream error: {e}. Retrying in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        import traceback
        log(f"[Sentinel CRITICAL EXIT]: {e}\n{traceback.format_exc()}")
