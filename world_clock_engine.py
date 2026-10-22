import datetime

import pytz

CITIES_TZ = {
    "toronto": "America/Toronto",
    "new york": "America/New_York",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "dubai": "Asia/Dubai",
    "los angeles": "America/Los_Angeles",
    "san francisco": "America/Los_Angeles",
    "utc": "UTC",
}


def get_world_clock():
    now_utc = datetime.datetime.now(pytz.utc)
    lines = []

    cities = [
        ("Toronto / New York (EDT/EST)", "America/Toronto"),
        ("London (BST/GMT)", "Europe/London"),
        ("Paris / Berlin (CEST/CET)", "Europe/Paris"),
        ("Dubai (GST)", "Asia/Dubai"),
        ("India (IST)", "Asia/Kolkata"),
        ("Tokyo (JST)", "Asia/Tokyo"),
        ("Sydney (AEST)", "Australia/Sydney"),
        ("San Francisco (PDT/PST)", "America/Los_Angeles"),
    ]

    for label, tz_str in cities:
        tz = pytz.timezone(tz_str)
        city_time = now_utc.astimezone(tz)
        formatted = city_time.strftime("%Y-%m-%d %I:%M:%S %p (%Z)")
        lines.append(f"- **{label}**: `{formatted}`")

    return f"### 🌐 Live Global World Clock Telemetry\n" + "\n".join(lines)


def handle_world_clock_intent(prompt: str):
    p_low = prompt.lower().strip()

    triggers = [
        "world clock",
        "global time",
        "what time",
        "time in",
        "clock in",
        "timezone",
        "time for",
    ]
    if not any(k in p_low for k in triggers):
        return None

    for city_key, tz_str in CITIES_TZ.items():
        if city_key in p_low:
            tz = pytz.timezone(tz_str)
            city_time = datetime.datetime.now(pytz.utc).astimezone(tz)
            formatted = city_time.strftime("%Y-%m-%d %I:%M:%S %p (%Z)")
            return (
                f"### 🕒 Current Local Time: **{city_key.title()}**\n- **Live Time**: `{formatted}`\n- **Timezone**: `{tz_str}`",
                "autonomous_world_clock_engine",
                [
                    {
                        "language": "python",
                        "code": f"get_time('{city_key}')",
                        "output": f"Fetched {city_key} time",
                    }
                ],
            )

    return (
        get_world_clock(),
        "autonomous_world_clock_engine",
        [
            {
                "language": "python",
                "code": "get_world_clock()",
                "output": "Fetched World Clock Telemetry",
            }
        ],
    )
