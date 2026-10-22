from .base_intent import BaseIntent

class ScreenVisionIntent(BaseIntent):
    KEYWORDS = ["what is on my screen", "read my screen", "look at my screen"]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(k in norm_prompt for k in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import screen_vision
            res = screen_vision.analyze_desktop_screen("Analyze the desktop and describe what is visible.")
            return (f"Visual Desktop Analysis:\n{res['analysis']}", "qwen2.5vl:7b", [{"language": "python", "code": "screen_vision.analyze_desktop_screen()", "output": str(res)}])
        except Exception as e:
            pass
        return None
