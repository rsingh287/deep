import os
import re
import sys
import time
import subprocess
import threading
import requests

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(PROJECT_ROOT, "scratch")
CLOUDFLARED_PATH = os.path.join(TOOLS_DIR, "cloudflared.exe")

_TUNNEL_PROC = None
_TUNNEL_URL = None
_TUNNEL_START_TIME = None
_TUNNEL_LOGS = []


def ensure_cloudflared() -> str:
    """Checks if cloudflared exists; downloads official standalone binary if missing."""
    if os.path.exists(CLOUDFLARED_PATH):
        return CLOUDFLARED_PATH

    # Check system PATH
    try:
        res = subprocess.run(["where.exe", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().splitlines()[0]
    except Exception:
        pass

    # Download official Cloudflare standalone Windows binary
    print("[CloudflareTunnel] Downloading official cloudflared-windows-amd64.exe...")
    download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    try:
        r = requests.get(download_url, stream=True, timeout=30)
        if r.status_code == 200:
            os.makedirs(TOOLS_DIR, exist_ok=True)
            with open(CLOUDFLARED_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("[CloudflareTunnel] Successfully downloaded cloudflared.exe.")
            return CLOUDFLARED_PATH
    except Exception as e:
        print(f"[CloudflareTunnel] Download failed: {e}")

    return None


def _monitor_tunnel_output(proc):
    global _TUNNEL_URL
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(proc.stderr.readline, ""):
        if not line:
            break
        line_clean = line.strip()
        _TUNNEL_LOGS.append(line_clean)
        if len(_TUNNEL_LOGS) > 100:
            _TUNNEL_LOGS.pop(0)

        match = url_pattern.search(line_clean)
        if match and not _TUNNEL_URL:
            _TUNNEL_URL = match.group(0)
            print(f"\n[CloudflareTunnel] Remote HTTPS Tunnel Active: {_TUNNEL_URL}\n")


def start_tunnel(local_port: int = 5000) -> dict:
    """Spawns an ephemeral Cloudflare Tunnel pointing to the local port."""
    global _TUNNEL_PROC, _TUNNEL_URL, _TUNNEL_START_TIME, _TUNNEL_LOGS

    if _TUNNEL_PROC is not None and _TUNNEL_PROC.poll() is None:
        return {
            "success": True,
            "status": "already_running",
            "url": _TUNNEL_URL,
            "port": local_port,
            "uptime_seconds": int(time.time() - _TUNNEL_START_TIME) if _TUNNEL_START_TIME else 0
        }

    cf_bin = ensure_cloudflared()
    if not cf_bin or not os.path.exists(cf_bin):
        return {
            "success": False,
            "error": "cloudflared binary unavailable. Please ensure internet access to download."
        }

    _TUNNEL_URL = None
    _TUNNEL_LOGS = []
    _TUNNEL_START_TIME = time.time()

    cmd = [cf_bin, "tunnel", "--url", f"http://localhost:{local_port}", "--no-autoupdate"]
    try:
        _TUNNEL_PROC = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Thread to read stderr for the trycloudflare URL
        thread = threading.Thread(target=_monitor_tunnel_output, args=(_TUNNEL_PROC,), daemon=True)
        thread.start()

        # Wait up to 8 seconds for URL extraction
        for _ in range(16):
            if _TUNNEL_URL:
                break
            time.sleep(0.5)

        return {
            "success": True,
            "status": "running",
            "url": _TUNNEL_URL or "Negotiating Cloudflare edge...",
            "port": local_port,
            "message": f"Secure encrypted tunnel established to http://localhost:{local_port}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def stop_tunnel() -> dict:
    """Gracefully terminates active Cloudflare Tunnel."""
    global _TUNNEL_PROC, _TUNNEL_URL, _TUNNEL_START_TIME

    if _TUNNEL_PROC is None or _TUNNEL_PROC.poll() is not None:
        _TUNNEL_URL = None
        return {"success": True, "status": "stopped", "message": "No active tunnel was running."}

    try:
        _TUNNEL_PROC.terminate()
        _TUNNEL_PROC.wait(timeout=3)
    except Exception:
        try:
            _TUNNEL_PROC.kill()
        except Exception:
            pass

    _TUNNEL_PROC = None
    last_url = _TUNNEL_URL
    _TUNNEL_URL = None
    _TUNNEL_START_TIME = None

    return {
        "success": True,
        "status": "stopped",
        "message": f"Cloudflare Tunnel disconnected ({last_url})"
    }


def get_tunnel_status() -> dict:
    """Returns current tunnel state, URL, and uptime."""
    is_running = _TUNNEL_PROC is not None and _TUNNEL_PROC.poll() is None
    uptime = int(time.time() - _TUNNEL_START_TIME) if (is_running and _TUNNEL_START_TIME) else 0

    return {
        "success": True,
        "is_active": is_running,
        "url": _TUNNEL_URL if is_running else None,
        "uptime_seconds": uptime,
        "recent_logs": _TUNNEL_LOGS[-10:] if _TUNNEL_LOGS else []
    }


if __name__ == "__main__":
    print("Testing Cloudflare Tunnel Controller status...")
    print(get_tunnel_status())
