"""
Deep 3D AI Workstation - Native PC Desktop Application
Launches Deep as a standalone native Windows desktop application with direct hardware access.
"""

import os
import subprocess
import sys
import time
import urllib.request

APP_PORT = 5000
APP_URL = f"http://127.0.0.1:{APP_PORT}/"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def is_server_running():
    try:
        with urllib.request.urlopen(
            f"{APP_URL}api/system/metrics", timeout=1.5
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_backend_server():
    if is_server_running():
        print(f"[PC App] Backend server is already running on {APP_URL}")
        return None

    print("[PC App] Starting Local AI Cockpit backend server (app.py)...")
    app_script = os.path.join(PROJECT_DIR, "app.py")
    python_exe = sys.executable

    proc = subprocess.Popen(
        [python_exe, app_script],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    max_wait = 15.0
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_server_running():
            print(f"[PC App] Backend server is ready on {APP_URL}!")
            return proc
        time.sleep(0.5)

    print(
        "[PC App Warning] Server took longer than expected to report ready, proceeding anyway."
    )
    return proc


def launch_via_pywebview():
    try:
        import webview

        print("[PC App] Launching via PyWebView (Microsoft Edge WebView2 Engine)...")
        webview.settings["ALLOW_FILE_URLS"] = True
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True

        window = webview.create_window(
            title="Deep - 3D AI Workstation Cockpit",
            url=APP_URL,
            width=450,
            height=750,
            background_color="#030712",
            resizable=True,
        )
        webview.start(gui="edgechromium", debug=False)
        return True
    except Exception as e:
        print(f"[PC App] PyWebView encountered an issue: {e}")
        return False


def launch_via_edge_app_mode():
    print("[PC App] Launching via Windows Native Edge App Mode...")
    edge_candidates = [
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    ]

    edge_exe = None
    for p in edge_candidates:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print(
            "[PC App Warning] No native browser engine found for App Mode. Opening default browser."
        )
        import webbrowser

        webbrowser.open(APP_URL)
        return

    profile_dir = os.path.join(PROJECT_DIR, "pc_app_profile")
    os.makedirs(profile_dir, exist_ok=True)

    cmd = [
        edge_exe,
        f"--app={APP_URL}",
        "--window-size=450,750",
        "--window-position=50,30",
        f"--user-data-dir={profile_dir}",
        "--enable-features=HardwareMediaKeyHandling",
        "--use-fake-ui-for-media-stream",  # Automatically grant microphone hardware access!
        "--no-first-run",
        "--no-default-browser-check",
    ]

    subprocess.Popen(cmd)
    print("[PC App] Dedicated Windows PC App window opened successfully!")


def main():
    print("=" * 60)
    print("  DEEP 3D AI WORKSTATION - PC DESKTOP APPLICATION")
    print("=" * 60)

    ensure_backend_server()

    mode = "edge_app" if len(sys.argv) < 2 else sys.argv[1]
    if mode == "pywebview":
        success = launch_via_pywebview()
        if not success:
            launch_via_edge_app_mode()
    else:
        launch_via_edge_app_mode()


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    main()
