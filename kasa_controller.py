"""
===================================================================
ANTIGRAVITY AI WORKSTATION: TP-LINK KASA SMART HOME LIGHTING ENGINE
===================================================================
Direct local Wi-Fi control for Kasa Smart Plugs, Bulbs & Light Strips.
"""

import asyncio
import re
import sys
import time

try:
    from kasa import Discover

    KASA_INSTALLED = True
except ImportError:
    KASA_INSTALLED = False

DEFAULT_KASA_IP = "192.168.2.240"
BROADCAST_TARGET = "192.168.2.255"


async def _get_device_fast():
    """Locates Kasa device on local Wi-Fi quickly and ensures state is fully updated."""
    dev = None
    for ip in [DEFAULT_KASA_IP, "192.168.2.126"]:
        try:
            dev = await Discover.discover_single(ip, timeout=1.2)
            if dev:
                break
        except Exception:
            pass

    if not dev:
        try:
            devs = await Discover.discover(target=BROADCAST_TARGET, timeout=1.5)
            if devs:
                dev = list(devs.values())[0]
        except Exception:
            pass

    if not dev:
        try:
            devs_all = await Discover.discover(timeout=1.5)
            if devs_all:
                dev = list(devs_all.values())[0]
        except Exception:
            pass

    if dev:
        try:
            await dev.update()
        except Exception:
            pass

    return dev


async def toggle_kasa_light(action="toggle", brightness=100):
    """Turn ON, OFF, or change brightness for a Kasa light/plug."""
    if not KASA_INSTALLED:
        return {"success": False, "error": "python-kasa not installed."}

    try:
        dev = await _get_device_fast()
        if not dev:
            return {
                "success": False,
                "error": "Could not reach TP-Link Kasa device on local Wi-Fi network.",
            }

        # Perform action directly and update target state explicitly
        is_on_val = False
        if action == "on":
            await dev.turn_on()
            is_on_val = True
        elif action == "off":
            await dev.turn_off()
            is_on_val = False
        elif action == "toggle":
            currently_on = getattr(dev, "is_on", False)
            if currently_on:
                await dev.turn_off()
                is_on_val = False
            else:
                await dev.turn_on()
                is_on_val = True
        elif action == "status":
            is_on_val = getattr(dev, "is_on", False)

        if hasattr(dev, "set_brightness") and brightness and is_on_val:
            try:
                await dev.set_brightness(brightness)
            except Exception:
                pass

        try:
            await dev.update()
        except Exception:
            pass

        alias_clean = (
            getattr(dev, "alias", "Deeps Room").encode("ascii", "ignore").decode()
            or "Deeps Room"
        )
        return {
            "success": True,
            "alias": alias_clean,
            "ip": getattr(dev, "host", DEFAULT_KASA_IP),
            "is_on": is_on_val,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


COLOR_HUES = {
    # Primary & Secondary Colors
    "red": (0, 100),
    "crimson": (348, 100),
    "scarlet": (9, 100),
    "ruby": (340, 100),
    "maroon": (0, 100),
    "coral": (16, 100),
    "peach": (20, 80),
    "orange": (30, 100),
    "amber": (25, 100),
    "tangerine": (35, 100),
    "gold": (45, 100),
    "yellow": (60, 100),
    "lemon": (55, 100),
    "lime": (90, 100),
    "chartreuse": (75, 100),
    "green": (120, 100),
    "emerald": (140, 100),
    "mint": (150, 80),
    "forest green": (120, 100),
    "olive": (80, 100),
    "cyan": (180, 100),
    "teal": (165, 100),
    "turquoise": (175, 100),
    "aqua": (180, 100),
    "sky blue": (195, 90),
    "ice blue": (200, 60),
    "blue": (240, 100),
    "royal blue": (225, 100),
    "navy": (240, 100),
    "deep blue": (240, 100),
    "indigo": (265, 100),
    "purple": (280, 100),
    "violet": (270, 100),
    "amethyst": (270, 90),
    "plum": (290, 90),
    "magenta": (300, 100),
    "fuchsia": (300, 100),
    "pink": (320, 90),
    "rose": (330, 90),
    "hot pink": (330, 100),
    "lavender": (255, 60),
    # White Tones & Temperatures
    "white": (0, 0),
    "warm white": (35, 20),
    "cool white": (200, 15),
    "daylight": (0, 0),
    "soft white": (30, 15),
}


async def set_kasa_light_color(color_name="orange", brightness=100):
    """Sets the color of a Kasa smart light bulb or strip using HSV values."""
    if not KASA_INSTALLED:
        return {"success": False, "error": "python-kasa not installed."}

    try:
        dev = await _get_device_fast()
        if not dev:
            return {
                "success": False,
                "error": "Could not reach TP-Link Kasa device on local Wi-Fi.",
            }

        color_clean = color_name.lower().strip()
        hue, sat = COLOR_HUES.get(
            color_clean, (30, 100)
        )  # Default to orange (30) if unknown

        if not getattr(dev, "is_on", False):
            await dev.turn_on()

        light_mod = dev.modules.get("Light") if hasattr(dev, "modules") else None
        if light_mod and hasattr(light_mod, "set_hsv"):
            await light_mod.set_hsv(hue, sat, brightness)
        elif hasattr(dev, "set_hsv"):
            await dev.set_hsv(hue, sat, brightness)
        elif hasattr(dev, "set_color_temp"):
            await dev.set_color_temp(
                2700 if "warm" in color_clean or "orange" in color_clean else 6500
            )

        # Force immediate hardware sync
        try:
            await dev.update()
        except Exception:
            pass

        alias_clean = (
            getattr(dev, "alias", "Deeps Room").encode("ascii", "ignore").decode()
            or "Deeps Room"
        )
        return {
            "success": True,
            "alias": alias_clean,
            "color": color_clean,
            "is_on": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def set_kasa_brightness(level=100, mode="set"):
    """Adjusts brightness of Kasa smart light bulb or strip."""
    if not KASA_INSTALLED:
        return {"success": False, "error": "python-kasa not installed."}

    try:
        dev = await _get_device_fast()
        if not dev:
            return {
                "success": False,
                "error": "Could not reach TP-Link Kasa device on local Wi-Fi.",
            }

        if not getattr(dev, "is_on", False):
            await dev.turn_on()

        light_mod = dev.modules.get("Light") if hasattr(dev, "modules") else None
        current_b = (
            getattr(light_mod, "brightness", None)
            if light_mod
            else getattr(dev, "brightness", 100)
        )

        target_b = level
        if mode == "dim":
            if level and level != 100:
                target_b = level
            elif current_b and current_b > 50:
                target_b = 30
            elif current_b and current_b > 20:
                target_b = 10
            else:
                target_b = 25
        elif mode == "bright":
            if level and level != 100 and level != 30:
                target_b = level
            else:
                target_b = 100

        target_b = max(1, min(100, target_b))

        if light_mod and hasattr(light_mod, "set_brightness"):
            await light_mod.set_brightness(target_b)
        elif hasattr(dev, "set_brightness"):
            await dev.set_brightness(target_b)

        try:
            await dev.update()
        except Exception:
            pass

        alias_clean = (
            getattr(dev, "alias", "Deeps Room").encode("ascii", "ignore").decode()
            or "Deeps Room"
        )
        return {
            "success": True,
            "alias": alias_clean,
            "brightness": target_b,
            "is_on": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


LAST_LIGHT_COMMAND_TIME = 0.0


def set_last_light_context():
    global LAST_LIGHT_COMMAND_TIME
    LAST_LIGHT_COMMAND_TIME = time.time()


def is_recent_light_context():
    return (time.time() - LAST_LIGHT_COMMAND_TIME) < 300


def execute_kasa_intent(prompt: str):
    """Parses user prompt and executes smart light power, color, or brightness action immediately with typo tolerance & conversation context."""
    p = prompt.lower().strip()

    # Reject non-light queries like flight searches, flight tickets, etc.
    if any(
        w in p for w in ["flight", "flights", "fly", "airline", "ticket", "boarding"]
    ):
        return None

    # Keywords indicating a light/lighting context using word boundary matching
    light_keywords = [
        "light",
        "lights",
        "ligth",
        "ligts",
        "ligh",
        "room light",
        "kasa",
        "lamp",
        "bulb",
        "lighting",
        "deeps room",
    ]
    explicit_light = any(
        re.search(r"\b" + re.escape(k) + r"\b", p) for k in light_keywords
    )
    recent_light = is_recent_light_context()
    has_light_context = explicit_light or recent_light

    if explicit_light:
        set_last_light_context()

    # 1. Check for Color Target (sorted by length descending so multi-word colors match first)
    color_target = None
    sorted_colors = sorted(COLOR_HUES.keys(), key=len, reverse=True)
    for c in sorted_colors:
        if re.search(r"\b" + re.escape(c) + r"\b", p):
            color_target = c
            break

    # Extract percentage or number if specifying level (e.g. 75%, 75 percent, to 75, at 75, level 75, 75)
    percent_match = (
        re.search(r"(\d{1,3})\s*(?:%|percent)", p)
        or re.search(
            r"\b(?:to|at|level|brightness|set to|reduce to|drop to|put to)\s*(\d{1,3})\b",
            p,
        )
        or re.search(r"\b(?:light|lights|room light)\s+(?:to\s+)?(\d{1,3})\b", p)
        or re.search(
            r"\b(?:reduce|decrease|lower|dim|set|adjust|make|turn)\s+(?:it\s+)?(?:to\s+)?(\d{1,3})\b",
            p,
        )
    )
    extracted_pct = None
    if percent_match:
        for group in percent_match.groups():
            if group and group.isdigit() and 1 <= int(group) <= 100:
                extracted_pct = int(group)
                break

    action = None
    if color_target and (
        has_light_context
        or any(w in p for w in ["change", "set", "make", "turn", "switch", "to"])
    ):
        action = "color"
    elif (
        not color_target
        and has_light_context
        and any(
            phrase in p
            for phrase in [
                "change color",
                "change colour",
                "set color",
                "set colour",
                "pick color",
                "pick colour",
            ]
        )
    ):
        action = "color"
        color_target = "orange"

    # 2. Check for Brightness / Dimming commands
    if not action:
        if re.search(
            r"\b(dim|dimmer|less light|lower light|decrease light|darker|reduce light|soft light|reduce it|dim it|lower it|decrease it|reduce to|dim to|lower to|decrease to)\b",
            p,
        ) or (
            extracted_pct
            and any(
                w in p for w in ["reduce", "decrease", "lower", "dim", "drop", "down"]
            )
        ):
            action = "dim"
        elif re.search(
            r"\b(bright|brighten|brighter|more light|increase light|max light|full light|higher light|boost light|bright the light|increase it|brighter it|boost it)\b",
            p,
        ) or (
            extracted_pct
            and any(w in p for w in ["increase", "boost", "raise", "higher", "bright"])
        ):
            action = "bright"
        elif extracted_pct and has_light_context:
            action = "brightness"

    if not action:
        if (
            re.search(
                r"\b(turn off|lights off|light off|ligth off|off light|switch off|make it dark|turn light off|room light turn off|turn it off|switch it off|shut it off|shut off)\b",
                p,
            )
            and has_light_context
        ):
            action = "off"
        elif (
            re.search(
                r"\b(turn on|lights on|light on|ligth on|on light|switch on|turn light on|room light turn on|turn it on|switch it on)\b",
                p,
            )
            and has_light_context
        ):
            action = "on"
        elif re.search(r"\b(toggle|switch)\b", p) and has_light_context:
            action = "toggle"
        elif has_light_context and re.search(r"\b(status|check|state)\b", p):
            action = "status"

    if not action:
        return None

    set_last_light_context()

    res = {}
    if action == "color":
        for attempt in range(2):
            res = asyncio.run(set_kasa_light_color(color_name=color_target))
            if res.get("success"):
                break
            time.sleep(0.5)
        if res.get("success"):
            return f"Light color set to {color_target}.", res
        else:
            return f"Error: {res.get('error')}", res
    elif action in ["dim", "bright", "brightness"]:
        target_mode = (
            "dim" if action == "dim" else ("bright" if action == "bright" else "set")
        )
        target_val = (
            extracted_pct if extracted_pct else (30 if action == "dim" else 100)
        )
        for attempt in range(2):
            res = asyncio.run(set_kasa_brightness(level=target_val, mode=target_mode))
            if res.get("success"):
                break
            time.sleep(0.5)
        if res.get("success"):
            return f"Light brightness adjusted to {target_val}%.", res
        else:
            return f"Error: {res.get('error')}", res
    else:
        for attempt in range(2):
            res = asyncio.run(toggle_kasa_light(action=action))
            if res.get("success"):
                break
            time.sleep(0.5)

        if res.get("success"):
            return f"Room lights {action} successfully.", res
        else:
            return f"Error: {res.get('error')}", res


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) > 1:
        prompt_arg = " ".join(sys.argv[1:])
        kasa_res = execute_kasa_intent(prompt_arg)
        if kasa_res:
            msg, res = kasa_res
            print(msg)
        else:
            print("No smart light intent matched.")
    else:
        print(asyncio.run(toggle_kasa_light(action="status")))
