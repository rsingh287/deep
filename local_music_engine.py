"""
Local Music Player Engine for Antigravity Local AI PC Cockpit
Scans local PC music folders, performs fuzzy song search, and triggers playback.
"""

import os
import subprocess
from typing import Any, Dict, List, Optional

MUSIC_DIRECTORIES = [
    os.path.expanduser(r"~\Music"),
    os.path.join(os.path.dirname(__file__), "music"),
    os.path.expanduser(r"~\Downloads"),
    os.path.expanduser(r"~\Desktop"),
]

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"}

os.makedirs(os.path.join(os.path.dirname(__file__), "music"), exist_ok=True)


def ensure_sample_track():
    local_dir = os.path.join(os.path.dirname(__file__), "music")
    sample_path = os.path.join(local_dir, "Antigravity_Cyber_Ambience.wav")
    if not os.path.exists(sample_path):
        try:
            import numpy as np
            import scipy.io.wavfile

            sr = 22050
            duration = 6.0
            t = np.linspace(0, duration, int(sr * duration), False)
            chord = (
                np.sin(2 * np.pi * 220 * t) * 0.3
                + np.sin(2 * np.pi * 261.63 * t) * 0.25
                + np.sin(2 * np.pi * 329.63 * t) * 0.25
                + np.sin(2 * np.pi * 440 * t) * 0.15
            )
            envelope = np.sin(np.pi * t / duration) ** 1.5
            audio = (chord * envelope * 32767).astype(np.int16)
            scipy.io.wavfile.write(sample_path, sr, audio)
        except Exception as e:
            print(f"[LocalMusic] Could not create sample track: {e}")


ensure_sample_track()


import difflib
import re

def clean_track_title(filename: str) -> str:
    """Removes website watermarks, track numbers, and bitrates to get clean song/artist title."""
    name = os.path.splitext(filename)[0]
    name = re.sub(r"\(.*?(?:desi|jatt|punjab|johal|khan|track|wap|mp3).*?\)", "", name, flags=re.I)
    name = re.sub(r"\[.*?(?:desi|jatt|punjab|johal|khan|track|wap|mp3).*?\]", "", name, flags=re.I)
    name = re.sub(r"\b(?:128kbps|320kbps|www\.[a-z0-9\-]+\.com|mp3_160k|official song)\b", "", name, flags=re.I)
    name = re.sub(r"^\d{1,3}[\s_\-]+", "", name)
    name = name.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", name).strip() or os.path.splitext(filename)[0]


import threading
import time

_CACHE_LOCK = threading.Lock()
_LOCAL_MUSIC_CACHE = {
    "tracks": [],
    "last_scan": 0.0,
    "token_map": {},  # token -> list of tracks
}


def invalidate_music_cache():
    """Forces next music scan to refresh the cache from disk."""
    with _CACHE_LOCK:
        _LOCAL_MUSIC_CACHE["last_scan"] = 0.0


def scan_local_music(max_results: int = 1000, force_rescan: bool = False) -> List[Dict[str, Any]]:
    """Scans all configured music directories with fast in-memory caching for sub-millisecond response."""
    now = time.time()
    with _CACHE_LOCK:
        if not force_rescan and _LOCAL_MUSIC_CACHE["tracks"] and (now - _LOCAL_MUSIC_CACHE["last_scan"] < 90.0):
            return _LOCAL_MUSIC_CACHE["tracks"][:max_results]

    found_tracks = []
    seen_paths = set()

    for folder in MUSIC_DIRECTORIES:
        if not os.path.exists(folder):
            continue
        try:
            for root, dirs, files in os.walk(folder):
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith((".", "$", "~"))
                    and d
                    not in (
                        "node_modules",
                        "site-packages",
                        "venv",
                        ".git",
                        "$RECYCLE.BIN",
                        "System Volume Information",
                        "ComfyUI_windows_portable",
                    )
                ]
                for file in sorted(files):
                    # Filter junk, recycle bin, or hidden files
                    if file.startswith(("$", ".", "~", "-")):
                        continue
                    ext = os.path.splitext(file)[1].lower()
                    if ext in AUDIO_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        if full_path in seen_paths:
                            continue
                        seen_paths.add(full_path)

                        try:
                            stat = os.stat(full_path)
                            if stat.st_size < 1024 and ext != ".wav":
                                continue
                            size_mb = round(stat.st_size / (1024 * 1024), 2)
                            title = clean_track_title(file)
                            found_tracks.append(
                                {
                                    "filename": file,
                                    "title": title,
                                    "path": full_path,
                                    "size_mb": size_mb,
                                    "folder": os.path.basename(root) or root,
                                    "ext": ext,
                                }
                            )
                            if len(found_tracks) >= max_results:
                                break
                        except Exception:
                            continue
        except Exception as e:
            print(f"[LocalMusic] Error scanning {folder}: {e}")

    with _CACHE_LOCK:
        _LOCAL_MUSIC_CACHE["tracks"] = found_tracks
        _LOCAL_MUSIC_CACHE["last_scan"] = now
        token_map = {}
        for t in found_tracks:
            words = set(re.findall(r"[a-z0-9]+", t["title"].lower()) + re.findall(r"[a-z0-9]+", t["filename"].lower()))
            for w in words:
                if len(w) >= 2:
                    token_map.setdefault(w, []).append(t)
        _LOCAL_MUSIC_CACHE["token_map"] = token_map

    return found_tracks[:max_results]


def find_track(query: str) -> Optional[Dict[str, Any]]:
    """
    Finds the best matching audio track using intelligent song vs. artist intent parsing,
    token matching, and boundary verification.

    Rules:
    1. If the user asks for a specific song (e.g. 'butterfly by jass bajwa' or 'cute munda sharry maan'),
       the SONG TITLE portion must match tokens in the local track. Just matching the singer
       is NEVER sufficient — if the requested song title is not found locally, returns None
       so the caller downloads the track via yt-dlp.
    2. If the user asks for an artist/singer only (e.g. 'songs by jass bajwa', 'play jass bajwa', 'jass bajwa songs'),
       it matches and returns a local track by that artist.
    3. Multi-word song queries without 'by' require all substantial query tokens to match.
    """
    tracks = scan_local_music(max_results=2000)
    if not tracks:
        return None

    q = (query or "").lower().strip()
    generic_keywords = [
        "music", "song", "any", "local music", "something",
        "a song", "some music", "my music", "offline music", "pc music",
        "gana", "local gana", "play local music", "play music"
    ]
    if not q or q in generic_keywords:
        for t in tracks:
            if t["size_mb"] > 1.0:
                return t
        return tracks[0]

    # Clean leading imperative verbs
    q = re.sub(r"^(?:play|listen to)\s+", "", q).strip()

    # -------------------------------------------------------------------------
    # Pattern A: "<song> by <artist>" or "<song> from <artist>" or "<song> of <artist>"
    # -------------------------------------------------------------------------
    m_by = re.match(r"^(.*?)\s+(?:by|from|of)\s+(.*?)$", q)
    if m_by:
        song_part = m_by.group(1).strip()
        artist_part = m_by.group(2).strip()

        generic_song_words = {"song", "songs", "music", "track", "tracks", "gana", "any", "all", "a", "the", ""}
        song_tokens = [w for w in re.findall(r"[a-z0-9]+", song_part) if w not in generic_song_words and len(w) >= 2]
        artist_tokens = [w for w in re.findall(r"[a-z0-9]+", artist_part) if len(w) >= 2]

        if not song_tokens:
            # Pure artist request (e.g. "songs by jass bajwa")
            for t in tracks:
                t_low = t["title"].lower() + " " + t["filename"].lower()
                if all(at in t_low for at in artist_tokens):
                    return t
            return None
        else:
            # Specific song + artist request (e.g. "butterfly by jass bajwa")
            # BOTH the song tokens AND artist tokens MUST match!
            candidates = []
            for t in tracks:
                t_low = t["title"].lower() + " " + t["filename"].lower()
                tokens_in_track = re.findall(r"[a-z0-9]+", t_low)

                # 1. Song tokens match count
                song_match_count = 0
                for st in song_tokens:
                    if st in t_low:
                        song_match_count += 1
                    elif any(difflib.SequenceMatcher(None, st, tw).ratio() >= 0.85 for tw in tokens_in_track):
                        song_match_count += 1

                # If song tokens do NOT match, REJECT this track completely!
                if song_match_count < len(song_tokens):
                    continue

                # 2. Artist tokens match count
                artist_match_count = 0
                for at in artist_tokens:
                    if at in t_low:
                        artist_match_count += 1
                    elif any(difflib.SequenceMatcher(None, at, tw).ratio() >= 0.85 for tw in tokens_in_track):
                        artist_match_count += 1

                min_artist_req = 1 if len(artist_tokens) <= 2 else (len(artist_tokens) // 2)
                if artist_match_count < min_artist_req:
                    continue

                score = (song_match_count * 2.0) + artist_match_count
                candidates.append((score, t))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                return candidates[0][1]
            return None

    # -------------------------------------------------------------------------
    # Pattern B: "<artist> songs" or "<artist> song" (Pure artist request)
    # -------------------------------------------------------------------------
    m_art_songs = re.match(r"^(.*?)\s+(?:songs|song|music|tracks|track|gana)$", q)
    if m_art_songs:
        art_cand = m_art_songs.group(1).strip()
        art_tokens = [w for w in re.findall(r"[a-z0-9]+", art_cand) if len(w) >= 2]
        if art_tokens:
            for t in tracks:
                t_low = t["title"].lower() + " " + t["filename"].lower()
                if all(at in t_low for at in art_tokens):
                    return t
            return None

    # -------------------------------------------------------------------------
    # Pattern C: General Query (single word, multi-word song, or singer)
    # -------------------------------------------------------------------------
    stop_words = {"play", "song", "track", "music", "the", "a", "an", "gana"}
    q_words = [w for w in re.findall(r"[a-z0-9]+", q) if w not in stop_words and len(w) >= 2]
    if not q_words:
        for t in tracks:
            if t["size_mb"] > 1.0:
                return t
        return tracks[0]

    # 1. Exact full phrase match
    q_clean = " ".join(q_words)
    for t in tracks:
        if q_clean in t["title"].lower() or q_clean in t["filename"].lower():
            return t

    # 2. Strict fuzzy match: EVERY query token must be matched in the candidate
    best_match = None
    best_score = 0.0

    for t in tracks:
        t_low = t["title"].lower()
        f_low = t["filename"].lower()
        all_tokens = re.findall(r"[a-z0-9]+", t_low) + re.findall(r"[a-z0-9]+", f_low)
        tokens_set = set(all_tokens)

        matched_tokens = 0
        token_scores = []
        for qw in q_words:
            best_t = 0.0
            for tw in tokens_set:
                if len(tw) < 2:
                    continue
                r = difflib.SequenceMatcher(None, qw, tw).ratio()
                if len(qw) >= 3 and len(tw) >= 3 and (qw in tw or tw in qw):
                    r = max(r, 0.9)
                best_t = max(best_t, r)
            if best_t >= 0.75:
                matched_tokens += 1
            token_scores.append(best_t)

        # STRICT RULE: For multi-word queries, ALL words must match!
        # If words like 'cute' or 'butterfly' are missing, this is NOT the requested song!
        if matched_tokens < len(q_words):
            continue

        score = sum(token_scores) / len(token_scores) if token_scores else 0.0
        if score > best_score:
            best_score = score
            best_match = t

    if best_match and best_score >= 0.75:
        return best_match

    return None


def play_track_native(track_path: str) -> Dict[str, Any]:
    """Launches the audio track on Windows using the default media player or PowerShell Start-Process."""
    if not os.path.exists(track_path):
        return {"status": "error", "message": f"File not found: {track_path}"}

    try:
        os.startfile(track_path)
        filename = os.path.basename(track_path)
        return {
            "status": "success",
            "message": f"Playing '{filename}' in your default media player.",
            "filename": filename,
            "path": track_path,
        }
    except Exception:
        try:
            # Fallback to PowerShell Start-Process with explicit quote escaping
            cmd = f'Start-Process -FilePath "{track_path}"'
            subprocess.Popen(["powershell.exe", "-NoProfile", "-Command", cmd])
            filename = os.path.basename(track_path)
            return {
                "status": "success",
                "message": f"Launched '{filename}'.",
                "filename": filename,
                "path": track_path,
            }
        except Exception as e2:
            return {"status": "error", "message": f"Failed to play file: {e2}"}


# =========================================================================
# 🔊 NATIVE PC SPEAKERS MUSIC ENGINE & MEDIA HUD TELEMETRY
# =========================================================================

_LAST_PLAYED_TRACK = {
    "title": "Local PC Music",
    "artist": "PC Speakers (Realtek Audio)",
    "filename": "",
    "path": "",
    "is_playing": False,
}


def set_last_played_track(track_dict: Dict[str, Any], is_playing: bool = True):
    """Updates the last played track telemetry for the Media HUD Remote."""
    with _CACHE_LOCK:
        _LAST_PLAYED_TRACK.update({
            "title": track_dict.get("title") or clean_track_title(track_dict.get("filename", "")),
            "artist": "PC Speakers (Realtek Audio)",
            "filename": track_dict.get("filename", ""),
            "path": track_dict.get("path", ""),
            "is_playing": is_playing,
        })


def is_dj_mode_enabled() -> bool:
    """Returns True if the Standalone DJ Engine is currently active on 127.0.0.1:8765."""
    stat = query_standalone_dj_status()
    return stat is not None


def toggle_dj_mode(enable: Optional[bool] = None) -> bool:
    return is_dj_mode_enabled()


def send_standalone_dj_action(action: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Sends action to the Standalone DJ Engine on 127.0.0.1:8765 if running."""
    import urllib.request
    import json
    try:
        data = {"action": action}
        if payload:
            data.update(payload)
        req = urllib.request.Request(
            "http://127.0.0.1:8765/control",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def query_standalone_dj_status() -> Optional[Dict[str, Any]]:
    """Queries telemetry from the Standalone DJ Engine on 127.0.0.1:8765 if running."""
    import urllib.request
    import json
    try:
        req = urllib.request.Request("http://127.0.0.1:8765/status")
        with urllib.request.urlopen(req, timeout=0.25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _stop_dj_playback():
    """Ensures no background audio is lingering in pygame mixer."""
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.quit()
    except Exception:
        pass


def play_track(track_path: str) -> Dict[str, Any]:
    """Plays track on PC Realtek Speakers via Standalone DJ Engine (with AutoMix), or native player fallback."""
    if os.path.exists(track_path):
        import urllib.request
        import json
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8765/play",
                data=json.dumps({"path": track_path}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("status") == "success":
                    filename = os.path.basename(track_path)
                    set_last_played_track({
                        "title": clean_track_title(filename),
                        "filename": filename,
                        "path": track_path,
                    }, is_playing=True)
                    return {
                        "status": "success",
                        "message": f"Playing '{clean_track_title(filename)}' on PC Speakers (AutoMix Engine).",
                        "filename": filename,
                        "path": track_path,
                    }
        except Exception as e:
            print(f"[LocalMusic] Standalone DJ /play route error: {e}")

    # Fallback to native Windows media player if DJ engine is not running
    res = play_track_native(track_path)
    if res.get("status") == "success":
        set_last_played_track({
            "title": clean_track_title(os.path.basename(track_path)),
            "filename": os.path.basename(track_path),
            "path": track_path,
        }, is_playing=True)
    return res


def get_chrome_path() -> Optional[str]:
    """Finds the absolute path to Google Chrome executable on Windows."""
    import winreg
    import shutil

    # 1. Check registry App Paths
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                val, _ = winreg.QueryValueEx(key, "")
                if val and os.path.isfile(val):
                    return val
        except Exception:
            pass

    # 2. Check standard installation directories
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            return p

    # 3. Check system PATH
    which_path = shutil.which("chrome") or shutil.which("chrome.exe")
    if which_path and os.path.isfile(which_path):
        return which_path

    return None


def _bring_chrome_to_foreground():
    """Restores and brings Google Chrome to the front of the active display."""
    import ctypes
    import time
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)

        def _enum_cb(hwnd, _):
            if user32.IsWindow(hwnd):
                cls_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cls_buf, 256)
                if "Chrome_WidgetWin_1" in cls_buf.value:
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    user32.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL
                    user32.SetForegroundWindow(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        time.sleep(0.4)
        user32.EnumWindows(WNDENUMPROC(_enum_cb), 0)
    except Exception:
        pass


def open_in_chrome(url: str, as_app: bool = False) -> bool:
    """
    Opens URL specifically in Google Chrome with a normal visible window on the active desktop.
    Gracefully pauses background DJ engine first to prevent overlapping sound.
    """
    import os
    import subprocess
    import webbrowser
    import ctypes

    # 1. Gracefully pause standalone DJ engine so local music and YouTube do not clash
    try:
        send_standalone_dj_action("pause")
    except Exception:
        pass

    # Ensure current thread has access to interactive desktop WinSta0\Default
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

    chrome_bin = get_chrome_path()
    arg_str = f'--app={url}' if as_app else url

    if chrome_bin:
        # Method A: Native Python os.startfile with arguments
        # Directly invokes Win32 ShellExecuteExW without passing through cmd.exe or subshell,
        # completely preventing quote escaping issues and Windows cannot find '\\' errors.
        try:
            os.startfile(chrome_bin, arguments=arg_str)
            _bring_chrome_to_foreground()
            return True
        except Exception as e:
            print(f"[LocalMusic] Chrome os.startfile error: {e}")

        # Method B: Direct Win32 ShellExecuteW
        try:
            res = ctypes.windll.shell32.ShellExecuteW(None, "open", chrome_bin, arg_str, None, 1)
            if res > 32:
                _bring_chrome_to_foreground()
                return True
        except Exception as e:
            print(f"[LocalMusic] Chrome ShellExecute error: {e}")

        # Method C: Subprocess Popen with explicit STARTUPINFO (SW_SHOWNORMAL + WinSta0\Default)
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 1  # SW_SHOWNORMAL
            si.lpDesktop = r"WinSta0\Default"
            args = [chrome_bin]
            if as_app:
                args.append(f"--app={url}")
            else:
                args.append(url)
            subprocess.Popen(args, startupinfo=si, shell=False)
            _bring_chrome_to_foreground()
            return True
        except Exception as e:
            print(f"[LocalMusic] Chrome direct Popen error: {e}")

    # Fallback: PowerShell Start-Process targeting chrome
    try:
        cmd = f'Start-Process "chrome" -ArgumentList "{url}"'
        subprocess.Popen(["powershell.exe", "-NoProfile", "-Command", cmd], shell=False)
        _bring_chrome_to_foreground()
        return True
    except Exception:
        pass

    # Universal Fallback: Windows default browser
    try:
        os.startfile(url)
        return True
    except Exception:
        pass

    try:
        webbrowser.open(url)
        return True
    except Exception:
        pass

    return False


def open_in_browser(url: str, as_app: bool = False) -> bool:
    """
    Opens YouTube / media URLs in Google Chrome (routed to PC Speakers).
    """
    return open_in_chrome(url, as_app=as_app)


# Alias for backwards compatibility
open_in_google_chrome = open_in_chrome


def download_and_play_track(query: str) -> Dict[str, Any]:
    """
    Searches YouTube for the track, extracts high-quality audio as MP3 via yt-dlp + ffmpeg,
    saves the MP3 directly into the user's C:\\Users\\User\\Music directory,
    and immediately launches the track in the default Windows PC media player.
    """
    import os
    import re
    import time
    import glob

    music_dir = os.path.expanduser(r"~\Music")
    os.makedirs(music_dir, exist_ok=True)

    clean_q = (query or "").strip()
    clean_q = re.sub(r"^(?:play\s+(?:the\s+)?(?:song|track|music)?|listen\s+to)\s+", "", clean_q, flags=re.I).strip()
    clean_q = re.sub(r"\b(?:on\s+youtube|in\s+youtube|from\s+youtube|youtube)\b", "", clean_q, flags=re.I).strip()
    if not clean_q:
        clean_q = "trending music"

    search_term = f"ytsearch1:{clean_q}"
    print(f"[LocalMusic] Downloading track via yt-dlp: '{clean_q}' -> {search_term}")

    before_files = set(glob.glob(os.path.join(music_dir, "*.mp3")))
    downloaded_path = None
    track_title = clean_q

    try:
        import yt_dlp

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(music_dir, '%(title)s.%(ext)s'),
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                },
                {
                    'key': 'SponsorBlock',
                    'categories': {'music_offtopic'},
                },
                {
                    'key': 'ModifyChapters',
                    'remove_sponsor_segments': {'music_offtopic'},
                },
            ],
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'windowsfilenames': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_term, download=True)
            if info:
                if 'entries' in info and info['entries']:
                    entry = info['entries'][0]
                else:
                    entry = info
                track_title = entry.get('title') or clean_q
                raw_filename = ydl.prepare_filename(entry)
                candidate_mp3 = os.path.splitext(raw_filename)[0] + ".mp3"
                if os.path.exists(candidate_mp3):
                    downloaded_path = candidate_mp3

    except Exception as e:
        print(f"[LocalMusic] yt_dlp download error: {e}")

    # Fallback to checking newly added mp3 files in music_dir
    if not downloaded_path or not os.path.exists(downloaded_path):
        after_files = set(glob.glob(os.path.join(music_dir, "*.mp3")))
        diff = after_files - before_files
        if diff:
            downloaded_path = max(diff, key=os.path.getmtime)
        else:
            all_mp3s = glob.glob(os.path.join(music_dir, "*.mp3"))
            if all_mp3s:
                latest = max(all_mp3s, key=os.path.getmtime)
                if time.time() - os.path.getmtime(latest) < 180:
                    downloaded_path = latest

    if not downloaded_path or not os.path.exists(downloaded_path):
        return {
            "status": "error",
            "message": f"Could not download audio for '{clean_q}'.",
            "query": clean_q,
        }

    try:
        size_mb = round(os.path.getsize(downloaded_path) / (1024 * 1024), 2)
    except Exception:
        size_mb = 0.0

    filename = os.path.basename(downloaded_path)
    clean_title = clean_track_title(filename) or track_title

    # Invalidate cache so newly downloaded song is instantly discoverable
    invalidate_music_cache()

    # Launch in default Windows player (or DJ engine if DJ mode active)
    play_track(downloaded_path)

    return {
        "status": "success",
        "message": f"Downloaded and playing '{clean_title}' in your PC Music Player.",
        "title": clean_title,
        "filename": filename,
        "path": downloaded_path,
        "size_mb": size_mb,
    }


download_song_ytdlp = download_and_play_track


def play_shuffle() -> Dict[str, Any]:
    """
    Creates a dynamic, fully-randomized playlist (.m3u) containing all tracks from the user's library,
    loads the full playlist queue into the PC Media Player, enables shuffle mode, and begins playback.
    This ensures continuous shuffle playback where the next song plays automatically instead of stopping.
    """
    import glob
    import random
    import threading

    tracks = scan_local_music(max_results=1000)
    valid_tracks = [t for t in tracks if t.get("size_mb", 0) > 0.5] or tracks
    if not valid_tracks:
        return {"status": "error", "message": "No music files found on your PC."}

    # Fully randomize all tracks for continuous shuffle order
    shuffled_tracks = list(valid_tracks)
    random.shuffle(shuffled_tracks)

    _stop_dj_playback()

    # 1. If Standalone DJ Engine is running on PC Speakers, route shuffle directly to it
    dj_res = send_standalone_dj_action("shuffle")
    if dj_res and dj_res.get("status") == "success":
        curr = dj_res.get("current_track") or {}
        q_cnt = dj_res.get("queue_count", len(valid_tracks))
        set_last_played_track(curr, is_playing=True)
        return {
            "status": "success",
            "message": f"🎧 DJ Shuffle active: Mixing {q_cnt} songs with seamless crossfades on PC Speakers.",
            "track": curr,
            "queue_count": q_cnt,
        }

    # Save to a dedicated shuffle playlist in the user's Music folder (PC Speakers)
    music_dir = os.path.expanduser(r"~\Music")
    os.makedirs(music_dir, exist_ok=True)
    playlist_path = os.path.join(music_dir, "Cockpit_Shuffle_Queue.m3u")

    try:
        with open(playlist_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for t in shuffled_tracks:
                f.write(f"#EXTINF:-1,{t.get('title', '')}\n")
                f.write(f"{t['path']}\n")
    except Exception as e:
        print(f"[LocalMusic] Error writing shuffle playlist: {e}")
        # Fallback to single track if playlist write fails
        selected = shuffled_tracks[0]
        res = play_track(selected["path"])
        res["track"] = selected
        return res

    launched = False

    # 1. Try launching via Windows 11 Media Player executable directly
    zune_exe_pattern = r"C:\Program Files\WindowsApps\Microsoft.ZuneMusic_*\Microsoft.Media.Player.exe"
    zune_exes = glob.glob(zune_exe_pattern)
    if zune_exes and os.path.exists(zune_exes[0]):
        try:
            subprocess.Popen([zune_exes[0], playlist_path])
            launched = True
        except Exception:
            pass

    # 2. Universal fallback to os.startfile / Start-Process
    if not launched:
        try:
            os.startfile(playlist_path)
            launched = True
        except Exception:
            try:
                cmd = f'Start-Process -FilePath "{playlist_path}"'
                subprocess.Popen(["powershell.exe", "-NoProfile", "-Command", cmd])
                launched = True
            except Exception as e2:
                print(f"[LocalMusic] Failed to launch playlist: {e2}")

    # Activate SMTC shuffle mode on the session asynchronously
    def _activate_smtc_shuffle():
        import time

        time.sleep(1.2)
        try:
            import asyncio
            from winsdk.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MediaManager,
            )

            async def _smtc():
                manager = await MediaManager.request_async()
                for s in manager.get_sessions():
                    app_id = (s.source_app_user_model_id or "").lower()
                    if "zune" in app_id or "media" in app_id or "music" in app_id:
                        await s.try_change_shuffle_active_async(True)

            asyncio.run(_smtc())
        except Exception:
            pass

    threading.Thread(target=_activate_smtc_shuffle, daemon=True).start()

    first_track = shuffled_tracks[0]
    set_last_played_track(first_track, is_playing=True)
    return {
        "status": "success",
        "message": f"Playing {len(shuffled_tracks)} songs on shuffle in your PC Music Player (PC Speakers).",
        "track": first_track,
        "queue_count": len(shuffled_tracks),
        "playlist_path": playlist_path,
        "filename": first_track["filename"],
        "path": first_track["path"],
    }


def control_media(action: str) -> bool:
    """
    Controls Windows media playback using a tri-layer approach:
    1. Direct DJ Crossfade Dual-Deck Player if DJ mode is active.
    2. Direct Windows System Media Transport Controls (SMTC via winsdk) for Windows Media Player, Groove, Spotify, etc.
    3. Windows Extended Multimedia Virtual Keycodes (ctypes keybd_event) for Win32 apps and universal fallback.
    Actions supported: 'pause', 'play', 'play_pause', 'toggle', 'next', 'prev', 'stop', 'mute', 'vol_up', 'vol_down', 'toggle_dj', 'enable_dj', 'disable_dj'
    """
    import time

    action = (action or "").lower().strip()
    if action == "toggle":
        action = "play_pause"

    if action in ("toggle_dj", "enable_dj", "disable_dj"):
        return True

    # 1. First route control directly to Standalone DJ Engine if running on PC Speakers
    dj_res = send_standalone_dj_action(action)
    if dj_res and dj_res.get("status") == "success":
        return True

    if action == "shuffle":
        play_shuffle()
        return True

    if action == "pause":
        _LAST_PLAYED_TRACK["is_playing"] = False
    elif action in ("play", "unpause"):
        _LAST_PLAYED_TRACK["is_playing"] = True
    elif action in ("play_pause", "toggle"):
        _LAST_PLAYED_TRACK["is_playing"] = not _LAST_PLAYED_TRACK.get("is_playing", False)

    smtc_success = False
    try:
        import asyncio
        from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

        async def _do_smtc():
            nonlocal smtc_success
            manager = await MediaManager.request_async()
            sessions = manager.get_sessions()
            target_sessions = []
            for s in sessions:
                app_id = (s.source_app_user_model_id or "").lower()
                if any(
                    k in app_id
                    for k in [
                        "zune", "music", "media", "player", "spotify",
                        "vlc", "foobar", "aimp", "itunes", "winamp",
                    ]
                ):
                    target_sessions.append(s)
            if not target_sessions:
                curr = manager.get_current_session()
                if curr:
                    target_sessions.append(curr)
                elif sessions:
                    target_sessions.extend(sessions)

            for s in target_sessions:
                try:
                    if action == "pause":
                        res = await s.try_pause_async()
                    elif action == "play":
                        res = await s.try_play_async()
                    elif action in ("play_pause", "toggle"):
                        res = await s.try_toggle_play_pause_async()
                    elif action == "next":
                        res = await s.try_skip_next_async()
                    elif action in ("prev", "previous"):
                        res = await s.try_skip_previous_async()
                    elif action == "stop":
                        res = await s.try_stop_async()
                    else:
                        res = False
                    if res:
                        smtc_success = True
                except Exception:
                    pass

        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(lambda: asyncio.run(_do_smtc())).result(timeout=0.6)
        except Exception:
            pass
    except Exception as e:
        print(f"[LocalMusic Engine] SMTC Error: {e}")

    try:
        import ctypes

        KEYEVENTF_EXTENDEDKEY = 0x0001
        KEYEVENTF_KEYUP = 0x0002
        vk_map = {
            "pause": 0xB3,      # VK_MEDIA_PLAY_PAUSE
            "play": 0xB3,
            "play_pause": 0xB3,
            "toggle": 0xB3,
            "next": 0xB0,       # VK_MEDIA_NEXT_TRACK
            "prev": 0xB1,       # VK_MEDIA_PREV_TRACK
            "stop": 0xB2,       # VK_MEDIA_STOP
            "vol_up": 0xAF,     # VK_VOLUME_UP
            "vol_down": 0xAE,   # VK_VOLUME_DOWN
            "mute": 0xAD,       # VK_VOLUME_MUTE
        }
        vk = vk_map.get(action)
        if vk:
            ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.04)
            ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"[LocalMusic Engine] Key event error: {e}")

    return smtc_success


def get_media_status() -> dict[str, Any]:
    """Returns current playback telemetry for the Cockpit Media API."""
    # 1. If Standalone DJ Engine is running, return its live telemetry directly
    dj_stat = query_standalone_dj_status()
    if dj_stat:
        curr = dj_stat.get("current_track") or _LAST_PLAYED_TRACK
        return {
            "dj_mode": True,
            "is_playing": dj_stat.get("is_playing", False),
            "paused": dj_stat.get("is_paused", False),
            "is_crossfading": dj_stat.get("is_crossfading", False),
            "deck": dj_stat.get("active_deck", "Deck A"),
            "current_track": curr,
            "progress": dj_stat.get("progress_seconds", 0.0),
            "duration": dj_stat.get("duration_seconds", 0.0),
            "volume": dj_stat.get("volume", 0.85),
            "queue_count": dj_stat.get("queue_count", 0),
            "target_device": dj_stat.get("target_device", "Speakers (2- Realtek(R) Audio)"),
        }

    # 2. Query SMTC from Windows Media Player / Windows media session
    smtc_track = None
    is_playing = None
    try:
        import asyncio
        from winsdk.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        )

        async def _query():
            manager = await MediaManager.request_async()
            session = manager.get_current_session()
            if not session:
                sessions = manager.get_sessions()
                if sessions:
                    session = sessions[0]
            if session:
                props = await session.try_get_media_properties_async()
                info = session.get_playback_info()
                status = str(info.playback_status) if info else ""
                playing = "Playing" in status
                if props and props.title:
                    return {
                        "title": props.title,
                        "artist": props.artist or "Windows Media Player",
                        "album": props.album_title or "",
                        "is_playing": playing,
                    }
                elif status:
                    return {
                        "title": _LAST_PLAYED_TRACK.get("title", "Windows Media Player"),
                        "artist": _LAST_PLAYED_TRACK.get("artist", "PC Speakers"),
                        "album": "",
                        "is_playing": playing,
                    }
            return None

        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                smtc_track = pool.submit(lambda: asyncio.run(_query())).result(timeout=0.5)
        except Exception:
            smtc_track = None

        if smtc_track:
            is_playing = smtc_track.get("is_playing", False)
    except Exception:
        pass

    # Use SMTC track if found, otherwise fall back to _LAST_PLAYED_TRACK
    track_info = smtc_track or _LAST_PLAYED_TRACK
    playing_state = is_playing if (smtc_track is not None and "is_playing" in smtc_track) else _LAST_PLAYED_TRACK.get("is_playing", False)

    return {
        "dj_mode": False,
        "is_playing": playing_state,
        "paused": not playing_state,
        "deck": "PC Speakers",
        "current_track": track_info,
        "progress": 0.0,
        "duration": 0.0,
        "volume": 1.0,
        "queue_count": 0,
        "target_device": "PC Speakers (Realtek)",
    }


