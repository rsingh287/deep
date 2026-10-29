import re
from .base_intent import BaseIntent

class VisualClickerIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        if len(norm_prompt.split()) > 10:
            return False
        return bool(re.match(r"^(please\s+)?click\s+(on\s+)?", norm_prompt.strip()))

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import visual_clicker
            target = re.sub(r"^.*?click\s+(?:on\s+)?", "", norm_prompt, flags=re.IGNORECASE).strip()
            if not target:
                target = "center"
            res = visual_clicker.locate_and_click(target)
            if isinstance(res, dict) and res.get("status") == "error":
                return (f"❌ **Visual Clicker Error:** {res.get('message', 'Failed to click element')}", "qwen2.5vl:7b", [{"language": "python", "code": f"visual_clicker.locate_and_click({repr(target)})", "output": str(res)}])
            return (f"🎯 **Visual Operator:** Executed click on '{target}'. Result: {res.get('message', 'Success')}", "qwen2.5vl:7b", [{"language": "python", "code": f"visual_clicker.locate_and_click({repr(target)})", "output": str(res)}])
        except Exception as e:
            print(f"[VisualClickerIntent] Error: {e}")
            return (f"❌ **Visual Clicker Error:** {e}", "qwen2.5vl:7b", [])
