import ctypes
import datetime
import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import webbrowser

# Optional third-party libraries (gracefully handled)
try:
    import psutil
except ImportError:
    psutil = None

try:
    import pycaw.pycaw as pc
except ImportError:
    pc = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

try:
    import winsound
except ImportError:
    winsound = None


def play_success_beep():
    if winsound:
        try:
            winsound.Beep(523, 100)
            winsound.Beep(659, 100)
            winsound.Beep(784, 220)
        except Exception:
            pass


def play_error_beep():
    if winsound:
        try:
            winsound.Beep(220, 150)
            winsound.Beep(175, 300)
        except Exception:
            pass


def press_key(vk_code):
    try:
        flags = KEYEVENTF_EXTENDEDKEY if (0xAD <= vk_code <= 0xB3) else 0
        ctypes.windll.user32.keybd_event(vk_code, 0, flags, 0)
        time.sleep(0.04)
        ctypes.windll.user32.keybd_event(vk_code, 0, flags | KEYEVENTF_KEYUP, 0)

        # Dual-layer SMTC transport control
        import local_music_engine
        if vk_code == VK_MEDIA_PLAY_PAUSE:
            local_music_engine.control_media("play_pause")
        elif vk_code == VK_MEDIA_NEXT_TRACK:
            local_music_engine.control_media("next")
        elif vk_code == VK_MEDIA_PREV_TRACK:
            local_music_engine.control_media("prev")
        elif vk_code == VK_MEDIA_STOP:
            local_music_engine.control_media("stop")
    except Exception:
        pass


def get_playback_devices(target_type=None):
    """
    Returns active playback devices filtered by target_type:
    'speaker' -> PC speakers / built-in audio
    'headphone' -> Headphones, headsets, earphones
    None or 'all' -> All active playback devices
    """
    if not pc:
        return []
    devs = []
    try:
        for d in pc.AudioUtilities.GetAllDevices():
            if d.state == pc.AudioDeviceState.Active and d.FriendlyName:
                low = d.FriendlyName.lower()
                # Skip input/recording devices
                if any(bad in low for bad in ["mic", "microphone", "input", "line in", "stereo mix"]):
                    continue
                if target_type in ["speaker", "pc"]:
                    if ("speaker" in low or "realtek" in low) and not any(h in low for h in ["head", "earphone", "phone"]):
                        devs.append(d)
                elif target_type in ["headphone", "headset"]:
                    if any(h in low for h in ["headphone", "headset", "earphone", "phone", "bh71", "usb audio"]):
                        devs.append(d)
                else:
                    devs.append(d)
    except Exception as e:
        print(f"[EverydayActions] get_playback_devices error: {e}")
    return devs


def get_device_volume(target_type=None):
    devs = get_playback_devices(target_type)
    if devs:
        try:
            scalar = devs[0].EndpointVolume.GetMasterVolumeLevelScalar()
            return int(round(scalar * 100))
        except Exception:
            pass
    return get_master_volume()


def set_device_volume(target_type, level_percent: int):
    level_percent = max(0, min(100, int(level_percent)))
    scalar = level_percent / 100.0
    devs = get_playback_devices(target_type)
    if devs:
        for d in devs:
            try:
                d.EndpointVolume.SetMasterVolumeLevelScalar(scalar, None)
            except Exception as e:
                print(f"[EverydayActions] Error setting volume on {getattr(d, 'FriendlyName', d)}: {e}")
        return level_percent
    return set_master_volume(level_percent)


def adjust_device_volume_relative(target_type, delta_percent: int):
    current = get_device_volume(target_type)
    if current is not None:
        target = max(0, min(100, current + delta_percent))
        return set_device_volume(target_type, target)
    return adjust_volume_relative(delta_percent)


def toggle_device_mute(target_type=None):
    devs = get_playback_devices(target_type)
    if devs:
        res = []
        for d in devs:
            try:
                curr = d.EndpointVolume.GetMute()
                new_m = 0 if curr else 1
                d.EndpointVolume.SetMute(new_m, None)
                res.append(bool(new_m))
            except Exception:
                pass
        if res:
            return "muted" if any(res) else "unmuted"
    return toggle_volume_mute()


def get_master_volume():
    if pc:
        try:
            speakers = pc.AudioUtilities.GetSpeakers()
            if speakers and speakers.EndpointVolume:
                scalar = speakers.EndpointVolume.GetMasterVolumeLevelScalar()
                return int(round(scalar * 100))
        except Exception:
            pass
    return None


def set_master_volume(level_percent: int):
    level_percent = max(0, min(100, int(level_percent)))
    scalar = level_percent / 100.0
    success = False

    if pc:
        try:
            speakers = pc.AudioUtilities.GetSpeakers()
            if speakers and speakers.EndpointVolume:
                speakers.EndpointVolume.SetMasterVolumeLevelScalar(scalar, None)
                success = True
        except Exception as e:
            print(f"[EverydayActions] pycaw volume set error: {e}")

    if not success:
        # Fallback via PowerShell / WScript
        try:
            # Step down to 0 then up
            ps_script = f"""
            $obj = New-Object -ComObject WScript.Shell
            for ($i=0; $i -lt 50; $i++) {{ $obj.SendKeys([char]174) }}
            $steps = [math]::Round({level_percent} / 2)
            for ($i=0; $i -lt $steps; $i++) {{ $obj.SendKeys([char]175) }}
            """
            subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_script])
            success = True
        except Exception:
            pass

    return level_percent


def adjust_volume_relative(delta_percent: int):
    current = get_master_volume()
    if current is not None:
        target = max(0, min(100, current + delta_percent))
        set_master_volume(target)
        return target
    else:
        # Fallback using hardware keys
        steps = max(1, abs(delta_percent) // 2)
        vk = VK_VOLUME_UP if delta_percent > 0 else VK_VOLUME_DOWN
        for _ in range(steps):
            press_key(vk)
        return f"adjusted by {delta_percent}%"


def toggle_volume_mute():
    is_muted = None
    if pc:
        try:
            speakers = pc.AudioUtilities.GetSpeakers()
            if speakers and speakers.EndpointVolume:
                current_mute = speakers.EndpointVolume.GetMute()
                new_mute = 0 if current_mute else 1
                speakers.EndpointVolume.SetMute(new_mute, None)
                is_muted = bool(new_mute)
        except Exception:
            pass

    if is_muted is None:
        press_key(VK_VOLUME_MUTE)
        return "toggled"
    return "muted" if is_muted else "unmuted"


def set_screen_brightness(level_percent: int):
    level_percent = max(0, min(100, int(level_percent)))
    if sbc:
        try:
            sbc.set_brightness(level_percent)
            return level_percent
        except Exception as e:
            print(f"[EverydayActions] sbc brightness error: {e}")

    # Fallback to WMI
    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level_percent})",
            ]
        )
        return level_percent
    except Exception:
        pass
    return level_percent


def adjust_screen_brightness_relative(delta_percent: int):
    if sbc:
        try:
            current = sbc.get_brightness()
            if isinstance(current, list):
                current = current[0]
            target = max(0, min(100, int(current) + delta_percent))
            sbc.set_brightness(target)
            return target
        except Exception:
            pass
    return set_screen_brightness(max(0, min(100, 50 + delta_percent)))


def handle_everyday_command(user_prompt: str):
    """
    Executes everyday human computer use commands directly and autonomously.
    Returns (ai_response, model_tag, executed_details) or None.
    """
    if not user_prompt:
        return None

    raw_low = user_prompt.lower().strip()
    clean = re.sub(r"[\.\?\!\;]+$", "", raw_low).strip()
    norm = re.sub(
        r"^(hey|hi|hello|yo|deep|buddy|bro|please|can you|could you|would you|i want to|just|ok|okay)\s+",
        "",
        clean,
    ).strip()
    norm = re.sub(
        r"^(hey|hi|hello|yo|deep|buddy|bro|please|can you|could you|would you|i want to|just|ok|okay)\s+",
        "",
        norm,
    ).strip()
    norm = norm.replace(",", " ").strip()
    norm = re.sub(r"\s+", " ", norm)

    # Automatically clear any stuck specialized skill when an everyday command is detected!
    def clear_active_skill_quietly():
        try:
            import agent_skill_runtime

            agent_skill_runtime.clear_active_skill()
        except Exception:
            pass

    # =========================================================================
    # 1. SOUND & VOLUME CONTROLS (ABSOLUTE & RELATIVE & MUTE)
    # =========================================================================

    # Detect device target (headphone vs speaker vs master)
    is_headphone = any(w in norm for w in ["headphone", "headphones", "headset", "earphone", "earphones", "buds"])
    is_speaker = any(w in norm for w in ["speaker", "speakers", "pc", "computer", "laptop"])
    target_type = "headphone" if is_headphone else ("speaker" if is_speaker else None)
    target_label = "Headphones" if is_headphone else ("PC Speakers" if is_speaker else "Volume")

    # 1A. Mute / Unmute
    is_mute_intent = any(
        norm == w or norm.startswith(w) or norm.endswith(w)
        for w in [
            "mute", "unmute", "put pc on mute", "mute pc", "mute the pc", "put on mute",
            "mute audio", "mute system", "mute volume", "silence pc", "silence audio",
            "turn off sound", "turn off audio", "unmute pc", "unmute audio", "sound off", "sound on",
            "mute speakers", "mute speaker", "mute headphones", "mute headset",
            "unmute speakers", "unmute headphones", "unmute headset"
        ]
    ) or bool(re.search(r"\b(mute|unmute|silence)\s+(?:the\s+)?(pc|speakers?|headphones?|headset|audio|sound)\b", norm))

    if is_mute_intent:
        clear_active_skill_quietly()
        status = toggle_device_mute(target_type) if target_type else toggle_volume_mute()
        icon = "🔇" if status in ["muted", "toggled"] else "🔊"
        play_success_beep()
        return (
            f"{icon} {target_label} {status.upper()}.",
            "everyday_volume_mute",
            [
                {
                    "language": "python",
                    "code": f"everyday_pc_actions.toggle_device_mute('{target_type}')",
                    "output": f"{target_label} status: {status}",
                }
            ],
        )

    # 1B. Advanced Device & Percentage Volume Handling
    WORD_NUMS = {
        "zero": 0, "ten": 10, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100
    }
    norm_phonetic = re.sub(r"\btwo\s+(\d+)\b", r"to \1", norm)
    norm_phonetic = re.sub(r"\btwo\s+(zero|ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b", r"to \1", norm_phonetic)
    norm_phonetic = re.sub(r"\bthat\s+speaker\b", r"set speaker", norm_phonetic)

    is_volume_related = any(w in norm_phonetic for w in [
        "volume", "sound", "louder", "quieter", "softer", "audio", "speaker", "speakers", "headphone", "headphones", "headset"
    ])

    if is_volume_related:
        val = None
        # Check explicit number
        m_num = re.search(r"(?:to|at|on|by)?\s*(\d{1,3})\s*%?", norm_phonetic)
        # Check number words
        for w, n in WORD_NUMS.items():
            if re.search(rf"\b(?:to|at|on|by)?\s*{w}\b", norm_phonetic):
                val = n
                break
        if val is None and m_num and m_num.group(1):
            val = int(m_num.group(1))

        is_by = ("by" in norm_phonetic or "+" in norm_phonetic or "-" in norm_phonetic)
        is_down = any(w in norm_phonetic for w in ["down", "decrease", "lower", "quieter", "softer", "drop", "reduce"])
        is_up = any(w in norm_phonetic for w in ["up", "increase", "raise", "louder", "boost", "turn up", "make it louder"])
        has_set_intent = any(w in norm_phonetic for w in ["to", "at", "set", "put", "change", "calibrate"])

        # 1C. Exact Volume Calibration
        if val is not None and 0 <= val <= 100 and (has_set_intent or (not is_by and not is_down and not is_up) or val > 30):
            clear_active_skill_quietly()
            final_vol = set_device_volume(target_type, val) if target_type else set_master_volume(val)
            icon = "🔇" if final_vol == 0 else ("🔉" if final_vol < 50 else "🔊")
            play_success_beep()
            return (
                f"{icon} {target_label} → **{final_vol}%**.",
                "everyday_volume_set",
                [
                    {
                        "language": "python",
                        "code": f"everyday_pc_actions.set_device_volume('{target_type}', {final_vol})",
                        "output": f"{target_label} calibrated to {final_vol}%",
                    }
                ],
            )

        # 1D. Relative Volume Up
        if is_up:
            clear_active_skill_quietly()
            delta = val if (is_by and val) else 10
            new_vol = adjust_device_volume_relative(target_type, delta) if target_type else adjust_volume_relative(delta)
            play_success_beep()
            return (
                f"🔊 {target_label} +{delta}% → **{new_vol}%**.",
                "everyday_volume_up",
                [
                    {
                        "language": "python",
                        "code": f"everyday_pc_actions.adjust_device_volume_relative('{target_type}', +{delta})",
                        "output": f"{target_label} increased to {new_vol}%",
                    }
                ],
            )

        # 1E. Relative Volume Down
        if is_down:
            clear_active_skill_quietly()
            delta = val if (is_by and val) else 10
            new_vol = adjust_device_volume_relative(target_type, -delta) if target_type else adjust_volume_relative(-delta)
            play_success_beep()
            return (
                f"🔉 {target_label} -{delta}% → **{new_vol}%**.",
                "everyday_volume_down",
                [
                    {
                        "language": "python",
                        "code": f"everyday_pc_actions.adjust_device_volume_relative('{target_type}', -{delta})",
                        "output": f"{target_label} reduced to {new_vol}%",
                    }
                ],
            )

    # =========================================================================
    # 2. SCREEN BRIGHTNESS CONTROLS
    # =========================================================================

    # 2A. Set Brightness to Exact Percentage
    m_bright_exact = re.search(
        r"(?:set|change|put|turn|adjust)?\s*(?:the\s+)?(?:screen\s+|display\s+)?brightness\s+(?:to\s+|at\s+|on\s+)?(\d{1,3})\s*%?",
        norm,
    )
    if not m_bright_exact:
        m_bright_exact = re.search(
            r"brightness\s*(?:to\s+|at\s+|on\s+)?(\d{1,3})\s*%?", norm
        )

    if m_bright_exact:
        b_val = int(m_bright_exact.group(1))
        if 0 <= b_val <= 100:
            clear_active_skill_quietly()
            final_b = set_screen_brightness(b_val)
            play_success_beep()
            return (
                f"🖥️ Brightness → **{final_b}%**.",
                "everyday_brightness_set",
                [
                    {
                        "language": "python",
                        "code": f"everyday_pc_actions.set_screen_brightness({final_b})",
                        "output": f"Display brightness calibrated to {final_b}%",
                    }
                ],
            )

    if any(
        norm == w or norm.startswith(w)
        for w in [
            "increase brightness",
            "raise brightness",
            "brightness up",
            "brighter",
            "make screen brighter",
        ]
    ):
        clear_active_skill_quietly()
        res_b = adjust_screen_brightness_relative(15)
        play_success_beep()
        return (
            f"☀️ Brightness boosted → **{res_b}%**.",
            "everyday_brightness_up",
            [
                {
                    "language": "python",
                    "code": "everyday_pc_actions.adjust_screen_brightness_relative(+15)",
                    "output": f"Brightness updated to {res_b}%",
                }
            ],
        )
    if any(
        norm == w or norm.startswith(w)
        for w in [
            "decrease brightness",
            "lower brightness",
            "brightness down",
            "dim screen",
            "dim display",
            "make screen dimmer",
            "darker",
        ]
    ):
        clear_active_skill_quietly()
        res_b = adjust_screen_brightness_relative(-15)
        play_success_beep()
        return (
            f"🌙 Brightness dimmed → **{res_b}%**.",
            "everyday_brightness_down",
            [
                {
                    "language": "python",
                    "code": "everyday_pc_actions.adjust_screen_brightness_relative(-15)",
                    "output": f"Brightness reduced to {res_b}%",
                }
            ],
        )

    # =========================================================================
    # 2C. WORKSTATION SETTINGS & COMMANDER CONFIGURATION OVERVIEW
    # =========================================================================
    if any(
        k in norm
        for k in [
            "where those settings went",
            "where are my settings",
            "where did my settings go",
            "where did those settings go",
            "where did the settings go",
            "where did all my settings go",
            "what did we set earlier",
            "we set these things earlier",
            "where are those settings",
            "show settings",
            "my settings",
            "workstation settings",
            "who am i",
            "what is my name",
            "system settings",
            "check settings",
            "settings status",
            "all my settings",
            "what settings",
            "my permissions",
            "commander profile",
            "who is commander",
        ]
    ):
        clear_active_skill_quietly()
        return (
            "⚙️ **Workstation Settings & System Configuration Overview**\n\n"
            "Below is a concise snapshot of your current configuration, identity, security policies, and active subsystems.\n\n"
            "### 👤 Commander Identity\n"
            f"- **Name:** {os.getenv('OPERATOR_NAME', 'Workstation Commander')}\n"
            "- **Role:** Chief Systems Commander & AI Engineer\n"
            "- **Status:** Verified Authorized Commander\n\n"
            "### 🛡️ Permissions Policy\n"
            "- **Host OS Execution:** ✅ Full access (Python, PowerShell, Win32 APIs, app launch, file I/O, volume & brightness control).\n"
            "- **Registry:** 🛡️ Blocked – no registry edits allowed.\n"
            "- **Privacy & Data Egress:** 🛡️ Blocked – no outbound data uploads.\n\n"
            "### 👁️ MediaPipe Vision & Kinematics\n"
            "- **Hand Tracking:** MediaPipe Hands – 21 3D landmarks (active).\n"
            "- **Face Mesh:** MediaPipe Face Mesh – 468 points (active).\n"
            "- **Portal:** [/camera_vision](http://127.0.0.1:5000/camera_vision)\n\n"
            "### 📑 Subsystem Portals\n"
            "1️⃣ **Face Emotion & Hand Gestures** – Live 3D Kinematics\n"
            "2️⃣ **Weather Radar** – Real‑time forecasts\n"
            "3️⃣ **Sharemarket & Trading** – Live market data\n"
            "4️⃣ **News Wire** – Global headlines\n"
            "5️⃣ **Jobs by Location** – IT & field career listings\n"
            "6️⃣ **Skills Arsenal (422)** – Developer tools & agents\n"
            "7️⃣ **Cyber Defense** – Security hardening dashboard\n"
            "8️⃣ **Memory Database** – Persistent knowledge store\n\n"
            "### 🔊 Everyday PC Controls\n"
            "- **Volume:** 0‑100 % scalar, mute/unmute, relative adjustments.\n"
            "- **Brightness:** 0‑100 % via WMI.\n"
            "- **Launchers:** Calculator, Notepad, Snipping Tool, Task Manager, Settings, Explorer, Chrome.\n"
            "- **Folders:** Downloads, Documents, Desktop, Pictures, Videos, Music, C:\\\n\n"
            "*All settings persist in `memory.db` and remain active across sessions.*",
            "workstation_settings_overview",
            [
                {
                    "language": "markdown",
                    "code": "WORKSTATION_SETTINGS_AUDIT",
                    "output": f"Commander: {os.getenv('OPERATOR_NAME', 'Workstation Commander')} | Policy: Full PC Access (Registry/Egress Blocked) | Subsystems: 8 Pages Active",
                }
            ],
        )

    # =========================================================================
    # 2D. YOUTUBE, SONGS, MEDIA PLAYBACK & WEB BROWSING (COCKPIT POWER)
    # =========================================================================

    # 1. Hardware Media Controls (Play / Pause / Next / Prev / Volume) - HIGHEST PRIORITY
    if norm in [
        "pause",
        "pause music",
        "pause the music",
        "pause song",
        "pause the song",
        "stop music",
        "stop the music",
        "stop song",
        "stop playback",
        "pause playback",
        "bars",
        "both music",
        "boss music",
        "bar music",
        "buzz music",
        "paws music",
        "cause music",
        "gana roko",
        "gana rok do",
        "gana band karo",
    ] or re.search(r"^(?:pause|stop)\s+(?:music|the\s+music|song|playback)$", norm):
        import local_music_engine
        local_music_engine.control_media("pause")
        play_success_beep()
        return (
            "⏸️ Music paused in your PC Media Player.",
            "everyday_media_pause",
            [
                {
                    "language": "powershell",
                    "code": "GlobalSystemMediaTransportControls: Pause",
                    "output": "Media Paused",
                }
            ],
        )

    if norm in [
        "play",
        "resume",
        "resume music",
        "resume song",
        "unpause",
        "unpause music",
        "continue music",
        "gana chalao",
        "gana shuru karo",
    ] or re.search(r"^(?:resume|unpause)\s+(?:music|song|playback)$", norm):
        import local_music_engine
        local_music_engine.control_media("play")
        play_success_beep()
        return (
            "▶️ Music resumed in your PC Media Player.",
            "everyday_media_play",
            [
                {
                    "language": "powershell",
                    "code": "GlobalSystemMediaTransportControls: Play",
                    "output": "Media Resumed",
                }
            ],
        )

    if norm in [
        "play or pause",
        "play pause",
        "pause or play",
        "toggle music",
    ] or re.search(r"^(?:play\s+or\s+pause|pause\s+or\s+play)$", norm):
        import local_music_engine
        local_music_engine.control_media("play_pause")
        play_success_beep()
        return (
            "⏯️ Media playback toggled.",
            "everyday_media_toggle",
            [
                {
                    "language": "powershell",
                    "code": "GlobalSystemMediaTransportControls: Toggle",
                    "output": "Media Play/Pause",
                }
            ],
        )
    if norm in [
        "play next",
        "next song",
        "next track",
        "skip song",
        "skip track",
        "next",
        "skip",
        "play the next",
        "the next",
        "forward track",
    ]:
        press_key(VK_MEDIA_NEXT_TRACK)
        play_success_beep()
        return (
            "⏭️ Next track skipped.",
            "everyday_media_next",
            [
                {
                    "language": "powershell",
                    "code": "keybd_event(VK_MEDIA_NEXT_TRACK)",
                    "output": "Next Track",
                }
            ],
        )
    if norm in [
        "play prev",
        "play previous",
        "previous song",
        "prev song",
        "previous track",
        "prev track",
        "previous",
        "prev",
        "play the previous",
        "the previous",
        "in previous",
        "rewind",
    ]:
        press_key(VK_MEDIA_PREV_TRACK)
        play_success_beep()
        return (
            "⏮️ Previous track skipped.",
            "everyday_media_prev",
            [
                {
                    "language": "powershell",
                    "code": "keybd_event(VK_MEDIA_PREV_TRACK)",
                    "output": "Previous Track",
                }
            ],
        )
    if norm in ["stop music", "stop song", "stop playback"]:
        press_key(VK_MEDIA_STOP)
        play_success_beep()
        return (
            "⏹️ Media playback stopped.",
            "everyday_media_stop",
            [
                {
                    "language": "powershell",
                    "code": "keybd_event(VK_MEDIA_STOP)",
                    "output": "Media Stopped",
                }
            ],
        )

    # 2A-0. DJ Crossfade Mode Commands
    is_dj_disable_cmd = any(
        k in norm for k in ["disable dj", "turn off dj", "stop dj", "exit dj", "dj off", "turn off crossfade"]
    )
    is_dj_enable_cmd = not is_dj_disable_cmd and any(
        k in norm for k in ["dj mode", "enable dj", "start dj", "dj mix", "crossfade mode", "turn on dj", "dj crossfade", "dj on"]
    )
    if is_dj_enable_cmd or is_dj_disable_cmd:
        clear_active_skill_quietly()
        try:
            import local_music_engine
            new_state = local_music_engine.toggle_dj_mode(True if is_dj_enable_cmd else False)
            play_success_beep()
            if new_state:
                return (
                    "🎧 **DJ Crossfade Dual-Deck Mode Activated!**\n\n"
                    "Tracks will now blend smoothly from Deck A to Deck B with 3.5-second club crossfades, automatic end-of-track mixing, and zero silence gaps.\n\n"
                    "• Say *'play music on shuffle'* to launch a seamless DJ mix set.\n"
                    "• Say *'next song'* to trigger an immediate crossfade transition.",
                    "dj_mode_enabled",
                    [{"type": "dj_mode", "status": "active"}]
                )
            else:
                return (
                    "🎧 **DJ Crossfade Mode Disabled.** Switched back to standard Windows PC Media Player.",
                    "dj_mode_disabled",
                    [{"type": "dj_mode", "status": "inactive"}]
                )
        except Exception as e:
            return (f"DJ Mode Error: {e}", "dj_mode_error", [])

    # 2A. Local Music Playback, Shuffle & Scan (Highest Media Priority)
    is_shuffle_music_cmd = (
        norm in [
            "play music on shuffle", "play music in shuffle", "play music shuffle",
            "play songs on shuffle", "play song on shuffle", "play track on shuffle",
            "play tracks on shuffle", "play on shuffle", "shuffle music",
            "shuffle songs", "shuffle song", "shuffle track", "shuffle tracks",
            "shuffle my music", "shuffle local music", "music on shuffle",
            "songs on shuffle", "shuffle play", "play random song", "play random music",
            "play random track", "play random songs", "random music", "random song",
            "ਲੋਕਲ ਗਾਣਾ ਸ਼ਫਲ ਕਰੋ", "gana shuffle te chalao", "shuffle te gana chalao"
        ]
        or bool(re.search(r"\bshuffle\b", norm) and any(w in norm for w in ["music", "song", "track", "gana", "play"]))
        or bool(re.search(r"^(?:play|listen\s+to)\s+(?:a\s+)?(?:random\s+)?(?:local\s+|my\s+|pc\s+)?(?:music|song|track)s?\s+(?:on|in)\s+shuffle$", norm))
        or bool(re.search(r"^(?:play|listen\s+to)\s+(?:a\s+)?random\s+(?:music|song|track)s?$", norm))
    )
    if is_shuffle_music_cmd:
        clear_active_skill_quietly()
        try:
            import local_music_engine
            res = local_music_engine.play_shuffle()
            if res and res.get("status") == "success" and "track" in res:
                track = res["track"]
                queue_count = res.get("queue_count", 1)
                play_success_beep()
                return (
                    f"🔀 **Playing on Shuffle:** {track['title']} (`{track['filename']}`) with **{queue_count} songs** in continuous queue.\n\n"
                    f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                    f'  <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                    f'    <span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">🔀 {track["title"]}</span>'
                    f'    <span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">Queue: {queue_count} songs</span>'
                    f'  </header>'
                    f'  <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                    f'    <span>▶️ Playing in your PC Music Player (Continuous Shuffle Active)</span>'
                    f'  </div>'
                    f'</div>',
                    "play_music_shuffle",
                    [
                        {
                            "language": "powershell",
                            "code": f'Start-Process -FilePath "{track["path"]}"',
                            "output": f"Playing {track['filename']} on shuffle",
                        },
                        {
                            "type": "local_audio_player",
                            "path": track["path"],
                            "title": track["title"],
                        }
                    ],
                )
            else:
                return (
                    "No audio files found to shuffle. Place your songs (.mp3, .wav, .flac) in `C:\\Users\\User\\Music`!",
                    "no_music_found",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Music player error: {e}", "music_error", [])

    is_local_music_cmd = (
        norm in [
            "play local music", "play local song", "play music on my pc",
            "play song on my pc", "play pc music", "play offline music",
            "play my music", "ਲੋਕਲ ਗਾਣਾ ਚਲਾਓ", "local gana chalao", "pc te gana chalao"
        ]
        or bool(re.search(r"^(?:play|listen\s+to)\s+(?:my\s+|local\s+|offline\s+|pc\s+)(?:music|songs?)$", norm))
    )
    if is_local_music_cmd:
        clear_active_skill_quietly()
        try:
            import local_music_engine
            track = local_music_engine.find_track("")
            if track:
                local_music_engine.play_track(track["path"])
                play_success_beep()
                return (
                    f"🎵 **Playing Local Music:** {track['title']} (`{track['filename']}`) in your default media player.\n\n"
                    f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                    f'  <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                    f'    <span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">🎵 {track["title"]}</span>'
                    f'    <span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">{track["size_mb"]} MB</span>'
                    f'  </header>'
                    f'  <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                    f'    <span>▶️ Playing in your PC Music Player</span>'
                    f'  </div>'
                    f'</div>',
                    "play_local_music",
                    [
                        {
                            "language": "powershell",
                            "code": f'Start-Process -FilePath "{track["path"]}"',
                            "output": f"Playing {track['filename']}",
                        },
                        {
                            "type": "local_audio_player",
                            "path": track["path"],
                            "title": track["title"],
                        }
                    ],
                )
            else:
                return (
                    "No audio files found. Place your songs (.mp3, .wav, .flac) in `C:\\Users\\User\\Music`!",
                    "no_music_found",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Music player error: {e}", "music_error", [])

    m_play_local_specific = re.search(
        r"^(?:play\s+local\s+song|play\s+local\s+track|play\s+song\s+locally|play\s+track\s+locally)\s+(.+)$", norm
    )
    if m_play_local_specific and not any(k in norm for k in ["youtube", "on youtube", "video"]):
        song_name = m_play_local_specific.group(1).strip()
        clear_active_skill_quietly()
        try:
            import local_music_engine
            track = local_music_engine.find_track(song_name)
            if track:
                local_music_engine.play_track(track["path"])
                play_success_beep()
                return (
                    f"🎵 **Playing Local Song:** {track['title']} (`{track['filename']}`) in your default media player.\n\n"
                    f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                    f'  <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                    f'    <span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">🎵 {track["title"]}</span>'
                    f'    <span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">{track["size_mb"]} MB</span>'
                    f'  </header>'
                    f'  <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                    f'    <span>▶️ Playing in your PC Music Player</span>'
                    f'  </div>'
                    f'</div>',
                    "play_local_song",
                    [
                        {
                            "language": "powershell",
                            "code": f'Start-Process -FilePath "{track["path"]}"',
                            "output": f"Playing {track['filename']}",
                        },
                        {
                            "type": "local_audio_player",
                            "path": track["path"],
                            "title": track["title"],
                        }
                    ],
                )
            else:
                download_res = local_music_engine.download_and_play_track(song_name)
                if download_res.get("status") == "success":
                    play_success_beep()
                    return (
                        f"🎵 **Downloaded & Playing in PC Music Player:** {download_res['title']} (`{download_res['filename']}`)\n\n"
                        f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                        f'  <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                        f'    <span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">⬇️ {download_res["title"]}</span>'
                        f'    <span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">{download_res.get("size_mb", 0)} MB • Downloaded</span>'
                        f'  </header>'
                        f'  <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                        f'    <span>▶️ Playing in your default PC Music Player</span>'
                        f'  </div>'
                        f'</div>',
                        "download_and_play_song",
                        [
                            {
                                "language": "powershell",
                                "code": f'Start-Process -FilePath "{download_res["path"]}"',
                                "output": f"Playing {download_res['filename']}",
                            },
                            {
                                "type": "local_audio_player",
                                "path": download_res["path"],
                                "title": download_res["title"],
                            }
                        ],
                    )
                else:
                    return (
                        f"Could not find or download '{song_name}' to local music: {download_res.get('message', 'Download error')}",
                        "download_error",
                        [],
                    )
        except Exception as e:
            return (f"⚠️ Music player error: {e}", "music_error", [])

    # 2B. YouTube & Specific Online Song Search & Playback
    # Strictly exclude conversational phrases, games, sports, and daily activities
    conversational_play_words = [
        "football", "soccer", "chess", "cricket", "basketball", "tennis",
        "badminton", "hockey", "baseball", "volleyball", "rugby", "golf",
        "video game", "video games", "board game", "cards", "poker",
        "with my friend", "with friends", "with my friends", "outside", "a game"
    ]
    is_conversational_play = (
        bool(re.search(r"\b(?:i|we|they|you|he|she)\s+play\b", norm))
        or (any(w in norm for w in conversational_play_words) and not any(y in norm for y in ["youtube", "on youtube", "song", "track", "music video"]))
        or norm.startswith("today ")
        or "how to play" in norm
        or "how do you play" in norm
        or "let's play" in norm
        or "can we play" in norm
        or "want to play" in norm
    )

    # 2B. Music, Song & Video / YouTube Dispatcher
    # Strictly separates:
    # 1. Explicit YouTube / Video requests -> Opened directly in Google Chrome application (NO UI iframes)
    # 2. General Song / Music requests without YouTube -> Checked locally first; if missing, downloaded via yt-dlp to C:\Users\User\Music and played in default PC media player
    if not is_conversational_play:
        # Check if user explicitly asked for YouTube or video
        is_explicit_youtube = any(
            k in norm for k in [
                "youtube", "you tube", "on youtube", "in youtube", "open in youtube",
                "from youtube", "youtube pe", "youtube te", "on you do", "on you two", "only you do"
            ]
        )
        is_video_request = bool(re.search(r"\b(?:video|music\s+video)\b", norm))

        explicit_yt_query = None

        if is_explicit_youtube or is_video_request:
            # Match explicit YouTube / Video patterns
            # 1) "open youtube and play ...", "open in youtube ...", "search youtube for ..."
            m_explicit_yt = re.search(
                r"^(?:open\s+(?:in\s+)?youtube\s+(?:and\s+play\s+)?(?:song\s+|video\s+)?|search\s+youtube\s+for\s+|search\s+on\s+youtube\s+for\s+)(.+)$",
                norm,
            )
            if m_explicit_yt:
                explicit_yt_query = m_explicit_yt.group(1).strip()
            # 2) "play/open <query> on/in/from youtube" or "<query> on/in youtube"
            elif any(k in norm for k in ["on youtube", "in youtube", "from youtube", "at youtube", "youtube pe"]):
                m_on_in_yt = re.search(r"^(?:play\s+|open\s+|launch\s+|listen\s+to\s+)?(.+?)\s+(?:on|in|from|at|pe)\s+youtube$", norm)
                if m_on_in_yt:
                    explicit_yt_query = m_on_in_yt.group(1).strip()
            # 3) "play/open youtube video <query>" or "play/open youtube song <query>" or "play youtube <query>"
            elif re.search(r"^(?:play|open|launch)\s+youtube\s+(?:video|song|track|music)?\s*(.+)$", norm):
                m_yt_prefix = re.search(r"^(?:play|open|launch)\s+youtube\s+(?:video|song|track|music)?\s*(.+)$", norm)
                explicit_yt_query = m_yt_prefix.group(1).strip()
            # 4) "play video <query>" or "play the video of <query>"
            elif re.search(r"^play\s+(?:the\s+)?video\s+(?:of\s+)?(.+)$", norm):
                m_vid = re.search(r"^play\s+(?:the\s+)?video\s+(?:of\s+)?(.+)$", norm)
                explicit_yt_query = m_vid.group(1).strip()
            # 5) Generic fallback if youtube in norm
            elif "youtube" in norm:
                cand = re.sub(r"\b(?:on\s+youtube|in\s+youtube|open\s+in\s+youtube|from\s+youtube|open\s+youtube\s+and\s+play|open\s+youtube|youtube)\b", "", norm).strip()
                cand = re.sub(r"^(?:play|open|launch)\s+(?:the\s+)?(?:song\s+by|song|track|music|video)?\s*", "", cand).strip()
                if cand:
                    explicit_yt_query = cand

            if explicit_yt_query:
                clear_active_skill_quietly()
                song_query = re.sub(r"^(?:this\s+)?(?:song\s+by|song|track|music|video\s+of|video)\s+", "", explicit_yt_query, flags=re.I).strip()
                if not song_query or song_query in ["a song", "song", "music", "some music", "video"]:
                    song_query = "trending music"

                search_query_encoded = urllib.parse.quote_plus(song_query)
                search_url = f"https://www.youtube.com/results?search_query={search_query_encoded}"
                watch_url = search_url
                try:
                    req = urllib.request.Request(
                        search_url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                    )
                    with urllib.request.urlopen(req, timeout=3.5) as resp:
                        html = resp.read().decode("utf-8", errors="ignore")
                        v_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                        if v_matches:
                            vid_id = v_matches[0]
                            watch_url = f"https://www.youtube.com/watch?v={vid_id}"
                except Exception:
                    pass

                import local_music_engine
                # Launch in Google Chrome (PC Speakers) and auto-pause local DJ music
                local_music_engine.open_in_chrome(watch_url)
                play_success_beep()

                return (
                    f"▶️ **Opened YouTube in Google Chrome:** Playing **{song_query}**\n\n"
                    f'<div class="cockpit-station-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(239,68,68,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                    f'<header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                    f'<span style="font-weight:700; color:#f87171; font-size:0.95rem;">▶️ YouTube Media Player (Chrome • PC Speakers)</span>'
                    f'<span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">Google Chrome</span>'
                    f'</header>'
                    f'<p style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#fca5a5; font-weight:600; margin:0;">'
                    f'<span>🌐 Playing in Google Chrome: {song_query}</span>'
                    f'</p>'
                    f'</div>',
                    "everyday_youtube_browser",
                    [
                        {
                            "language": "browser",
                            "code": f'Start-Process "chrome.exe" "{watch_url}"',
                            "output": f"Launched YouTube in Google Chrome: {song_query}",
                        }
                    ],
                )

        else:
            # -------------------------------------------------------------
            # General Song / Music Request (WITHOUT saying open in YouTube)
            # Rule: Check local music track first; if missing, download via yt-dlp and play in local DJ engine
            # -------------------------------------------------------------
            target_song_query = None

            # Pattern 1: "play song ...", "play the song ...", "play songs by ...", "play track ...", "play music ..."
            m_song = re.search(r"^(?:play\s+(?:a\s+|the\s+)?(?:song|songs|track|tracks|music)\s+(?:by\s+)?)(.+)$", norm)
            if m_song:
                target_song_query = m_song.group(1).strip()
            # Pattern 2: "play <song> by <artist>" (e.g. "play ash by karan aujla")
            elif re.search(r"^play\s+(.+?\s+by\s+[a-zA-Z0-9\s]+)$", norm):
                m_by = re.search(r"^play\s+(.+)$", norm)
                target_song_query = m_by.group(1).strip()
            # Pattern 3: "play <artist> song"
            elif re.search(r"^play\s+(.+?)\s+(?:song|songs|track|music)$", norm):
                m_art = re.search(r"^play\s+(.+)$", norm)
                target_song_query = m_art.group(1).strip()
            # Pattern 4: Short imperative "play <name>" (1-5 words, not generic activity)
            elif re.search(r"^play\s+([a-zA-Z0-9\s\-_]+)$", norm):
                m_short = re.search(r"^play\s+([a-zA-Z0-9\s\-_]+)$", norm)
                cand = m_short.group(1).strip()
                if cand and len(cand.split()) <= 5 and cand not in [
                    "now", "again", "it", "this", "that", "game", "games", "sports", "local", "pc", "offline"
                ]:
                    target_song_query = cand

            if target_song_query:
                clear_active_skill_quietly()
                import local_music_engine

                # 1. Check local track first
                track = local_music_engine.find_track(target_song_query)
                if track:
                    local_music_engine.play_track(track["path"])
                    play_success_beep()
                    return (
                        f"🎵 **Playing Local Track:** {track['title']} (`{track['filename']}`) on PC Speakers (AutoMix).\n\n"
                        f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                        f'<header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                        f'<span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">🎵 {track["title"]}</span>'
                        f'<span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">{track["size_mb"]} MB</span>'
                        f'</header>'
                        f'<div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                        f'<span>▶️ Playing on PC Speakers (Realtek)</span>'
                        f'</div>'
                        f'</div>',
                        "play_local_song",
                        [
                            {
                                "language": "powershell",
                                "code": f'Start-Process -FilePath "{track["path"]}"',
                                "output": f"Playing {track['filename']}",
                            },
                            {
                                "type": "local_audio_player",
                                "path": track["path"],
                                "title": track["title"],
                            }
                        ],
                    )
                else:
                    # 2. Not in local library -> Download via yt-dlp to C:\Users\User\Music and play in local music player
                    download_res = local_music_engine.download_and_play_track(target_song_query)
                    if download_res.get("status") == "success":
                        play_success_beep()
                        return (
                            f"🎵 **Downloaded & Playing on PC Speakers:** {download_res['title']} (`{download_res['filename']}`)\n\n"
                            f'<div class="cockpit-audio-card" style="margin-top:10px; padding:14px 18px; background:rgba(15,23,42,0.85); border:1px solid rgba(56,189,248,0.35); border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.4);">'
                            f'<header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                            f'<span style="font-weight:700; color:#38bdf8; font-size:0.95rem;">⬇️ {download_res["title"]}</span>'
                            f'<span style="font-size:0.75rem; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 8px; border-radius:4px;">{download_res.get("size_mb", 0)} MB • Downloaded</span>'
                            f'</header>'
                            f'<div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#34d399; font-weight:600;">'
                            f'<span>▶️ Saved to Local Library & Playing on PC Speakers</span>'
                            f'</div>'
                            f'</div>',
                            "download_and_play_song",
                            [
                                {
                                    "language": "powershell",
                                    "code": f'Start-Process -FilePath "{download_res["path"]}"',
                                    "output": f"Playing {download_res['filename']}",
                                    "title": download_res["title"],
                                },
                                {
                                    "type": "local_audio_player",
                                    "path": download_res["path"],
                                    "title": download_res["title"],
                                }
                            ],
                        )
                    else:
                        return (
                            f"Could not find or download '{target_song_query}' to local music: {download_res.get('message', 'Download error')}",
                            "download_error",
                            [],
                        )

    if any(
        norm == t or norm == f"please {t}"
        for t in [
            "open youtube",
            "launch youtube",
            "youtube",
        ]
    ):
        clear_active_skill_quietly()
        yt_url = "https://www.youtube.com"
        import local_music_engine
        local_music_engine.open_in_chrome(yt_url)
        play_success_beep()
        return (
            "▶️ **Opened YouTube in Google Chrome.**",
            "everyday_youtube_open",
            [
                {
                    "language": "browser",
                    "code": f'Start-Process "chrome.exe" "{yt_url}"',
                    "output": "Opened YouTube in Google Chrome",
                }
            ],
        )

    # 2C. Cockpit Subsystems (Weather, Trading, Defense, News, Jobs, Memory, Skills, Vision)
    subsystem_map = {
        "weather": ("/weather", "Live Weather Radar Station", "🌦️"),
        "weather forecast": ("/weather", "Live Weather Radar Station", "🌦️"),
        "live weather": ("/weather", "Live Weather Radar Station", "🌦️"),
        "open weather": ("/weather", "Live Weather Radar Station", "🌦️"),
        "show weather": ("/weather", "Live Weather Radar Station", "🌦️"),
        "check weather": ("/weather", "Live Weather Radar Station", "🌦️"),
        "trading": ("/trading", "Sharemarket & Trading Station", "📈"),
        "open trading": ("/trading", "Sharemarket & Trading Station", "📈"),
        "show trading": ("/trading", "Sharemarket & Trading Station", "📈"),
        "sharemarket": ("/trading", "Sharemarket & Trading Station", "📈"),
        "stock market": ("/trading", "Sharemarket & Trading Station", "📈"),
        "stocks": ("/trading", "Sharemarket & Trading Station", "📈"),
        "cyber defense": ("/cyber_defense", "Cyber Defense Matrix", "🛡️"),
        "open cyber defense": ("/cyber_defense", "Cyber Defense Matrix", "🛡️"),
        "defense": ("/cyber_defense", "Cyber Defense Matrix", "🛡️"),
        "news": ("/news", "Global News Wire", "📰"),
        "open news": ("/news", "Global News Wire", "📰"),
        "jobs": ("/jobs", "Global Tech Career Radar", "💼"),
        "open jobs": ("/jobs", "Global Tech Career Radar", "💼"),
        "job search": ("/jobs", "Global Tech Career Radar", "💼"),
        "memory": ("/memory", "Neural Memory & Knowledge Vault", "🧠"),
        "open memory": ("/memory", "Neural Memory & Knowledge Vault", "🧠"),
        "skills": ("/skills", "422 AI Skills Arsenal", "⚡"),
        "open skills": ("/skills", "422 AI Skills Arsenal", "⚡"),
        "camera vision": ("/camera_vision", "MediaPipe 3D Kinematics Studio", "👁️"),
        "open vision": ("/camera_vision", "MediaPipe 3D Kinematics Studio", "👁️"),
        "open camera": ("/camera_vision", "MediaPipe 3D Kinematics Studio", "👁️"),
    }
    for trig, (sub_url, sub_title, sub_icon) in subsystem_map.items():
        if norm == trig or norm == f"please {trig}" or norm == f"launch {trig}":
            clear_active_skill_quietly()
            play_success_beep()
            return (
                f"{sub_icon} **Opening {sub_title}** on your Cockpit.",
                "everyday_open_subsystem",
                [
                    {
                        "type": "open_subsystem",
                        "url": sub_url,
                        "title": sub_title,
                        "icon": sub_icon
                    }
                ],
            )
    if norm in ["stop music", "stop song", "stop playback"]:
        press_key(VK_MEDIA_STOP)
        play_success_beep()
        return (
            "⏹️ Media playback stopped.",
            "everyday_media_stop",
            [
                {
                    "language": "powershell",
                    "code": "keybd_event(VK_MEDIA_STOP)",
                    "output": "Media Stopped",
                }
            ],
        )

    # 3. Google & Wikipedia Search
    google_match = re.search(
        r"(?:search\s+google\s+for\s+|google\s+search\s+|google\s+)(.+)", norm
    )
    if google_match and not norm.startswith("google chrome"):
        clear_active_skill_quietly()
        g_query = google_match.group(1).strip()
        g_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(g_query)}"
        webbrowser.open(g_url)
        play_success_beep()
        return (
            f'🔍 Searching Google for **"{g_query}"**.',
            "everyday_google_search",
            [
                {
                    "language": "browser",
                    "code": f"open '{g_url}'",
                    "output": f"Google Search for '{g_query}'",
                }
            ],
        )

    wiki_match = re.search(
        r"(?:search\s+wikipedia\s+for\s+|wikipedia\s+search\s+|wikipedia\s+)(.+)", norm
    )
    if wiki_match:
        clear_active_skill_quietly()
        w_query = wiki_match.group(1).strip()
        w_url = f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote_plus(w_query)}"
        webbrowser.open(w_url)
        play_success_beep()
        return (
            f'📖 Searching Wikipedia for **"{w_query}"**.',
            "everyday_wikipedia_search",
            [
                {
                    "language": "browser",
                    "code": f"open '{w_url}'",
                    "output": f"Wikipedia Search for '{w_query}'",
                }
            ],
        )

    # 4. Common Web Apps
    web_app_map = {
        "open github": ("https://github.com", "GitHub"),
        "open reddit": ("https://reddit.com", "Reddit"),
        "open chatgpt": ("https://chatgpt.com", "ChatGPT"),
        "open netflix": ("https://netflix.com", "Netflix"),
        "open spotify": ("https://open.spotify.com", "Spotify"),
        "open gmail": ("https://mail.google.com", "Gmail"),
    }
    for trig, (wurl, wname) in web_app_map.items():
        if norm == trig or norm == f"please {trig}":
            clear_active_skill_quietly()
            webbrowser.open(wurl)
            play_success_beep()
            return (
                f"🌐 Opening **{wname}** in your browser.",
                "everyday_webapp_open",
                [
                    {
                        "language": "powershell",
                        "code": f"start '{wurl}'",
                        "output": f"Opened {wname}",
                    }
                ],
            )

    # 5. Blender Launcher
    if norm in ["open blender", "launch blender", "blender", "start blender"]:
        clear_active_skill_quietly()
        blender_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        ]
        launched = False
        for bp in blender_paths:
            if os.path.exists(bp):
                subprocess.Popen([bp])
                launched = True
                break
        if not launched:
            subprocess.Popen(["cmd.exe", "/c", "start", "blender"], shell=True)
        play_success_beep()
        return (
            "🎨 Opening Blender 3D Suite for you.",
            "everyday_blender_open",
            [
                {
                    "language": "powershell",
                    "code": "start blender.exe",
                    "output": "Blender 3D Launched",
                }
            ],
        )

    # 6. Clean Temp Files
    if norm in [
        "clean temp files",
        "clear temp files",
        "clean temporary files",
        "clean temp",
    ]:
        clear_active_skill_quietly()
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue",
            ]
        )
        play_success_beep()
        return (
            "🧹 Temporary cache and temp files cleaned successfully.",
            "everyday_clean_temp",
            [
                {
                    "language": "powershell",
                    "code": "Remove-Item -Path $env:TEMP\\* -Recurse -Force",
                    "output": "Temp files purged",
                }
            ],
        )

    # =========================================================================
    # 3. EVERYDAY APPS LAUNCHERS (INSTANT LOCAL EXECUTION)
    # =========================================================================

    app_registry = [
        (
            [
                "open calculator",
                "launch calculator",
                "calculator",
                "calc",
                "open calc",
                "start calculator",
            ],
            "calc.exe",
            "🧮 Calculator",
        ),
        (
            [
                "open notepad",
                "launch notepad",
                "notepad",
                "open text editor",
                "text editor",
                "start notepad",
            ],
            "notepad.exe",
            "📝 Notepad",
        ),
        (
            [
                "take screenshot",
                "take a screenshot",
                "screenshot",
                "screen snip",
                "snipping tool",
                "open snipping tool",
                "snip screen",
                "capture screen",
            ],
            "snippingtool.exe",
            "✂️ Snipping Tool / Screenshot",
        ),
        (
            [
                "open task manager",
                "task manager",
                "launch task manager",
                "open taskmgr",
                "taskmgr",
            ],
            "taskmgr.exe",
            "📊 Task Manager",
        ),
        (
            [
                "open settings",
                "launch settings",
                "windows settings",
                "open control panel",
                "pc settings",
            ],
            "start ms-settings:",
            "⚙️ Windows Settings",
        ),
        (
            ["open paint", "launch paint", "paint", "mspaint", "open mspaint"],
            "mspaint.exe",
            "🎨 Microsoft Paint",
        ),
        (
            [
                "open file explorer",
                "launch file explorer",
                "file explorer",
                "explorer",
                "open explorer",
                "open my computer",
                "open this pc",
                "files",
            ],
            "explorer.exe",
            "📁 File Explorer",
        ),
        (
            [
                "open cmd",
                "open command prompt",
                "launch cmd",
                "command prompt",
                "open terminal",
                "open powershell",
                "powershell",
            ],
            "cmd.exe /c start cmd.exe",
            "💻 Command Prompt Terminal",
        ),
        (
            ["open chrome", "launch chrome", "google chrome", "open google chrome"],
            "chrome.exe",
            "🌐 Google Chrome",
        ),
        (
            ["open edge", "launch edge", "microsoft edge", "open msedge"],
            "msedge.exe",
            "🌐 Microsoft Edge",
        ),
    ]

    for triggers, cmd, label in app_registry:
        if any(
            norm == t or norm == f"please {t}" or norm == f"can you {t}"
            for t in triggers
        ):
            clear_active_skill_quietly()
            try:
                if cmd.startswith("start "):
                    subprocess.Popen(cmd, shell=True)
                elif "/" in cmd or " " in cmd:
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen(["cmd.exe", "/c", "start", cmd])
                play_success_beep()
                return (
                    f"✅ **{label}** launched.",
                    "everyday_app_launch",
                    [
                        {
                            "language": "powershell",
                            "code": f"start {cmd}",
                            "output": f"Launched {label} (Process Initialized)",
                        }
                    ],
                )
            except Exception as e:
                play_error_beep()
                return (
                    f"⚠️ Failed to launch {label}: {e}",
                    "everyday_app_launch_error",
                    [
                        {
                            "language": "powershell",
                            "code": f"start {cmd}",
                            "output": str(e),
                        }
                    ],
                )

    # =========================================================================
    # 4. EVERYDAY QUICK FOLDERS SHORTCUTS
    # =========================================================================
    folder_shortcuts = [
        (
            ["open downloads", "downloads folder", "show downloads", "downloads"],
            os.path.expanduser("~/Downloads"),
            "📥 Downloads Folder",
        ),
        (
            [
                "open documents",
                "documents folder",
                "show documents",
                "documents",
                "my documents",
            ],
            os.path.expanduser("~/Documents"),
            "📄 Documents Folder",
        ),
        (
            ["open desktop", "desktop folder", "show desktop folder"],
            os.path.expanduser("~/Desktop"),
            "🖥️ Desktop Folder",
        ),
        (
            [
                "open pictures",
                "pictures folder",
                "show pictures",
                "photos",
                "photos folder",
                "open photos",
            ],
            os.path.expanduser("~/Pictures"),
            "🖼️ Pictures Folder",
        ),
        (
            ["open videos", "videos folder", "show videos"],
            os.path.expanduser("~/Videos"),
            "🎬 Videos Folder",
        ),
        (
            ["open music", "music folder", "show music"],
            os.path.expanduser("~/Music"),
            "🎵 Music Folder",
        ),
        (
            ["open c drive", "c drive", "c:", "open local disk c"],
            "C:\\",
            "💾 Local Disk (C:)",
        ),
    ]

    for triggers, path, label in folder_shortcuts:
        if any(norm == t or norm == f"please {t}" for t in triggers):
            clear_active_skill_quietly()
            try:
                os.startfile(path)
                play_success_beep()
                return (
                    f"📂 **{label}** opened.",
                    "everyday_folder_open",
                    [
                        {
                            "language": "powershell",
                            "code": f"explorer.exe '{path}'",
                            "output": f"Opened {label}",
                        }
                    ],
                )
            except Exception:
                pass

    # Empty Recycle Bin
    if any(
        norm == t
        for t in [
            "empty recycle bin",
            "clean recycle bin",
            "clear recycle bin",
            "empty trash",
            "clean trash",
        ]
    ):
        clear_active_skill_quietly()
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
                ]
            )
            play_success_beep()
            return (
                "🗑️ Recycle Bin cleared.",
                "everyday_recycle_bin",
                [
                    {
                        "language": "powershell",
                        "code": "Clear-RecycleBin -Force",
                        "output": "Recycle Bin purged",
                    }
                ],
            )
        except Exception:
            pass

    # =========================================================================
    # 5. DESKTOP, WINDOW MANAGEMENT & POWER
    # =========================================================================

    # 5A. Minimize All / Show Desktop
    if any(
        norm == t
        for t in [
            "minimize all",
            "minimize all windows",
            "minimize windows",
            "show desktop",
            "hide all windows",
        ]
    ):
        clear_active_skill_quietly()
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(New-Object -ComObject Shell.Application).MinimizeAll()",
                ]
            )
            play_success_beep()
            return (
                "🪟 All windows minimized.",
                "everyday_minimize_all",
                [
                    {
                        "language": "powershell",
                        "code": "(New-Object -ComObject Shell.Application).MinimizeAll()",
                        "output": "All windows minimized",
                    }
                ],
            )
        except Exception:
            pass

    # 5B. Lock PC
    if any(
        norm == t
        for t in [
            "lock pc",
            "lock computer",
            "lock screen",
            "lock workstation",
            "lock windows",
        ]
    ):
        clear_active_skill_quietly()
        try:
            ctypes.windll.user32.LockWorkStation()
            play_success_beep()
            return (
                "🔒 PC Locked.",
                "everyday_lock_pc",
                [
                    {
                        "language": "powershell",
                        "code": "rundll32.exe user32.dll,LockWorkStation",
                        "output": "WorkStation Locked",
                    }
                ],
            )
        except Exception:
            pass

    # 5C. Sleep PC
    if any(
        norm == t
        for t in [
            "sleep pc",
            "put pc to sleep",
            "sleep computer",
            "put computer to sleep",
            "suspend pc",
        ]
    ):
        clear_active_skill_quietly()
        try:
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            play_success_beep()
            return (
                "💤 PC going to sleep.",
                "everyday_sleep_pc",
                [
                    {
                        "language": "powershell",
                        "code": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                        "output": "System Sleep Invoked",
                    }
                ],
            )
        except Exception:
            pass

    # =========================================================================
    # 6. MEDIA PLAYBACK CONTROLS
    # =========================================================================
    if any(
        norm == t
        for t in [
            "play",
            "pause",
            "play music",
            "pause music",
            "resume music",
            "toggle play",
            "play pause",
        ]
    ):
        clear_active_skill_quietly()
        press_key(VK_MEDIA_PLAY_PAUSE)
        return (
            "⏯️ **Autonomous Everyday PC Action:** Media Play/Pause toggled.",
            "everyday_media_play_pause",
            [
                {
                    "language": "powershell",
                    "code": "SendKey(VK_MEDIA_PLAY_PAUSE)",
                    "output": "Play/Pause Sent",
                }
            ],
        )

    if any(
        norm == t
        for t in ["next song", "next track", "skip song", "next", "skip track"]
    ):
        clear_active_skill_quietly()
        press_key(VK_MEDIA_NEXT_TRACK)
        return (
            "⏭️ **Autonomous Everyday PC Action:** Skipped to Next Track.",
            "everyday_media_next",
            [
                {
                    "language": "powershell",
                    "code": "SendKey(VK_MEDIA_NEXT_TRACK)",
                    "output": "Next Track Sent",
                }
            ],
        )

    if any(
        norm == t
        for t in [
            "previous song",
            "previous track",
            "prev song",
            "last song",
            "prev track",
        ]
    ):
        clear_active_skill_quietly()
        press_key(VK_MEDIA_PREV_TRACK)
        return (
            "⏮️ **Autonomous Everyday PC Action:** Rewound to Previous Track.",
            "everyday_media_prev",
            [
                {
                    "language": "powershell",
                    "code": "SendKey(VK_MEDIA_PREV_TRACK)",
                    "output": "Previous Track Sent",
                }
            ],
        )

    if any(norm == t for t in ["stop music", "stop audio", "stop playback"]):
        clear_active_skill_quietly()
        press_key(VK_MEDIA_STOP)
        return (
            "⏹️ **Autonomous Everyday PC Action:** Media playback stopped.",
            "everyday_media_stop",
            [
                {
                    "language": "powershell",
                    "code": "SendKey(VK_MEDIA_STOP)",
                    "output": "Playback Stopped",
                }
            ],
        )

    # =========================================================================
    # 7. LIVE SYSTEM STATUS, TELEMETRY & HARDWARE SPECS
    # =========================================================================

    # 7A. Date & Time
    if any(
        norm == t
        for t in [
            "what time is it",
            "current time",
            "time now",
            "tell me the time",
            "what is the time",
        ]
    ):
        now = datetime.datetime.now()
        return (
            f"🕒 **Current Local Time:** {now.strftime('%I:%M:%S %p')} ({now.strftime('%A, %B %d, %Y')})",
            "everyday_time_query",
            [
                {
                    "language": "python",
                    "code": "datetime.datetime.now()",
                    "output": now.isoformat(),
                }
            ],
        )

    if any(
        norm == t
        for t in [
            "today's date",
            "what is today's date",
            "what date is it",
            "current date",
            "what is the date",
        ]
    ):
        now = datetime.datetime.now()
        return (
            f"📅 **Today's Date:** {now.strftime('%A, %B %d, %Y')}",
            "everyday_date_query",
            [
                {
                    "language": "python",
                    "code": "datetime.date.today()",
                    "output": now.strftime("%Y-%m-%d"),
                }
            ],
        )

    # 7B. Battery Level
    if any(
        norm == t
        for t in [
            "battery",
            "battery percentage",
            "battery level",
            "battery status",
            "is pc charging",
        ]
    ):
        if psutil and hasattr(psutil, "sensors_battery"):
            bat = psutil.sensors_battery()
            if bat:
                plugged = (
                    "🔌 Plugged In (Charging)" if bat.power_plugged else "🔋 On Battery"
                )
                return (
                    f"🔋 **Autonomous Battery Telemetry:** Battery is at **{bat.percent}%** ({plugged}).",
                    "everyday_battery_telemetry",
                    [
                        {
                            "language": "python",
                            "code": "psutil.sensors_battery()",
                            "output": f"Percent: {bat.percent}%, Plugged: {bat.power_plugged}",
                        }
                    ],
                )
        return (
            "🔌 **Autonomous Battery Telemetry:** Workstation is connected to direct AC power.",
            "everyday_battery_telemetry",
            [
                {
                    "language": "text",
                    "code": "sensors_battery()",
                    "output": "AC Power Active",
                }
            ],
        )

    # 7C. Hardware & System Specs (RAM, CPU, Disk)
    if any(
        norm == t
        for t in [
            "system specs",
            "pc specs",
            "hardware status",
            "ram usage",
            "memory usage",
            "cpu usage",
            "disk space",
            "system info",
        ]
    ):
        ram_str, cpu_str, disk_str = "N/A", "N/A", "N/A"
        if psutil:
            ram = psutil.virtual_memory()
            ram_str = f"{ram.percent}% used ({round((ram.total - ram.available)/(1024**3), 1)}GB / {round(ram.total/(1024**3), 1)}GB)"
            cpu_str = f"{psutil.cpu_percent(interval=0.1)}% ({psutil.cpu_count(logical=True)} logical cores)"
            try:
                disk = psutil.disk_usage("C:")
                disk_str = f"{disk.percent}% used ({round(disk.free/(1024**3), 1)}GB free of {round(disk.total/(1024**3), 1)}GB)"
            except Exception:
                pass

        hostname = socket.gethostname()
        return (
            f"🖥️ **Live Workstation Telemetry ({hostname}):**\n\n"
            f"• **CPU Load:** {cpu_str}\n"
            f"• **RAM Memory:** {ram_str}\n"
            f"• **Storage (C:):** {disk_str}\n"
            f"• **OS Environment:** Windows {sys.getwindowsversion().major} (Build {sys.getwindowsversion().build})\n"
            f"• **Python Engine:** v{sys.version.split()[0]}",
            "everyday_system_specs",
            [
                {
                    "language": "python",
                    "code": "psutil.virtual_memory(); psutil.cpu_percent(); psutil.disk_usage('C:')",
                    "output": f"RAM: {ram_str} | CPU: {cpu_str} | Disk: {disk_str}",
                }
            ],
        )

    # 7D. Network / IP Address
    if any(
        norm == t
        for t in ["my ip", "ip address", "network status", "what is my ip", "local ip"]
    ):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return (
            f"🌐 **Network Configuration:**\n\n• **Computer Name:** `{hostname}`\n• **Local IPv4 Address:** `{local_ip}`",
            "everyday_network_ip",
            [
                {
                    "language": "python",
                    "code": "socket.gethostbyname(socket.gethostname())",
                    "output": f"{hostname}: {local_ip}",
                }
            ],
        )

    # =========================================================================
    # 8. EVERYDAY WEB DESTINATIONS & SEARCH
    # =========================================================================

    # Google Search query (e.g. "search google for apple stocks", "google latest space news")
    m_search = re.search(
        r"^(?:search\s+google\s+for|search\s+for|google\s+search\s+for|google)\s+(.+)$",
        norm,
    )
    if m_search:
        clear_active_skill_quietly()
        query = m_search.group(1).strip()
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return (
            f'🔍 **Autonomous Web Action:** Searched Google for **"{query}"** in your browser.\n\n🔗 [Open Results Directly]({url})',
            "everyday_web_search",
            [
                {
                    "language": "powershell",
                    "code": f"start '{url}'",
                    "output": f"Search launched for {query}",
                }
            ],
        )

    web_shortcuts = [
        (
            ["open youtube", "go to youtube", "youtube"],
            "https://www.youtube.com",
            "📺 YouTube",
        ),
        (
            ["open google", "go to google", "google"],
            "https://www.google.com",
            "🔍 Google",
        ),
        (
            ["open gmail", "go to gmail", "gmail", "open email"],
            "https://mail.google.com",
            "✉️ Gmail",
        ),
        (["open github", "go to github", "github"], "https://github.com", "🐙 GitHub"),
        (
            ["open reddit", "go to reddit", "reddit"],
            "https://www.reddit.com",
            "🤖 Reddit",
        ),
        (
            ["open twitter", "go to twitter", "twitter", "open x"],
            "https://x.com",
            "🐦 X / Twitter",
        ),
        (
            ["open chatgpt", "go to chatgpt", "chatgpt"],
            "https://chatgpt.com",
            "🧠 ChatGPT",
        ),
        (
            ["open wikipedia", "go to wikipedia", "wikipedia"],
            "https://www.wikipedia.org",
            "📚 Wikipedia",
        ),
    ]

    for triggers, url, label in web_shortcuts:
        if any(norm == t or norm == f"please {t}" for t in triggers):
            clear_active_skill_quietly()
            if "youtube.com" in url or "youtu.be" in url:
                import local_music_engine
                local_music_engine.open_in_chrome(url)
            else:
                webbrowser.open(url)
            return (
                f"🌐 **Autonomous Everyday Web Action:** Opened **{label}** in your browser.\n\n🔗 [Direct Link]({url})",
                "everyday_web_shortcut",
                [
                    {
                        "language": "powershell",
                        "code": f"start '{url}'",
                        "output": f"Navigated to {url}",
                    }
                ],
            )

    # =========================================================================
    # 9. HANDS-FREE AUTOMATED SCROLLING
    # =========================================================================
    MOUSEEVENTF_WHEEL = 0x0800
    user32 = ctypes.windll.user32

    # Scroll Down
    if any(
        norm == w or norm.startswith(w + " ")
        for w in [
            "scroll down",
            "scroll down a bit",
            "scroll down more",
            "scroll down please",
            "scroll lower",
            "go down",
            "scroll down the page",
            "scroll down screen",
        ]
    ):
        clear_active_skill_quietly()
        clicks = 5
        m_num = re.search(r"(\d+)", norm)
        if m_num:
            clicks = min(20, max(1, int(m_num.group(1))))
        delta = -120 * clicks
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        play_success_beep()
        return (
            f"📜 **Autonomous Desktop Control:** Scrolled down {clicks} steps.",
            "everyday_scroll_down",
            [
                {
                    "language": "python",
                    "code": f"user32.mouse_event(0x0800, 0, 0, {delta}, 0)",
                    "output": f"Scrolled down {clicks} clicks",
                }
            ],
        )

    # Scroll Up
    if any(
        norm == w or norm.startswith(w + " ")
        for w in [
            "scroll up",
            "scroll up a bit",
            "scroll up more",
            "scroll up please",
            "scroll higher",
            "go up",
            "scroll up the page",
            "scroll up screen",
        ]
    ):
        clear_active_skill_quietly()
        clicks = 5
        m_num = re.search(r"(\d+)", norm)
        if m_num:
            clicks = min(20, max(1, int(m_num.group(1))))
        delta = 120 * clicks
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        play_success_beep()
        return (
            f"📜 **Autonomous Desktop Control:** Scrolled up {clicks} steps.",
            "everyday_scroll_up",
            [
                {
                    "language": "python",
                    "code": f"user32.mouse_event(0x0800, 0, 0, {delta}, 0)",
                    "output": f"Scrolled up {clicks} clicks",
                }
            ],
        )

    # Page Down
    if norm in ["page down", "scroll page down", "next page", "scroll down one page"]:
        clear_active_skill_quietly()
        user32.keybd_event(0x22, 0, 0, 0)
        user32.keybd_event(0x22, 0, KEYEVENTF_KEYUP, 0)
        play_success_beep()
        return (
            "📜 **Autonomous Desktop Control:** Scrolled Page Down.",
            "everyday_page_down",
            [
                {
                    "language": "python",
                    "code": "user32.keybd_event(0x22, 0, 0, 0)",
                    "output": "Page Down key sent",
                }
            ],
        )

    # Page Up
    if norm in ["page up", "scroll page up", "previous page", "scroll up one page"]:
        clear_active_skill_quietly()
        user32.keybd_event(0x21, 0, 0, 0)
        user32.keybd_event(0x21, 0, KEYEVENTF_KEYUP, 0)
        play_success_beep()
        return (
            "📜 **Autonomous Desktop Control:** Scrolled Page Up.",
            "everyday_page_up",
            [
                {
                    "language": "python",
                    "code": "user32.keybd_event(0x21, 0, 0, 0)",
                    "output": "Page Up key sent",
                }
            ],
        )

    # Scroll to Top
    if norm in [
        "scroll to top",
        "go to top",
        "scroll top",
        "top of page",
        "scroll to the top",
    ]:
        clear_active_skill_quietly()
        user32.keybd_event(0x24, 0, 0, 0)
        user32.keybd_event(0x24, 0, KEYEVENTF_KEYUP, 0)
        play_success_beep()
        return (
            "📜 **Autonomous Desktop Control:** Scrolled to top of the page.",
            "everyday_scroll_top",
            [
                {
                    "language": "python",
                    "code": "user32.keybd_event(0x24, 0, 0, 0)",
                    "output": "Home key sent",
                }
            ],
        )

    # Scroll to Bottom
    if norm in [
        "scroll to bottom",
        "go to bottom",
        "scroll bottom",
        "bottom of page",
        "scroll to the bottom",
    ]:
        clear_active_skill_quietly()
        user32.keybd_event(0x23, 0, 0, 0)
        user32.keybd_event(0x23, 0, KEYEVENTF_KEYUP, 0)
        play_success_beep()
        return (
            "📜 **Autonomous Desktop Control:** Scrolled to bottom of the page.",
            "everyday_scroll_bottom",
            [
                {
                    "language": "python",
                    "code": "user32.keybd_event(0x23, 0, 0, 0)",
                    "output": "End key sent",
                }
            ],
        )

    # =========================================================================
    # 10. SCREEN RECORDING (LOCAL MP4)
    # =========================================================================
    if any(
        norm == w or norm.startswith(w + " ")
        for w in [
            "start recording",
            "record screen",
            "start screen recording",
            "record my work",
            "start video recording",
            "record desktop",
            "start desktop recording",
            "begin recording",
        ]
    ):
        clear_active_skill_quietly()
        try:
            import screen_recorder

            rec_res = screen_recorder.start_recording()
            play_success_beep()
            return (
                f"🎥 **Autonomous Screen Recorder:** {rec_res.get('message', 'Recording started.')}\n\n"
                f"📁 Destination: `{rec_res.get('file', 'recordings/')}`\n"
                f"💡 Say **'stop recording'** when finished to save the video file.",
                "screen_record_start",
                [
                    {
                        "language": "python",
                        "code": "screen_recorder.start_recording()",
                        "output": str(rec_res),
                    }
                ],
            )
        except Exception as e:
            play_error_beep()
            return (
                f"⚠️ **Screen Recorder Notice:** Could not start screen recording: {e}",
                "screen_record_error",
                [],
            )

    if any(
        norm == w or norm.startswith(w + " ")
        for w in [
            "stop recording",
            "stop screen recording",
            "save recording",
            "end recording",
            "finish recording",
            "stop desktop recording",
            "done recording",
        ]
    ):
        clear_active_skill_quietly()
        try:
            import screen_recorder

            rec_res = screen_recorder.stop_recording()
            play_success_beep()
            file_path = rec_res.get("file")
            dur = rec_res.get("duration_seconds", 0)
            size = rec_res.get("size_mb", 0)
            if file_path and os.path.exists(file_path):
                return (
                    f"🎬 **Screen Recording Saved!**\n\n"
                    f"- ⏱️ **Duration:** {dur} seconds\n"
                    f"- 📦 **File Size:** {size} MB\n"
                    f"- 💾 **Saved to:** `{file_path}`\n\n"
                    f"Video has been saved locally and is ready for playback.",
                    "screen_record_stop",
                    [
                        {
                            "language": "python",
                            "code": "screen_recorder.stop_recording()",
                            "output": str(rec_res),
                        }
                    ],
                )
            else:
                return (
                    f"ℹ️ **Screen Recorder:** {rec_res.get('message', 'No recording session was active.')}",
                    "screen_record_status",
                    [],
                )
        except Exception as e:
            return (
                f"⚠️ **Screen Recorder Notice:** Error stopping recording: {e}",
                "screen_record_error",
                [],
            )

    if norm in [
        "recording status",
        "is it recording",
        "is recording active",
        "are you recording",
    ]:
        clear_active_skill_quietly()
        try:
            import screen_recorder

            st = screen_recorder.get_recording_status()
            return (
                f"🎥 **Screen Recording Status:** {st.get('message', 'Idle')}",
                "screen_record_status",
                [],
            )
        except Exception:
            pass

    # =========================================================================
    # 11. LIVE SCREEN UNDERSTANDING & ERROR DIAGNOSIS (QWEN 2.5-VL)
    # =========================================================================
    if any(
        norm == w or norm.startswith(w)
        for w in [
            "what's on my screen",
            "what is on my screen",
            "look at my screen",
            "see my screen",
            "read my screen",
            "diagnose screen",
            "diagnose my screen",
            "find error on screen",
            "find the error",
            "check for errors on screen",
            "what is going on on my screen",
            "what is going on",
            "understand what is going on",
            "analyze my screen",
            "analyze screen",
            "inspect my screen",
            "tell me what is on my screen",
            "what do you see on my screen",
            "explain what is on my screen",
            "explain my screen",
            "check my screen",
        ]
    ):
        clear_active_skill_quietly()
        try:
            import screen_vision

            v_prompt = (
                "You are D.E.E.P. AI inspecting the user's active desktop screen. "
                "1. State what window or application is currently in focus. "
                "2. If code, terminal commands, or errors/tracebacks are visible: accurately diagnose the exact error, cause, and how to fix it. "
                "3. If a web browser or document is open: give a succinct summary. "
                "4. Be direct, clear, and actionable."
            )
            analysis_data = screen_vision.analyze_desktop_screen(
                prompt=v_prompt, model="qwen2.5vl:7b", timeout_s=45
            )
            if analysis_data.get("status") == "success":
                analysis_text = analysis_data.get("analysis", "")
                latency = analysis_data.get("latency_s", 0)
                model_used = analysis_data.get("model", "qwen2.5vl:7b")
                play_success_beep()
                return (
                    f"🖥️ **Screen Vision Diagnosis** *(Powered by {model_used} in {latency}s)*:\n\n"
                    f"{analysis_text}",
                    "screen_vision_diagnosis",
                    [
                        {
                            "language": "json",
                            "code": "screen_vision.analyze_desktop_screen()",
                            "output": f"Processed via {model_used} in {latency}s",
                        }
                    ],
                )
            else:
                return (
                    f"⚠️ **Screen Vision Notice:** {analysis_data.get('message', 'Could not analyze screen at this moment.')}",
                    "screen_vision_error",
                    [],
                )
        except Exception as e:
            play_error_beep()
            return (f"⚠️ **Screen Vision Exception:** {e}", "screen_vision_error", [])

    # =========================================================================
    # 12. WORKSPACE WINDOW SNAP & GRID ARRANGER
    # =========================================================================
    if norm in [
        "snap left",
        "put window on left",
        "window left",
        "dock left",
        "move left",
    ]:
        clear_active_skill_quietly()
        try:
            import workspace_arranger

            res = workspace_arranger.snap_left()
            play_success_beep()
            return (
                f"🪟 **Workspace Arranger:** {res.get('message', 'Snapped active window to left.')}",
                "workspace_snap_left",
                [],
            )
        except Exception as e:
            return (f"⚠️ Workspace note: {e}", "workspace_error", [])

    if norm in [
        "snap right",
        "put window on right",
        "window right",
        "dock right",
        "move right",
    ]:
        clear_active_skill_quietly()
        try:
            import workspace_arranger

            res = workspace_arranger.snap_right()
            play_success_beep()
            return (
                f"🪟 **Workspace Arranger:** {res.get('message', 'Snapped active window to right.')}",
                "workspace_snap_right",
                [],
            )
        except Exception as e:
            return (f"⚠️ Workspace note: {e}", "workspace_error", [])

    if norm in ["maximize window", "maximize", "full screen window", "full screen"]:
        clear_active_skill_quietly()
        try:
            import workspace_arranger

            res = workspace_arranger.maximize_window()
            play_success_beep()
            return (
                f"🪟 **Workspace Arranger:** {res.get('message', 'Maximized window.')}",
                "workspace_maximize",
                [],
            )
        except Exception as e:
            return (f"⚠️ Workspace note: {e}", "workspace_error", [])

    if norm in [
        "coding layout",
        "tile windows",
        "arrange workspace",
        "split screen",
        "coding setup",
    ]:
        clear_active_skill_quietly()
        try:
            import workspace_arranger

            res = workspace_arranger.arrange_coding_layout()
            play_success_beep()
            return (
                f"💻 **Workspace Arranger:** {res.get('message', 'Coding layout arranged.')}",
                "workspace_coding_layout",
                [],
            )
        except Exception as e:
            return (f"⚠️ Workspace note: {e}", "workspace_error", [])

    # =========================================================================
    # 13. SMART CLIPBOARD COPILOT
    # =========================================================================
    if norm in [
        "read clipboard",
        "what's on my clipboard",
        "check clipboard",
        "inspect clipboard",
        "clipboard content",
    ]:
        clear_active_skill_quietly()
        try:
            import clipboard_copilot

            res = clipboard_copilot.analyze_clipboard()
            play_success_beep()
            summary = res.get("summary", "Clipboard read.")
            preview = res.get("preview", "")
            return (
                f"📋 **Smart Clipboard Copilot:** {summary}\n\n"
                f"```\n{preview}\n```\n"
                f"💡 *Tip: Say 'fix clipboard' to automatically repair bugs, or 'format clipboard' for JSON.*",
                "clipboard_read",
                [],
            )
        except Exception as e:
            return (f"⚠️ Clipboard error: {e}", "clipboard_error", [])

    if norm in [
        "fix clipboard",
        "debug clipboard",
        "repair clipboard",
        "fix code on clipboard",
    ]:
        clear_active_skill_quietly()
        try:
            import clipboard_copilot

            res = clipboard_copilot.fix_clipboard_with_ai()
            if res.get("status") == "success":
                play_success_beep()
                return (
                    f"✨ **Smart Clipboard Copilot Fix:**\n\n"
                    f"{res.get('explanation', '')}\n\n"
                    f"✅ **{res.get('message', 'Fixed code copied to clipboard!')}**",
                    "clipboard_fix",
                    [],
                )
            else:
                return (
                    f"⚠️ Clipboard Copilot: {res.get('message', 'Could not repair code.')}",
                    "clipboard_notice",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Clipboard Copilot error: {e}", "clipboard_error", [])

    if norm in ["format clipboard", "format json on clipboard", "beautify clipboard"]:
        clear_active_skill_quietly()
        try:
            import clipboard_copilot

            res = clipboard_copilot.format_clipboard()
            play_success_beep()
            return (
                f"📋 **Smart Clipboard Copilot:** {res.get('message')}",
                "clipboard_format",
                [],
            )
        except Exception as e:
            return (f"⚠️ Clipboard error: {e}", "clipboard_error", [])

    # =========================================================================
    # 14. LIVE ERROR WATCHDOG SENTINEL
    # =========================================================================
    if norm in [
        "start watchdog",
        "start error watchdog",
        "enable sentinel",
        "enable error watchdog",
    ]:
        clear_active_skill_quietly()
        try:
            import error_watchdog

            res = error_watchdog.start_watchdog()
            play_success_beep()
            return (
                f"🛡️ **Error Watchdog Sentinel:** {res.get('message')}",
                "watchdog_start",
                [],
            )
        except Exception as e:
            return (f"⚠️ Watchdog note: {e}", "watchdog_error", [])

    if norm in ["stop watchdog", "stop error watchdog", "disable sentinel"]:
        clear_active_skill_quietly()
        try:
            import error_watchdog

            res = error_watchdog.stop_watchdog()
            play_success_beep()
            return (
                f"🛡️ **Error Watchdog Sentinel:** {res.get('message')}",
                "watchdog_stop",
                [],
            )
        except Exception as e:
            return (f"⚠️ Watchdog note: {e}", "watchdog_error", [])

    if norm in ["watchdog status", "error watchdog status", "check watchdog"]:
        clear_active_skill_quietly()
        try:
            import error_watchdog

            res = error_watchdog.get_watchdog_status()
            return (
                f"🛡️ **Error Watchdog Status:** Active: **{res.get('is_running')}**\n"
                f"- Check interval: {res.get('interval_seconds')}s\n"
                f"- Last checked: {res.get('last_checked')}\n"
                f"- Total alerts: {res.get('error_count')}",
                "watchdog_status",
                [],
            )
        except Exception as e:
            return (f"⚠️ Watchdog note: {e}", "watchdog_error", [])

    # =========================================================================
    # 15. VISUAL UI AUTO-CLICKER ("CLICK BY VISION")
    # =========================================================================
    m_click = re.search(r"^(?:click|click\s+on|tap|press)\s+(.+)$", norm)
    if m_click and not any(
        w in norm for w in ["youtube", "music", "song", "video", "button below"]
    ):
        clear_active_skill_quietly()
        target_name = m_click.group(1).strip()
        try:
            import visual_clicker

            res = visual_clicker.locate_and_click(target_name)
            if res.get("status") == "success":
                play_success_beep()
                return (
                    f"🎯 **Visual Auto-Clicker:** {res.get('message', 'Clicked successfully.')}",
                    "visual_click_success",
                    [],
                )
            else:
                return (
                    f"⚠️ **Visual Auto-Clicker:** {res.get('message', 'Could not locate element.')}",
                    "visual_click_notice",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Visual Clicker error: {e}", "visual_click_error", [])

    # =========================================================================
    # 16. AGENT-REACH LIVE INTERNET SEARCH ($0 API FEES)
    # =========================================================================
    m_reach = re.search(
        r"^(?:reach\s+search|search\s+internet\s+for|search\s+web\s+for|internet\s+search\s+for|agent\s+reach)\s+(.+)$",
        norm,
    )
    if m_reach:
        clear_active_skill_quietly()
        q = m_reach.group(1).strip()
        try:
            import agent_reach_engine

            data = agent_reach_engine.multi_reach_search(q)
            md_report = agent_reach_engine.format_reach_markdown(data)
            play_success_beep()
            return (md_report, "agent_reach_search", [])
        except Exception as e:
            return (f"⚠️ Agent-Reach error: {e}", "agent_reach_error", [])

    m_gh_search = re.search(
        r"^(?:search\s+github\s+for|find\s+github\s+repos\s+for|github\s+search)\s+(.+)$",
        norm,
    )
    if m_gh_search:
        clear_active_skill_quietly()
        q = m_gh_search.group(1).strip()
        try:
            import agent_reach_engine

            repos = agent_reach_engine.search_github(q, limit=4)
            md = [f'🐙 **GitHub Repositories for "{q}":**\n']
            for r in repos:
                md.append(
                    f"- [{r['title']}]({r['url']}) ⭐ `{r['stars']:,} stars` ({r['language']})\n  *{r['description']}*"
                )
            play_success_beep()
            return ("\n".join(md), "agent_reach_github", [])
        except Exception as e:
            return (f"⚠️ GitHub search error: {e}", "github_search_error", [])

    # =========================================================================
    # 17. VOICE CLONING & PERSONALITY STUDIO (OPENVOICE / NEURAL)
    # =========================================================================
    m_voice_switch = re.search(
        r"^(?:switch|change|set)\s+(?:the\s+)?voice\s+(?:to\s+)?([a-zA-Z0-9_\-]+)$",
        norm,
    )
    if m_voice_switch or any(
        norm == f"voice {p}"
        for p in ["jarvis", "friday", "commander", "deep", "punjabi", "hindi"]
    ):
        clear_active_skill_quietly()
        prof_name = (
            m_voice_switch.group(1).strip()
            if m_voice_switch
            else norm.replace("voice ", "").strip()
        )
        try:
            import voice_cloning_engine

            res = voice_cloning_engine.set_active_profile(prof_name)
            if res.get("status") == "success":
                play_success_beep()
                return (
                    f"🎙️ **Voice Personality Switched!**\n\n"
                    f"- **Active Voice:** {res.get('name')}\n"
                    f"- **Audio Engine:** Neural Studio (Edge-TTS + OpenVoice Profile)\n\n"
                    f"All spoken responses will now use this personality.",
                    "voice_profile_switched",
                    [],
                )
            else:
                return (
                    f"⚠️ Voice Switch Notice: {res.get('message')}",
                    "voice_profile_notice",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Voice Switch Error: {e}", "voice_profile_error", [])

    if norm in ["list voices", "available voices", "voice options", "voice profiles"]:
        clear_active_skill_quietly()
        try:
            import voice_cloning_engine

            profs = voice_cloning_engine.list_profiles()
            md = ["🎙️ **Available Voice Personalities:**\n"]
            for k, v in profs.get("profiles", {}).items():
                active_badge = " *(Active)*" if k == profs.get("active") else ""
                md.append(
                    f"- **{v['name']}** (`switch voice to {k}`){active_badge}\n  *{v['description']}*"
                )
            return ("\n".join(md), "voice_profiles_list", [])
        except Exception as e:
            return (f"⚠️ Error listing voices: {e}", "voice_profile_error", [])

    # =========================================================================
    # 18. INTERCEPTOR SECURITY AUDIT
    # =========================================================================
    if norm in [
        "interceptor logs",
        "security audit logs",
        "show blocked actions",
        "interceptor status",
    ]:
        clear_active_skill_quietly()
        try:
            import interceptor_engine

            logs = interceptor_engine.get_recent_interceptions(limit=8)
            md = ["🛡️ **Interceptor Security Guardrail Logs:**\n"]
            for l in logs:
                icon = "🛑" if l["status"] == "BLOCKED" else "✅"
                md.append(
                    f"- {icon} **[{l['timestamp']}]** `{l['action_type']}`: {l['reason']} *(Target: `{l['target']}`)*"
                )
            if not logs:
                md.append("No security events logged yet. All actions normal.")
            return ("\n".join(md), "interceptor_logs", [])
        except Exception as e:
            return (f"⚠️ Interceptor logs error: {e}", "interceptor_error", [])

    # =========================================================================
    # 19. VOICE CLONING & PERSONALITY STUDIO
    # =========================================================================
    if norm in [
        "clone my voice",
        "record my voice",
        "voice cloning",
        "clone voice",
        "open voice studio",
    ]:
        clear_active_skill_quietly()
        play_success_beep()
        return (
            "Opening Neural Voice Cloning Studio. Click 'Record 5s Clip' or upload an audio file to clone your voice.",
            "open_voice_studio",
            [],
        )

    if norm in [
        "switch voice to my voice",
        "use my voice",
        "switch to my voice",
        "my voice",
    ]:
        clear_active_skill_quietly()
        try:
            import voice_cloning_engine

            res = voice_cloning_engine.set_active_profile("my_voice")
            if res.get("status") == "success":
                play_success_beep()
                return (
                    "Switched active voice personality to My Cloned Voice.",
                    "voice_switch_my_voice",
                    [],
                )
            else:
                return (
                    "No custom voice recorded yet! Say 'clone my voice' or click '🎙️ Clone Voice' to record your voice first.",
                    "voice_no_clone",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Voice switch error: {e}", "voice_error", [])

    # =========================================================================
    # 20. PUNJABI NATIVE COMMANDS & UNDERSTANDING (GURMUKHI & ROMAN)
    # =========================================================================
    if any(
        k in norm
        for k in [
            "sat sri akal",
            "sat shri akal",
            "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ",
            "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ",
            "ਕਿਵੇਂ ਹੋ",
            "kive ho",
            "kidda",
            "ki haal hai",
            "ki haal chaal",
        ]
    ):
        clear_active_skill_quietly()
        play_success_beep()
        return (
            "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਜੀ! ਮੈਂ ਦੀਪ ਹਾਂ, ਤੁਹਾਡਾ ਏਆਈ ਅਸਿਸਟੈਂਟ। ਦੱਸੋ ਜੀ ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕੀ ਸੇਵਾ ਕਰ ਸਕਦਾ ਹਾਂ?",
            "punjabi_greeting",
            [],
        )

    if any(
        k in norm
        for k in ["ਨੋਟਪੈਡ ਖੋਲ੍ਹੋ", "ਨੋਟਪੈਡ ਖੋਲੋ", "ਨੋਟਪੈਡ ਖੋਲ", "notepad kholo"]
    ):
        clear_active_skill_quietly()
        play_success_beep()
        os.system("start notepad.exe")
        return ("ਨੋਟਪੈਡ ਖੋਲ੍ਹ ਦਿੱਤਾ ਗਿਆ ਹੈ ਜੀ।", "open_notepad", [])

    if any(
        k in norm
        for k in [
            "ਕੈਲਕੁਲੇਟਰ ਖੋਲ੍ਹੋ",
            "ਕੈਲਕੁਲੇਟਰ ਖੋਲੋ",
            "calc kholo",
            "calculator kholo",
        ]
    ):
        clear_active_skill_quietly()
        play_success_beep()
        os.system("start calc.exe")
        return ("ਕੈਲਕੁਲੇਟਰ ਖੋਲ੍ਹ ਦਿੱਤਾ ਗਿਆ ਹੈ ਜੀ।", "open_calc", [])

    if any(
        k in norm
        for k in [
            "ਮੌਸਮ ਕਿਵੇਂ ਹੈ",
            "ਮੌਸਮ ਦੱਸੋ",
            "ਮੌਸਮ ਕਿਹੋ ਜਿਹਾ ਹੈ",
            "mausam kiven hai",
            "mausam dasso",
            "mausam kive hai",
        ]
    ):
        clear_active_skill_quietly()
        play_success_beep()
        return (
            "ਲਾਈਵ ਮੌਸਮ ਰਾਡਾਰ ਖੋਲ੍ਹ ਰਿਹਾ ਹਾਂ ਜੀ।",
            "open_weather",
            [{"tool": "open_subsystem", "args": {"subsystem": "weather"}}],
        )

    if any(
        k in norm
        for k in [
            "ਗਾਣਾ ਚਲਾਓ",
            "ਗੀਤ ਚਲਾਓ",
            "ਯੂਟਿਊਬ ਚਲਾਓ",
            "gana chalao",
            "geet chalao",
            "youtube chalao",
        ]
    ) and not any(l in norm for l in ["ਲੋਕਲ", "local", "pc"]):
        clear_active_skill_quietly()
        play_success_beep()
        import local_music_engine
        local_music_engine.open_in_chrome("https://www.youtube.com/results?search_query=punjabi+songs")
        return ("ਯੂਟਿਊਬ ਉੱਤੇ ਪੰਜਾਬੀ ਗੀਤ ਗੂਗਲ ਕਰੋਮ ਵਿੱਚ ਚਲਾ ਦਿੱਤੇ ਹਨ ਜੀ।", "play_youtube", [])

    if any(k in norm for k in ["ਸਕ੍ਰੀਨਸ਼ੌਟ ਲਓ", "ਸਕਰੀਨਸ਼ੋਟ ਲਓ", "screenshot lao"]):
        clear_active_skill_quietly()
        play_success_beep()
        return ("ਸਕ੍ਰੀਨਸ਼ੌਟ ਲਿਆ ਜਾ ਰਿਹਾ ਹੈ ਜੀ।", "take_screenshot", [])

    if any(
        k in norm
        for k in ["ਸਕ੍ਰੀਨ ਦੇਖੋ", "ਸਕ੍ਰੀਨ ਸਮਝੋ", "screen dekho", "screen samjho"]
    ):
        clear_active_skill_quietly()
        play_success_beep()
        return ("ਮੈਂ ਤੁਹਾਡੀ ਸਕ੍ਰੀਨ ਦੀ ਜਾਂਚ ਕਰ ਰਿਹਾ ਹਾਂ ਜੀ...", "screen_diagnose", [])

    # =========================================================================
    # 21. LOCAL PC MUSIC PLAYBACK (MP3, WAV, FLAC, M4A)
    # =========================================================================
    m_list_music = re.search(
        r"^(?:list\s+my\s+music|list\s+local\s+music|what\s+songs\s+do\s+i\s+have|show\s+my\s+music|show\s+local\s+music)$",
        norm,
    )
    if m_list_music:
        clear_active_skill_quietly()
        try:
            import local_music_engine

            tracks = local_music_engine.scan_local_music(max_results=10)
            if tracks:
                msg = [f"🎵 **Found {len(tracks)} local track(s) on your PC:**\n"]
                for t in tracks:
                    msg.append(
                        f"- **{t['title']}** (`{t['filename']}`) - {t['size_mb']} MB in `{t['folder']}`"
                    )
                msg.append("\n*Say 'play [song name]' or 'play local music' to play.*")
                play_success_beep()
                return ("\n".join(msg), "list_local_music", [])
            else:
                return (
                    "No music files found in C:\\Users\\User\\Music or Downloads. Copy some .mp3 or .wav files into your Music folder!",
                    "list_local_music_empty",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Music search error: {e}", "music_error", [])

    m_play_local = re.search(
        r"^(?:play\s+local\s+music|play\s+music\s+on\s+my\s+pc|play\s+song\s+on\s+my\s+pc|play\s+local\s+song|play\s+pc\s+music|play\s+offline\s+music)$",
        norm,
    )
    if m_play_local or any(
        norm == k for k in ["ਲੋਕਲ ਗਾਣਾ ਚਲਾਓ", "local gana chalao", "pc te gana chalao"]
    ):
        clear_active_skill_quietly()
        try:
            import local_music_engine

            track = local_music_engine.find_track("")
            if track:
                res = local_music_engine.play_track(track["path"])
                play_success_beep()
                return (
                    f"🎵 **Playing Local Music:** {track['title']} ({track['filename']}) in your default media player.",
                    "play_local_music",
                    [],
                )
            else:
                return (
                    "No audio files found. Place your songs (.mp3, .wav, .flac) in `C:\\Users\\User\\Music`!",
                    "no_music_found",
                    [],
                )
        except Exception as e:
            return (f"⚠️ Music player error: {e}", "music_error", [])

    m_play_specific = re.search(
        r"^(?:play\s+local\s+song|play\s+song|play\s+track)\s+(.+)$", norm
    )
    if m_play_specific and not any(
        k in norm for k in ["youtube", "on youtube", "video"]
    ):
        song_name = m_play_specific.group(1).strip()
        clear_active_skill_quietly()
        try:
            import local_music_engine

            track = local_music_engine.find_track(song_name)
            if track:
                res = local_music_engine.play_track(track["path"])
                play_success_beep()
                return (
                    f"🎵 **Playing Local Song:** {track['title']} ({track['filename']}) in your default media player.",
                    "play_local_song",
                    [],
                )
            else:
                download_res = local_music_engine.download_and_play_track(song_name)
                if download_res.get("status") == "success":
                    play_success_beep()
                    return (
                        f"🎵 **Downloaded & Playing in PC Music Player:** {download_res['title']} ({download_res['filename']}) in your default media player.",
                        "download_and_play_song",
                        [
                            {
                                "language": "powershell",
                                "code": f'Start-Process -FilePath "{download_res["path"]}"',
                                "output": f"Playing {download_res['filename']}",
                            }
                        ],
                    )
                else:
                    return (
                        f"Could not find or download '{song_name}' to local music: {download_res.get('message', 'Download error')}",
                        "download_error",
                        [],
                    )
        except Exception as e:
            return (f"⚠️ Music player error: {e}", "music_error", [])

    return None


# ============================================================
# SECTION 22: BLENDER 3D AI COPILOT COMMANDS
# ============================================================

# def handle_blender_command(cmd):
#     """Handle all Blender-related voice and text commands."""
#     import urllib.request
#     import json
#
#     cmd_lower = cmd.lower().strip()
#
#     # Just launch Blender (no modeling)
#     launch_keywords = ["open blender", "launch blender", "start blender", "blender kholo", "blender open"]
#     if any(k in cmd_lower for k in launch_keywords):
#         try:
#             req = urllib.request.Request(
#                 "http://127.0.0.1:5000/api/blender/open",
#                 data=json.dumps({}).encode(),
#                 headers={"Content-Type": "application/json"}
#             )
#             urllib.request.urlopen(req, timeout=5)
#             return {
#                 "action": "open_blender",
#                 "spoken": "Opening Blender 3D suite on your desktop.",
#                 "status": "launched"
#             }
#         except Exception as e:
#             return {"action": "open_blender", "spoken": f"Error launching Blender: {e}", "status": "error"}
#
#     # 3D Modeling triggers
#     model_triggers = [
#         "make a 3d", "create a 3d", "model a", "model in blender",
#         "design a 3d", "build a 3d", "blender make", "blender create",
#         "3d model banao", "3d banao", "blender mein banao",
#         "make in blender", "create in blender", "build in blender",
#         "generate 3d", "render 3d"
#     ]
#
#     is_3d_command = any(k in cmd_lower for k in model_triggers)
#
#     if is_3d_command:
#         # Extract the subject of the 3D model
#         subject = cmd_lower
#         for strip_prefix in ["make a 3d", "create a 3d", "model a", "model in blender",
#                               "design a 3d", "build a 3d", "blender make", "blender create",
#                               "make in blender", "create in blender", "build in blender",
#                               "generate 3d", "render 3d", "3d model banao", "3d banao",
#                               "blender mein banao"]:
#             subject = subject.replace(strip_prefix, "").strip()
#         for strip_suffix in ["in blender", "with blender", "using blender"]:
#             subject = subject.rstrip().removesuffix(strip_suffix).strip()
#         if not subject:
#             subject = "abstract object"
#
#         # Launch async 3D creation
#         prompt = cmd  # pass full original command for best LLM context
#         try:
#             payload = {"prompt": prompt, "auto_open": True}
#             req = urllib.request.Request(
#                 "http://127.0.0.1:5000/api/blender/create",
#                 data=json.dumps(payload).encode(),
#                 headers={"Content-Type": "application/json"}
#             )
#             urllib.request.urlopen(req, timeout=8)
#             return {
#                 "action": "blender_create",
#                 "spoken": f"On it! I am generating a 3D {subject} in Blender right now. Blender will open with your model in about 20 to 30 seconds.",
#                 "status": "started",
#                 "prompt": prompt
#             }
#         except Exception as e:
#             return {
#                 "action": "blender_create",
#                 "spoken": f"Blender modeling failed: {e}",
#                 "status": "error"
#             }
#
#     return None
#
#
# def is_blender_command(cmd):
#     """Returns True if the command is Blender or 3D modeling related."""
#     cmd_lower = cmd.lower()
#     blender_keywords = [
#         "open blender", "launch blender", "start blender",
#         "make a 3d", "create a 3d", "model a", "model in blender",
#         "design a 3d", "build a 3d", "blender make", "blender create",
#         "3d model", "make in blender", "create in blender", "build in blender",
#         "generate 3d", "render 3d", "3d banao", "blender kholo",
#         "3d model banao", "blender mein banao"
#     ]
#     return any(k in cmd_lower for k in blender_keywords)
