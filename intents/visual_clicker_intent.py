from .base_intent import BaseIntent

class VisualClickerIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return "click on" in norm_prompt or "click " in norm_prompt

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import visual_clicker
            target = norm_prompt.split("click ")[-1].replace("on", "").strip()
            res = visual_clicker.locate_and_click(target)
            return (f"Visual Operator executed click on '{target}'. Result: {res}", "qwen2.5vl:7b", [{"language": "python", "code": f"visual_clicker.locate_and_click('{target}')", "output": str(res)}])
        except Exception as e:
            pass
        return None
