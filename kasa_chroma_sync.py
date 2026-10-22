import asyncio
import os
import time
import kasa_controller

SCENE_PROFILES = {
    "voice_active": {
        "color": "cyan",
        "brightness": 85,
        "description": "Electric Cyan glow indicating D.E.E.P acoustic engagement"
    },
    "deep_focus": {
        "color": "warm white",
        "brightness": 55,
        "description": "Warm amber 2700K focus atmosphere for coding and research"
    },
    "defense_alert": {
        "color": "red",
        "brightness": 100,
        "description": "Crimson pulse indicating DEFCON / security interception"
    },
    "aurora_glow": {
        "color": "green",
        "brightness": 70,
        "description": "Emerald boreal radiance for northern space weather alerts"
    },
    "daylight": {
        "color": "white",
        "brightness": 95,
        "description": "Crisp balanced 4500K daylight workspace illumination"
    }
}


def trigger_chroma_scene(scene_name: str) -> dict:
    """Executes a dynamic ambient lighting scene on connected TP-Link Kasa smart bulbs."""
    scene_key = scene_name.lower().strip()
    profile = SCENE_PROFILES.get(scene_key, SCENE_PROFILES["voice_active"])

    try:
        color = profile["color"]
        brightness = profile["brightness"]

        # Run async color and brightness adjustment
        res = asyncio.run(kasa_controller.set_kasa_light_color(color_name=color, brightness=brightness))

        return {
            "success": True,
            "scene": scene_key,
            "profile": profile,
            "kasa_response": res,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "success": False,
            "scene": scene_key,
            "profile": profile,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def get_available_scenes() -> dict:
    """Returns catalog of all reactive room lighting presets."""
    return SCENE_PROFILES


if __name__ == "__main__":
    print("Testing Kasa Chroma Sync Presets...")
    print("Catalog:", list(get_available_scenes().keys()))
    res = trigger_chroma_scene("voice_active")
    print("Trigger result:", res["success"], res.get("scene"))
