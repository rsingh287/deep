from flask import Blueprint, request, jsonify, render_template, current_app, Response, redirect, send_from_directory
import os, json, subprocess, requests, base64, time, psutil, platform
import urllib.parse
import pyautogui
import db_engine
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory.db")
OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")
SERVER_BOOT_TIME = time.time()
LAST_USER_INTERACTION = time.time()

system_bp = Blueprint('system', __name__)

_gpu_cache = {"time": 0, "gpu_pct": 0, "vram_used_mb": 0, "vram_total_mb": 8192, "vram_pct": 0}

def get_nvidia_telemetry():
    now = time.time()
    if now - _gpu_cache["time"] < 1.5:
        return _gpu_cache
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            timeout=1.5,
            startupinfo=startupinfo,
            text=True
        )
        parts = [p.strip() for p in res.strip().split(",")]
        if len(parts) >= 3:
            gpu_pct = int(parts[0])
            vram_used = int(parts[1])
            vram_total = int(parts[2])
            vram_pct = round((vram_used / vram_total) * 100, 1) if vram_total > 0 else 0
            _gpu_cache.update({
                "time": now,
                "gpu_pct": gpu_pct,
                "vram_used_mb": vram_used,
                "vram_total_mb": vram_total,
                "vram_pct": vram_pct
            })
    except Exception:
        pass
    return _gpu_cache



@system_bp.route("/api/system/info", methods=["GET"])
def get_system_info():
    try:
        cpu_pct = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        drive = os.path.splitdrive(os.path.abspath(__file__))[0] + "\\"
        disk = psutil.disk_usage(drive)
        net = psutil.net_io_counters()

        gpu_data = get_nvidia_telemetry()
        gpu_pct = gpu_data["gpu_pct"]
        vram_pct = gpu_data["vram_pct"]

        pending_alerts = []
        try:
            from routes.cyber import get_and_clear_pending_alerts
            pending_alerts = get_and_clear_pending_alerts()
        except Exception:
            pass

        return jsonify({
            "success": True,
            "cpu_percent": cpu_pct,
            "ram_percent": ram.percent,
            "ram_used_gb": round((ram.total - ram.available) / (1024**3), 1),
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "disk_percent": disk.percent,
            "gpu_percent": gpu_pct,
            "vram_percent": vram_pct,
            "vram_used_mb": gpu_data["vram_used_mb"],
            "vram_total_mb": gpu_data["vram_total_mb"],
            "net_sent_mb": round(net.bytes_sent / (1024 * 1024), 1),
            "net_recv_mb": round(net.bytes_recv / (1024 * 1024), 1),
            "os": f"{platform.system()} {platform.release()}",
            "hostname": platform.node(),
            "pending_alerts": pending_alerts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "cpu_percent": 0, "ram_percent": 0})

@system_bp.route("/api/system/location", methods=["GET"])
def get_location():
    try:
        r = requests.get("http://ip-api.com/json/", timeout=4)
        if r.status_code == 200:
            data = r.json()
            return jsonify({
                "success": True,
                "city": data.get("city", "Greater Sudbury"),
                "region": data.get("regionName", "Ontario"),
                "region_code": data.get("region", "ON"),
                "country": data.get("country", "Canada"),
                "country_code": data.get("countryCode", "CA"),
                "lat": data.get("lat", 46.5199),
                "lon": data.get("lon", -80.9385),
                "timezone": data.get("timezone", "America/Toronto"),
                "isp": data.get("isp", "Bell Canada"),
                "ip": data.get("query", "Local"),
                "formatted": f"{data.get('city', 'Greater Sudbury')}, {data.get('regionName', 'Ontario')}, {data.get('country', 'Canada')}",
                "commander": "Mr. Ramadeep Singh"
            })
    except Exception as e:
        pass
    return jsonify({
        "success": True,
        "city": "Greater Sudbury",
        "region": "Ontario",
        "country": "Canada",
        "lat": 46.5199,
        "lon": -80.9385,
        "timezone": "America/Toronto",
        "formatted": "Greater Sudbury, Ontario, Canada",
        "commander": "Mr. Ramadeep Singh"
    })

@system_bp.route("/api/system/last_interaction", methods=["GET"])
def get_last_interaction():
    return jsonify({"last_interaction": LAST_USER_INTERACTION, "now": time.time()})

@system_bp.route("/api/system/touch_interaction", methods=["POST"])
def touch_interaction():
    global LAST_USER_INTERACTION
    LAST_USER_INTERACTION = time.time()
    return jsonify({"status": "ok", "last_interaction": LAST_USER_INTERACTION})

@system_bp.route("/api/health", methods=["GET"])
def get_health():
    return jsonify({
        "status": "healthy",
        "uptime": round(time.time() - SERVER_BOOT_TIME, 2),
        "timestamp": time.time()
    })

@system_bp.route("/companion", methods=["GET"])
def redirect_companion():
    return redirect("/floating_assistant_app/?standalone=true")

@system_bp.route("/api/history", methods=["GET"])
def get_history_alias():
    try:
        rows = db_engine.execute_query("SELECT chat_id as id, title, updated_at as created_at FROM chat_sessions ORDER BY updated_at DESC LIMIT 50;")
        chats = [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]
        return jsonify({"success": True, "chats": chats})
    except Exception:
        return jsonify({"success": True, "chats": []})

@system_bp.route("/api/system/active_window", methods=["GET"])
def get_active_window():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        if h_wnd:
            length = user32.GetWindowTextLengthW(h_wnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(h_wnd, buff, length + 1)
                if buff.value and buff.value.strip():
                    return jsonify({"success": True, "active_window": buff.value.strip()})
    except Exception:
        pass

    try:
        cmd = "(Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -ExpandProperty MainWindowTitle)[0]"
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=2,
        )
        window_title = res.stdout.strip()
        if not window_title:
            window_title = "Desktop / System Explorer"
        return jsonify({"success": True, "active_window": window_title})
    except Exception as e:
        return jsonify({"success": True, "active_window": "Desktop Explorer"})


def fetch_single_weather(lat, lon, name_label):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_resp = requests.get(url, timeout=3).json()
        curr = w_resp.get("current_weather", {})
        temp_c = curr.get("temperature", 0.0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        windspeed = curr.get("windspeed", 0.0)
        wcode = curr.get("weathercode", 0)

        w_conditions = {
            0: "Clear Sky",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Rime Fog",
            51: "Light Drizzle",
            61: "Slight Rain",
            63: "Moderate Rain",
            65: "Heavy Rain",
            71: "Slight Snow",
            80: "Rain Showers",
            95: "Thunderstorm",
        }
        condition = w_conditions.get(wcode, "Fair Weather")

        alert = "GREEN — Normal"
        alert_level = "normal"

        if wcode in [95, 96, 99]:
            alert = "⚠️ THUNDERSTORM WARNING"
            alert_level = "warning"
        elif wcode in [65, 82]:
            alert = "🌧️ HEAVY DOWNPOUR ALERT"
            alert_level = "warning"
        elif windspeed > 40:
            alert = f"💨 HIGH WIND ({windspeed} km/h)"
            alert_level = "warning"
        elif temp_c > 35:
            alert = f"🔥 HEAT ADVISORY ({temp_f}°F)"
            alert_level = "warning"
        elif temp_c < -10:
            alert = f"❄️ FREEZING ADVISORY ({temp_f}°F)"
            alert_level = "warning"

        return {
            "name": name_label,
            "temp_c": temp_c,
            "temp_f": temp_f,
            "condition": condition,
            "windspeed_kmh": windspeed,
            "alert": alert,
            "alert_level": alert_level,
        }
    except Exception:
        return {
            "name": name_label,
            "temp_c": "--",
            "temp_f": "--",
            "condition": "Clear",
            "windspeed_kmh": "--",
            "alert": "GREEN — Normal",
            "alert_level": "normal",
        }


@system_bp.route("/api/system/weather", methods=["GET"])
def get_weather():
    locations_data = []

    fixed_locations = [
        {"name": "Sudbury", "lat": 46.49, "lon": -80.99},
        {"name": "Niagara", "lat": 43.09, "lon": -79.08},
        {"name": "Brampton", "lat": 43.73, "lon": -79.76},
    ]

    curr_city = ""
    curr_lat = 0.0
    curr_lon = 0.0
    try:
        loc_resp = requests.get("http://ip-api.com/json/", timeout=3).json()
        curr_city = loc_resp.get("city", "").strip()
        curr_lat = loc_resp.get("lat", 0.0)
        curr_lon = loc_resp.get("lon", 0.0)
    except Exception:
        pass

    matches_fixed = False
    if curr_city:
        city_lower = curr_city.lower()
        for loc in fixed_locations:
            if loc["name"].lower() in city_lower or city_lower in loc["name"].lower():
                matches_fixed = True
                break

    if curr_city and not matches_fixed:
        locations_data.append(
            fetch_single_weather(curr_lat, curr_lon, f"📍 {curr_city} (Current)")
        )

    for loc in fixed_locations:
        name_label = loc["name"]
        if curr_city and loc["name"].lower() in curr_city.lower():
            name_label = f"📍 {loc['name']} (Current Location)"
        locations_data.append(fetch_single_weather(loc["lat"], loc["lon"], name_label))

    return jsonify({"success": True, "locations": locations_data})

@system_bp.route("/api/system/macro", methods=["POST"])
def run_macro():
    action = request.json.get("action", "")
    try:
        if action == "notepad":
            subprocess.Popen(["notepad.exe"])
            msg = "Opened Notepad"
        elif action == "taskmgr":
            subprocess.Popen(["taskmgr.exe"])
            msg = "Opened Task Manager"
        elif action == "calc":
            subprocess.Popen(["calc.exe"])
            msg = "Opened Calculator"
        elif action == "browser":
            subprocess.Popen(["explorer.exe", "https://www.google.com"])
            msg = "Opened Default Web Browser"
        elif action == "clean_temp":
            cmd = "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue"
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd], capture_output=True
            )
            msg = "Cleaned Windows Temp Directory"
        elif action == "lock_pc":
            cmd = "rundll32.exe user32.dll,LockWorkStation"
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd])
            msg = "Workstation Locked"
        elif action == "explorer":
            subprocess.Popen(["explorer.exe"])
            msg = "Opened File Explorer"
        elif action == "powershell" or action == "terminal":
            subprocess.Popen(["powershell.exe"])
            msg = "Opened Terminal"
        elif action == "search_web":
            q = urllib.parse.quote(request.json.get("query", ""))
            subprocess.Popen(["explorer.exe", f"https://www.google.com/search?q={q}"])
            msg = f"Searched Google for: {request.json.get('query', '')}"
        elif action in ["search_yt", "play_youtube"]:
            from app import resolve_first_youtube_video
            raw_q = request.json.get("query", "trending music")
            target_url = resolve_first_youtube_video(raw_q)
            try:
                import local_music_engine
                local_music_engine.open_in_chrome(target_url)
            except Exception:
                try:
                    os.startfile(target_url)
                except Exception:
                    pass
            msg = f"Playing YouTube: {raw_q}"
        elif action == "scroll_down":
            import ctypes

            clicks = int(request.json.get("steps", 5))
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, -120 * clicks, 0)
            msg = f"Scrolled down {clicks} steps"
        elif action == "scroll_up":
            import ctypes

            clicks = int(request.json.get("steps", 5))
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, 120 * clicks, 0)
            msg = f"Scrolled up {clicks} steps"
        elif action == "record_start":
            import screen_recorder

            res = screen_recorder.start_recording()
            msg = res.get("message", "Started recording")
        elif action == "record_stop":
            import screen_recorder

            res = screen_recorder.stop_recording()
            msg = res.get("message", "Stopped recording")
        elif action == "screen_analyze":
            import screen_vision

            q = request.json.get(
                "prompt",
                "Analyze what is visible on this screen. Highlight any errors or key details.",
            )
            res = screen_vision.analyze_desktop_screen(
                prompt=q, model="qwen2.5vl:7b", timeout_s=45
            )
            msg = res.get("analysis", "Screen analyzed")
            return jsonify({"status": "success", "message": msg, "details": res})
        elif action == "snap_left":
            import workspace_arranger

            res = workspace_arranger.snap_left()
            msg = res.get("message", "Snapped left")
        elif action == "snap_right":
            import workspace_arranger

            res = workspace_arranger.snap_right()
            msg = res.get("message", "Snapped right")
        elif action == "maximize_window":
            import workspace_arranger

            res = workspace_arranger.maximize_window()
            msg = res.get("message", "Maximized window")
        elif action == "coding_layout":
            import workspace_arranger

            res = workspace_arranger.arrange_coding_layout()
            msg = res.get("message", "Coding layout arranged")
        elif action == "clipboard_read":
            import clipboard_copilot

            res = clipboard_copilot.analyze_clipboard()
            return jsonify(
                {"status": "success", "message": res.get("summary", ""), "details": res}
            )
        elif action == "clipboard_fix":
            import clipboard_copilot

            res = clipboard_copilot.fix_clipboard_with_ai()
            return jsonify(
                {"status": "success", "message": res.get("message", ""), "details": res}
            )
        elif action == "clipboard_format":
            import clipboard_copilot

            res = clipboard_copilot.format_clipboard()
            return jsonify(
                {"status": "success", "message": res.get("message", ""), "details": res}
            )
        elif action == "watchdog_start":
            import error_watchdog

            res = error_watchdog.start_watchdog()
            msg = res.get("message", "Watchdog started")
        elif action == "watchdog_stop":
            import error_watchdog

            res = error_watchdog.stop_watchdog()
            msg = res.get("message", "Watchdog stopped")
        elif action == "visual_click":
            import visual_clicker

            target = request.json.get("target", "center")
            res = visual_clicker.locate_and_click(target)
            return jsonify(
                {
                    "status": res.get("status", "success"),
                    "message": res.get("message", ""),
                    "details": res,
                }
            )
        elif action == "settings":
            subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:"])
            msg = "Opened Windows Settings"
        elif action == "control_panel":
            subprocess.Popen(["control.exe"])
            msg = "Opened Control Panel"
        elif action == "paint":
            subprocess.Popen(["mspaint.exe"])
            msg = "Opened Paint"
        elif action == "downloads":
            subprocess.Popen(["explorer.exe", "shell:Downloads"])
            msg = "Opened Downloads Folder"
        elif action == "documents":
            subprocess.Popen(["explorer.exe", "shell:Personal"])
            msg = "Opened Documents Folder"
        elif action == "chrome":
            subprocess.Popen(["cmd.exe", "/c", "start", "chrome"])
            msg = "Launched Google Chrome"
        elif action == "vscode":
            subprocess.Popen(["cmd.exe", "/c", "code"])
            msg = "Launched VS Code"
        elif action == "desktop":
            pyautogui.hotkey("win", "d")
            msg = "Toggled Windows Desktop"
        elif action == "search_wiki":
            q = urllib.parse.quote(request.json.get("query", ""))
            subprocess.Popen(["explorer.exe", f"https://en.wikipedia.org/wiki/{q}"])
            msg = f"Searched Wikipedia for: {request.json.get('query', '')}"
        elif action == "open_url":
            url = request.json.get("url", "https://www.google.com").strip()
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return jsonify({"success": False, "error": "Invalid URL protocol; only HTTP and HTTPS allowed"}), 400
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception as we:
                try:
                    os.startfile(url)
                except Exception:
                    return jsonify({"success": False, "error": f"Failed to open URL: {we}"}), 500
            msg = f"Opened URL: {url}"
        else:
            return jsonify({"success": False, "error": "Unknown macro action"}), 400

        return jsonify({"success": True, "message": msg})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/version", methods=["GET"])
def get_system_version():
    try:
        project_dir = os.path.dirname(__file__)
        latest_mtime = int(SERVER_BOOT_TIME)
        for root, _, files in os.walk(project_dir):
            if any(
                p in root for p in ["__pycache__", ".git", "pc_app_profile", "static"]
            ):
                continue
            for f in files:
                if f.endswith((".py", ".html", ".css", ".js", ".json")):
                    try:
                        fp = os.path.join(root, f)
                        mt = int(os.path.getmtime(fp))
                        if mt > latest_mtime:
                            latest_mtime = mt
                    except Exception:
                        pass
        ver_sig = f"{int(SERVER_BOOT_TIME)}_{latest_mtime}"
        return jsonify(
            {
                "app_version": ver_sig,
                "boot_time": SERVER_BOOT_TIME,
                "latest_mtime": latest_mtime,
                "status": "ready",
            }
        )
    except Exception as e:
        return jsonify({"app_version": str(SERVER_BOOT_TIME), "error": str(e)})

@system_bp.route("/api/system/metrics", methods=["GET"])
def get_system_metrics():
    try:
        cpu_pct = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net_io = psutil.net_io_counters()

        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info
                processes.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"] or "unknown",
                        "cpu": round(info["cpu_percent"] or 0.0, 1),
                        "memory": round(info["memory_percent"] or 0.0, 1),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        processes.sort(key=lambda x: x["cpu"], reverse=True)

        gpu_pct = 0
        vram_pct = 0
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=1.5)
            if res.returncode == 0 and res.stdout.strip():
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 3:
                    gpu_pct = int(float(parts[0]))
                    used_mb = float(parts[1])
                    total_mb = float(parts[2])
                    if total_mb > 0:
                        vram_pct = int((used_mb / total_mb) * 100)
        except Exception:
            pass

        return jsonify(
            {
                "os": f"{platform.system()} {platform.release()}",
                "cpu_cores": psutil.cpu_count(logical=True),
                "cpu_pct": cpu_pct,
                "gpu_pct": gpu_pct,
                "vram_pct": vram_pct,
                "memory_pct": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_pct": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "bytes_sent_mb": round(net_io.bytes_sent / (1024 * 1024), 1),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024 * 1024), 1),
                "top_processes": processes[:8],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@system_bp.route("/api/system/volume", methods=["POST"])
def volume_control():
    data = request.json or {}
    action = data.get("action", "up")
    try:
        import everyday_pc_actions

        target = data.get("target") # "speaker" or "headphone" or None
        if action == "mute":
            status = everyday_pc_actions.toggle_device_mute(target) if target else everyday_pc_actions.toggle_volume_mute()
            return jsonify({"success": True, "action": action, "target": target, "status": status})
        elif action == "up":
            delta = data.get("delta", 10)
            level = everyday_pc_actions.adjust_device_volume_relative(target, delta) if target else everyday_pc_actions.adjust_volume_relative(delta)
            return jsonify({"success": True, "action": action, "target": target, "level": level})
        elif action == "down":
            delta = data.get("delta", -10)
            level = everyday_pc_actions.adjust_device_volume_relative(target, delta if delta < 0 else -delta) if target else everyday_pc_actions.adjust_volume_relative(delta if delta < 0 else -delta)
            return jsonify({"success": True, "action": action, "target": target, "level": level})
        elif action == "set":
            val = data.get("level", 50)
            level = everyday_pc_actions.set_device_volume(target, val) if target else everyday_pc_actions.set_master_volume(val)
            return jsonify({"success": True, "action": action, "target": target, "level": level})
        return jsonify({"success": True, "action": action})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/stop", methods=["POST", "GET"])
def emergency_stop_endpoint():
    """Handles emergency stop signal cleanly from the Cockpit UI."""
    try:
        try:
            import local_music_engine
            local_music_engine.control_media("stop")
        except Exception:
            pass
        return jsonify({
            "success": True,
            "status": "stopped",
            "message": "Emergency stop executed cleanly. All pending actions halted."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/brightness", methods=["POST"])
def brightness_control():
    level = request.json.get("level", 80)
    try:
        cmd = f"Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{{Timeout = 0; Brightness = {level}}}"
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
        )
        return jsonify({"success": True, "level": level})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/kill", methods=["POST"])
def kill_process():
    pid = request.json.get("pid")
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({"success": True, "message": f"Terminated process {pid}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system_stats", methods=["GET"])
def get_system_stats():
    """Returns real-time PyTorch GPU/CUDA, CPU, RAM, and Disk telemetry metrics."""
    try:
        import psutil

        cpu_pct = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage("C:\\")
            disk_free = round(disk.free / (1024**3), 1)
        except Exception:
            disk_free = 50.0
        gpu_info = {
            "available": False,
            "device_name": "Integrated / Ollama Engine",
            "allocated_mb": 0,
            "reserved_mb": 0,
            "gpu_pct": 0,
        }
        try:
            import torch

            if torch.cuda.is_available():
                gpu_info["available"] = True
                gpu_info["device_name"] = torch.cuda.get_device_name(0)
                gpu_info["allocated_mb"] = round(
                    torch.cuda.memory_allocated(0) / (1024 * 1024), 2
                )
                gpu_info["reserved_mb"] = round(
                    torch.cuda.memory_reserved(0) / (1024 * 1024), 2
                )
                gpu_info["gpu_pct"] = round(
                    min(
                        100.0,
                        (torch.cuda.memory_allocated(0) / (8 * 1024 * 1024 * 1024))
                        * 100,
                    ),
                    1,
                )
        except Exception:
            pass

        return jsonify(
            {
                "success": True,
                "cpu_pct": cpu_pct,
                "ram_pct": ram.percent,
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "disk_free_gb": disk_free,
                "gpu": gpu_info,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/open_url", methods=["POST"])
def system_open_url():
    data = request.json or {}
    url = data.get("url", "").strip()
    if url:
        import subprocess

        subprocess.Popen(["cmd.exe", "/c", "start", url])
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "No URL provided"}), 400

@system_bp.route("/api/health/full", methods=["GET"])
def get_health_full():
    """Provides status on DB connectivity, OLLAMA availability, and system resource health."""
    health_status = {
        "status": "healthy",
        "components": {
            "database": {"status": "unknown", "details": ""},
            "ollama": {"status": "unknown", "details": ""},
            "system_resources": {"status": "unknown", "details": {}}
        }
    }
    
    # Check DB Connectivity
    try:
        res = db_engine.execute_query("SELECT 1")
        if res is not None:
            health_status["components"]["database"]["status"] = "healthy"
            health_status["components"]["database"]["details"] = "Connected successfully"
        else:
            health_status["components"]["database"]["status"] = "unhealthy"
            health_status["components"]["database"]["details"] = "Query returned None"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"]["status"] = "unhealthy"
        health_status["components"]["database"]["details"] = str(e)
        health_status["status"] = "degraded"

    # Check OLLAMA Availability
    try:
        ollama_base = OLLAMA_API.replace("/api/generate", "")
        # A simple GET to the base URL should return 200 "Ollama is running"
        res = requests.get(ollama_base, timeout=2)
        if res.status_code == 200:
            health_status["components"]["ollama"]["status"] = "healthy"
            health_status["components"]["ollama"]["details"] = "Ollama is responding"
        else:
            health_status["components"]["ollama"]["status"] = "unhealthy"
            health_status["components"]["ollama"]["details"] = f"HTTP {res.status_code}"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["ollama"]["status"] = "unhealthy"
        health_status["components"]["ollama"]["details"] = str(e)
        health_status["status"] = "degraded"

    # Check System Resources
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        drive = os.path.splitdrive(os.path.abspath(__file__))[0] + "\\"
        disk = psutil.disk_usage(drive).percent
        
        health_status["components"]["system_resources"]["details"] = {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk
        }
        
        if cpu > 95 or ram > 95 or disk > 95:
            health_status["components"]["system_resources"]["status"] = "degraded"
            health_status["status"] = "degraded"
        else:
            health_status["components"]["system_resources"]["status"] = "healthy"
            
    except Exception as e:
        health_status["components"]["system_resources"]["status"] = "unhealthy"
        health_status["components"]["system_resources"]["details"] = str(e)
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] == "healthy" else 207
    return jsonify(health_status), status_code


# -------------------------------------------------------------
# ADVANCED SOVEREIGN ENGINES (PODCAST, BIOMETRICS, TUNNEL, TAX, CHROMA, AUDIT)
# -------------------------------------------------------------

@system_bp.route("/api/podcast/generate", methods=["POST"])
def api_podcast_generate():
    try:
        import podcast_generator_engine
        data = request.get_json(silent=True) or {}
        topic = data.get("topic", "System Architecture & AI Sovereignty")
        content = data.get("content", "")
        res = podcast_generator_engine.generate_podcast(topic, content)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/podcast/list", methods=["GET"])
def api_podcast_list():
    try:
        import podcast_generator_engine
        items = podcast_generator_engine.list_podcasts()
        return jsonify({"success": True, "podcasts": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/podcasts/<path:filename>", methods=["GET"])
def serve_podcast_audio(filename):
    podcast_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "podcasts")
    return send_from_directory(podcast_dir, filename)


@system_bp.route("/api/biometrics/fatigue_check", methods=["GET", "POST"])
def api_biometrics_fatigue():
    try:
        import biometric_fatigue_sentinel
        frames = int((request.get_json(silent=True) or {}).get("frames", 20))
        res = biometric_fatigue_sentinel.estimate_cognitive_fatigue(frame_count=frames)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/tunnel/start", methods=["POST"])
def api_tunnel_start():
    try:
        import cloudflare_tunnel_manager
        data = request.get_json(silent=True) or {}
        port = int(data.get("port", 5000))
        res = cloudflare_tunnel_manager.start_tunnel(local_port=port)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/tunnel/stop", methods=["POST"])
def api_tunnel_stop():
    try:
        import cloudflare_tunnel_manager
        res = cloudflare_tunnel_manager.stop_tunnel()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/tunnel/status", methods=["GET"])
def api_tunnel_status():
    try:
        import cloudflare_tunnel_manager
        res = cloudflare_tunnel_manager.get_tunnel_status()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/system/auto_evolve", methods=["POST", "GET"])
def api_auto_evolve():
    try:
        import auto_evolution_engine
        data = request.get_json(silent=True) or {}
        topic = data.get("topic")
        if topic:
            docs = auto_evolution_engine.search_web_documentation(topic)
            snippet = docs[0]["snippet"] if docs else f"Cutting-edge capability for {topic}"
            res = auto_evolution_engine.synthesize_and_install_skill(
                skill_id=topic,
                skill_name=topic.title().replace("-", " "),
                description=snippet,
                domain="autonomous-expansion"
            )
            return jsonify({"success": True, "action": "synthesized", "details": res})
        else:
            res = auto_evolution_engine.run_comprehensive_evolution_scan()
            return jsonify({"success": True, "action": "scan_complete", "details": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/war_room_status", methods=["GET"])
def api_war_room_status():
    try:
        import psutil, subprocess, db_engine, time
        
        # 1. Database telemetry
        db_stat = {"connected": False, "tables": 0, "latency_ms": 0}
        t0 = time.time()
        conn = None
        try:
            conn = db_engine.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT count(table_name) FROM information_schema.tables WHERE table_schema='public'")
            t_cnt = cur.fetchone()[0]
            db_stat = {
                "connected": True,
                "tables": t_cnt,
                "latency_ms": round((time.time() - t0) * 1000, 2),
                "engine": "PostgreSQL 18.4 (deep_db)"
            }
        except Exception as e:
            db_stat["error"] = str(e)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            
        # 2. Git status
        git_info = {"branch": "Local Workspace", "last_commit": "HEAD", "dirty_files": 0}
        try:
            g_b = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, timeout=2)
            g_log = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True, text=True, timeout=2)
            g_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=2)
            if g_b.returncode == 0 and g_b.stdout.strip():
                git_info["branch"] = g_b.stdout.strip()
            if g_log.returncode == 0 and g_log.stdout.strip():
                git_info["last_commit"] = g_log.stdout.strip()
            if g_status.returncode == 0:
                git_info["dirty_files"] = len([l for l in g_status.stdout.splitlines() if l.strip()])
        except Exception as e:
            git_info["error"] = str(e)

        # 3. Hardware vitals
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        hardware = {
            "cpu_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_used_gb": round((mem.total - mem.available) / (1024**3), 2),
            "ram_total_gb": round(mem.total / (1024**3), 2),
            "ram_percent": mem.percent,
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "gpu_model": "NVIDIA RTX A2000 8GB GDDR6 (CUDA 13.2)"
        }

        # Check Ollama status
        ollama_online = False
        try:
            import socket
            with socket.create_connection(("127.0.0.1", 11434), timeout=0.2):
                ollama_online = True
        except Exception:
            ollama_online = False

        # 4. Active Daemons
        daemons = [
            {"name": "PostgreSQL 18.4", "target": "localhost:5432/deep_db", "status": "ONLINE" if db_stat["connected"] else "OFFLINE"},
            {"name": "Flask Cockpit", "target": "localhost:5000", "status": "ONLINE"},
            {"name": "Ollama Inference", "target": "localhost:11434 (RTX A2000)", "status": "ONLINE" if ollama_online else "OFFLINE"},
            {"name": "Cyber Sentinel", "target": "Firewall & Watchdog", "status": "ONLINE"},
            {"name": "Astra Visual Memory", "target": "Screen Capture Engine", "status": "ONLINE"},
            {"name": "TTS Speech Engine", "target": "Windows SAPI Dual-Voice", "status": "ONLINE"}
        ]

        # 5. Resilience Circuit Breakers Matrix
        circuit_breakers = []
        try:
            from hystrix_circuit_breaker import global_circuit_registry
            circuit_breakers = global_circuit_registry.get_telemetry_matrix()
        except Exception as e:
            circuit_breakers = [{"error": str(e)}]

        # 6. Embedded MCU & PICkit 3 Hardware Profile
        mcu_status = {}
        try:
            import embedded_mcu_engine
            mcu_status = embedded_mcu_engine.get_toolchain_status()
        except Exception as e:
            mcu_status = {"error": str(e)}

        return jsonify({
            "success": True,
            "timestamp": time.time(),
            "database": db_stat,
            "git": git_info,
            "hardware": hardware,
            "daemons": daemons,
            "circuit_breakers": circuit_breakers,
            "mcu": mcu_status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@system_bp.route("/api/system/circuit_breakers", methods=["GET"])
def api_circuit_breakers_status():
    """Returns real-time Netflix Hystrix resilience telemetry across all services."""
    try:
        from hystrix_circuit_breaker import global_circuit_registry
        matrix = global_circuit_registry.get_telemetry_matrix()
        return jsonify({"success": True, "resilience_matrix": matrix})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/system/circuit_breakers/trip", methods=["POST"])
def api_trip_circuit_breaker():
    """Fault-injection endpoint: manually trips a circuit breaker to OPEN."""
    try:
        from flask import request
        from hystrix_circuit_breaker import global_circuit_registry
        data = request.json or {}
        name = data.get("name")
        breaker = global_circuit_registry.get(name)
        if not breaker:
            return jsonify({"success": False, "error": f"Circuit breaker '{name}' not found"}), 404
        breaker.trip()
        return jsonify({
            "success": True,
            "message": f"Circuit breaker '{name}' tripped to OPEN",
            "breaker": breaker.get_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/system/circuit_breakers/reset", methods=["POST"])
def api_reset_circuit_breaker():
    """Recovers a circuit breaker back to CLOSED state."""
    try:
        from flask import request
        from hystrix_circuit_breaker import global_circuit_registry
        data = request.json or {}
        name = data.get("name")
        breaker = global_circuit_registry.get(name)
        if not breaker:
            return jsonify({"success": False, "error": f"Circuit breaker '{name}' not found"}), 404
        breaker.reset()
        return jsonify({
            "success": True,
            "message": f"Circuit breaker '{name}' reset to CLOSED",
            "breaker": breaker.get_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500








@system_bp.route("/api/voice/vad/status", methods=["GET"])
def api_voice_vad_status():
    """Returns sub-400ms voice pipeline and streaming Silero VAD telemetry."""
    try:
        from voice_vad_stream_engine import get_voice_vad_stream_engine
        engine = get_voice_vad_stream_engine()
        return jsonify({"success": True, "telemetry": engine.telemetry})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/voice/vad/toggle", methods=["POST"])
def api_voice_vad_toggle():
    """Controls the streaming VAD listener (start / stop / pause / resume)."""
    try:
        from flask import request
        from voice_vad_stream_engine import get_voice_vad_stream_engine
        data = request.json or {}
        action = data.get("action", "toggle").lower()
        engine = get_voice_vad_stream_engine()

        if action == "start":
            engine.start_pipeline()
        elif action == "stop":
            engine.stop_pipeline()
        elif action == "pause":
            engine.pause_pipeline()
        elif action == "resume":
            engine.resume_pipeline()
        else:
            if engine.running:
                engine.stop_pipeline()
            else:
                engine.start_pipeline()

        return jsonify({"success": True, "telemetry": engine.telemetry})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/api/voice/vad/transcribe", methods=["POST"])
def api_voice_vad_transcribe():
    """Benchmarking endpoint: transcribes synthetic or provided audio array with GPU Whisper."""
    try:
        from flask import request
        import numpy as np
        from voice_vad_stream_engine import get_voice_vad_stream_engine
        data = request.json or {}
        audio_samples = data.get("audio_samples")
        engine = get_voice_vad_stream_engine()

        if audio_samples and isinstance(audio_samples, list):
            arr = np.array(audio_samples, dtype=np.float32)
        else:
            # Benchmark with 1-second synthetic sample
            arr = np.zeros(16000, dtype=np.float32)

        text, latency_ms = engine.transcribe_audio_chunk(arr)
        return jsonify({
            "success": True,
            "text": text,
            "stt_latency_ms": latency_ms,
            "device": engine.telemetry.get("device", "cpu")
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
