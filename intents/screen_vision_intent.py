from .base_intent import BaseIntent

class ScreenVisionIntent(BaseIntent):
    KEYWORDS = [
        "what is on my screen",
        "whats on my screen",
        "what is on screen",
        "whats on screen",
        "read my screen",
        "read screen",
        "look at my screen",
        "look at screen",
        "analyze my screen",
        "analyze screen",
        "check my screen",
        "inspect my screen",
        "describe my screen",
        "screen vision",
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(k in norm_prompt for k in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import screen_vision
            res = screen_vision.analyze_desktop_screen("Analyze the desktop and describe what is visible.")
            if isinstance(res, dict):
                if res.get("status") == "error":
                    err_msg = res.get("message", "Unknown screen vision error")
                    return (f"❌ **Screen Vision Error:** {err_msg}", "qwen2.5vl:7b", [{"language": "python", "code": "screen_vision.analyze_desktop_screen()", "output": str(res)}])
                analysis_text = res.get("analysis", "Desktop captured and analyzed.")
                return (f"🖥️ **Visual Desktop Analysis:**\n\n{analysis_text}", res.get("model_used", "qwen2.5vl:7b"), [{"language": "python", "code": "screen_vision.analyze_desktop_screen()", "output": str(res)}])
            return ("🖥️ **Visual Desktop Analysis:** Screen captured successfully.", "qwen2.5vl:7b", [])
        except Exception as e:
            print(f"[ScreenVisionIntent] Error: {e}")
            return (f"❌ **Screen Vision Error:** {e}", "qwen2.5vl:7b", [])
