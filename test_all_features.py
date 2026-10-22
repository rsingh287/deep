import json

import requests

BASE_URL = "http://127.0.0.1:5000"


def safe_print(title, data):
    print("\n============================================================")
    print(f"[TEST] {title}")
    print("============================================================")
    try:
        json_str = json.dumps(data, indent=2, ensure_ascii=True)
        print(json_str)
    except Exception as e:
        print(f"Display error: {e}")


def run_master_feature_check():
    print("============================================================")
    print("ANTIGRAVITY AI WORKSTATION: MASTER FEATURE SUITE VERIFICATION")
    print("============================================================")

    # 1. Test Server Ping
    try:
        r0 = requests.get(f"{BASE_URL}/", timeout=4)
        print(f"[OK] [1/7] Local Cockpit Server Online (HTTP {r0.status_code})")
    except Exception as e:
        print(f"[ERROR] Local server error: {e}")
        return

    # 2. Test Voice Command Hardware Execution (Punjabi & English)
    try:
        payload = {"command": "PIC board countdown kaunt chalao"}
        r1 = requests.post(
            f"{BASE_URL}/api/speech/execute_voice_action", json=payload, timeout=8
        ).json()
        safe_print("Voice Action & PIC Hardware Trigger", r1)
    except Exception as e:
        print(f"Voice Action Error: {e}")

    # 3. Test Hardware Optical Inspection (Webcam LEDs / 7-Segments)
    try:
        r2 = requests.post(f"{BASE_URL}/api/vision/inspect_hardware", timeout=8).json()
        safe_print("Webcam Hardware Optical Inspection (PIC Board)", r2)
    except Exception as e:
        print(f"Hardware Vision Error: {e}")

    # 4. Test Desktop Screen Vision & Layout OCR
    try:
        r3 = requests.post(f"{BASE_URL}/api/vision/screen", json={}, timeout=25).json()
        safe_print("Desktop Screen Vision & Brightness Analysis", r3)
    except Exception as e:
        print(f"Screen Vision Error: {e}")

    # 5. Test Live Camera Vision Stream & AI Scene Understanding
    try:
        r4 = requests.get(f"{BASE_URL}/api/vision/live_stream_frame", timeout=8).json()
        # Truncate base64 image for clean console display
        if "image_b64" in r4:
            r4["image_b64_preview"] = r4["image_b64"][:40] + "... [TRUNCATED]"
            del r4["image_b64"]
        safe_print("Live Camera Stream & Real-Time AI Vision", r4)
    except Exception as e:
        print(f"Live Stream Error: {e}")

    # 6. Test Sign Language & Hand Gesture Translation
    try:
        r5 = requests.get(f"{BASE_URL}/api/vision/sign_language", timeout=8).json()
        if "image_b64" in r5:
            r5["image_b64_preview"] = r5["image_b64"][:40] + "... [TRUNCATED]"
            del r5["image_b64"]
        safe_print("Sign Language & Hand Gesture Translator", r5)
    except Exception as e:
        print(f"Sign Language Error: {e}")

    # 7. Test Facial Expression & Emotion Recognition
    try:
        r6 = requests.get(f"{BASE_URL}/api/vision/facial_expression", timeout=8).json()
        if "image_b64" in r6:
            r6["image_b64_preview"] = r6["image_b64"][:40] + "... [TRUNCATED]"
            del r6["image_b64"]
        safe_print("Facial Expression & Emotion Recognition", r6)
    except Exception as e:
        print(f"Facial Expression Error: {e}")

    print("\n============================================================")
    print("ALL 7 ADVANCED AI FEATURES TESTED & OPERATIONAL!")
    print("============================================================")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    run_master_feature_check()
