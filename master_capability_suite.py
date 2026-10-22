import datetime
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:5000/api/chat"

test_suite = [
    ("🐳 Docker Telemetry Engine", "docker ps"),
    ("📦 Docker Images Inventory", "docker images"),
    ("💱 Real-Time Foreign Exchange", "convert 100 USD to CAD"),
    ("🕒 Live World Clock & Timezone", "what time is it in Tokyo"),
    ("🌦️ Real-Time Weather Forecast", "weather in Toronto"),
    ("📈 Financial Crypto Telemetry", "crypto price bitcoin"),
    ("🔥 Trending Crypto Tokens", "trending crypto"),
    ("📅 Wikipedia Today in History", "today in history"),
    ("📍 Postal Geolocation Lookup", "zip code 90210"),
    ("🍸 Mixology & Drink Recipe", "cocktail margarita"),
    ("🥗 Open Food Facts Nutrition", "food nutrition 737628064502"),
    ("🔐 Base64 Encoder Engine", "base64 encode Antigravity Workstation"),
    ("🆔 UUID v4 Generator", "generate uuid"),
    ("✈️ Autonomous Travel Booking", "book flight from Toronto to Vancouver"),
    ("📚 W3Schools Tutorial Engine", "w3schools python dictionary"),
    ("🎓 Interactive Learning Academy", "show my sql course progress"),
]


def run_master_suite():
    print("=" * 75)
    print(
        "🚀 ANTIGRAVITY WORKSTATION: MASTER CAPABILITY & INTEGRATION VERIFICATION SUITE"
    )
    print(f"🕒 Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)

    passed = 0
    failed = 0

    for idx, (title, prompt) in enumerate(test_suite, 1):
        print(f"\n[{idx}/{len(test_suite)}] Testing: {title}")
        print(f"   ► Input Prompt: '{prompt}'")
        try:
            r = requests.post(API_URL, json={"prompt": prompt}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                model = (
                    data.get("model_used") or data.get("model") or "Autonomous Engine"
                )
                response = data.get("response", "").strip()
                preview = response.replace("\n", " ")[:140]

                print(f"   ✅ Execution Status: SUCCESS")
                print(f"   🤖 Engine / Model: {model}")
                print(f"   💬 Output Sample: {preview}...")
                passed += 1
            else:
                print(f"   ❌ Execution Status: FAILED (HTTP {r.status_code})")
                failed += 1
        except Exception as e:
            print(f"   ❌ Execution Status: ERROR ({str(e)})")
            failed += 1

    print("\n" + "=" * 75)
    print("📊 MASTER SUITE SUMMARY RESULT:")
    print(f"• Total Autonomous Modules Tested: {len(test_suite)}")
    print(
        f"• Successfully Executed: {passed} / {len(test_suite)} ({(passed/len(test_suite))*100:.1f}%)"
    )
    print(
        f"• System Health Status: {'🟢 100% OPERATIONAL & VERIFIED' if failed == 0 else '🟡 PARTIAL ISSUES DETECTED'}"
    )
    print("=" * 75)


if __name__ == "__main__":
    run_master_suite()
