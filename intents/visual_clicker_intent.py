import re
from typing import Tuple, List, Dict, Any
from .base_intent import BaseIntent

class VisualClickerIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        words = norm_prompt.strip().split()
        if len(words) > 15:
            return False
        p = norm_prompt.strip()
        # Matches: click (on), double click (on), right click (on), hover (over), type ... into ...
        patterns = [
            r"^(please\s+)?(double\s+)?click\s+(on\s+)?",
            r"^(please\s+)?right\s+click\s+(on\s+)?",
            r"^(please\s+)?hover\s+(over\s+)?",
            r"^(please\s+)?type\s+.+\s+into\s+",
        ]
        return any(bool(re.match(pat, p)) for pat in patterns)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        try:
            import visual_clicker

            p = norm_prompt.strip()
            action = "click"
            clicks = 1
            button = "left"
            text_to_type = None
            target = "center"

            # 1. Type into pattern: "type hello into search bar"
            type_m = re.match(r"^(?:please\s+)?type\s+['\"]?(.+?)['\"]?\s+into\s+['\"]?(.+?)['\"]?$", p)
            if type_m:
                action = "type"
                text_to_type = type_m.group(1).strip()
                target = type_m.group(2).strip()
            # 2. Right click pattern: "right click on recycle bin"
            elif re.match(r"^(?:please\s+)?right\s+click\s+(?:on\s+)?", p):
                action = "right_click"
                button = "right"
                target = re.sub(r"^(?:please\s+)?right\s+click\s+(?:on\s+)?", "", p).strip()
            # 3. Double click pattern: "double click on visual studio"
            elif re.match(r"^(?:please\s+)?double\s+click\s+(?:on\s+)?", p):
                action = "double_click"
                clicks = 2
                target = re.sub(r"^(?:please\s+)?double\s+click\s+(?:on\s+)?", "", p).strip()
            # 4. Hover pattern: "hover over mute button"
            elif re.match(r"^(?:please\s+)?hover\s+(?:over\s+)?", p):
                action = "hover"
                target = re.sub(r"^(?:please\s+)?hover\s+(?:over\s+)?", "", p).strip()
            # 5. Standard click pattern: "click on mute button"
            else:
                target = re.sub(r"^(?:please\s+)?click\s+(?:on\s+)?", "", p).strip()

            if not target:
                target = "center"

            res = visual_clicker.locate_and_click(
                target_element=target,
                action=action,
                clicks=clicks,
                button=button,
                text_to_type=text_to_type
            )

            if isinstance(res, dict) and res.get("status") in ("error", "grounding_failed"):
                return (
                    f"❌ **Visual Grounding Error:** {res.get('message', 'Failed to execute action')}",
                    "qwen2.5vl:7b",
                    [{"language": "python", "code": f"visual_clicker.locate_and_click({repr(target)}, action={repr(action)})", "output": str(res)}]
                )

            msg = res.get("message", "Visual action executed.")
            coords_info = f"({res.get('x')}, {res.get('y')})" if "x" in res else ""
            return (
                f"🎯 **VLM Visual Operator:** {msg} {coords_info}",
                "qwen2.5vl:7b",
                [{"language": "python", "code": f"visual_clicker.locate_and_click({repr(target)}, action={repr(action)})", "output": str(res)}]
            )
        except Exception as e:
            print(f"[VisualClickerIntent] Error: {e}")
            return (f"❌ **Visual Clicker Error:** {e}", "qwen2.5vl:7b", [])
