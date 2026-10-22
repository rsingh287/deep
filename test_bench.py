import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8")
BASE_URL = "http://127.0.0.1:5000"


def test_1_fast_model():
    print("\n--- ⚡ SCENARIO 1: Fast Model (qwen2.5:7b) ---")
    t0 = time.time()
    try:
        res = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "prompt": "Write 1 line of Python code to print Hello World",
                "model": "qwen2.5:7b",
            },
            timeout=30,
        ).json()
        dur = time.time() - t0
        print(f"✅ Success in {dur:.2f}s | Model: {res.get('model_used')}")
        print(f"Output: {res.get('response', '').strip()[:150]}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_2_auto_router():
    print("\n--- 🤖 SCENARIO 2: Intelligent Auto Router ('auto') ---")
    t0 = time.time()
    try:
        res = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "prompt": "Explain quantum computing in 1 short sentence.",
                "model": "auto",
            },
            timeout=30,
        ).json()
        dur = time.time() - t0
        print(f"✅ Success in {dur:.2f}s | Auto Selected: {res.get('model_used')}")
        print(f"Output: {res.get('response', '').strip()[:150]}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_3_swarm_mode():
    print("\n--- 🐝 SCENARIO 3: Multi-Agent Swarm Mode (Architect + Auditor) ---")
    t0 = time.time()
    try:
        res = requests.post(
            f"{BASE_URL}/api/swarm_chat",
            json={"prompt": "Give 1 tip for secure Python coding."},
            timeout=120,
        ).json()
        dur = time.time() - t0
        print(f"✅ Success in {dur:.2f}s | Swarm Status: {res.get('success')}")
        print(f"Output:\n{res.get('response', '').strip()[:300]}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_1_fast_model()
    test_2_auto_router()
    test_3_swarm_mode()
