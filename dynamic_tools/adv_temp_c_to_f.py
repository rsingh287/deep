from functools import lru_cache
def run(args: dict) -> dict:
    if not isinstance(args, dict):
        return {"error": "Invalid args", "success": False}
    c = float(args.get("celsius", 0.0))
    f = (c * 9.0 / 5.0) + 32.0
    return {"celsius": c, "fahrenheit": round(f, 2), "success": True}

