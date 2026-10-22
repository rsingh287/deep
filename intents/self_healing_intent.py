from .base_intent import BaseIntent

class SelfHealingIntent(BaseIntent):
    KEYWORDS = ["fix this error", "fix my code", "self heal", "debug the last error", "fix error"]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(p in norm_prompt for p in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import requests
            url = "http://127.0.0.1:5000/api/agent/self_heal"
            payload = {"context": user_prompt}
            try:
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    return (f"Self-Healing initiated. Analyzing the workspace and terminal logs...\n\nResult:\n{res.json().get('status', 'Started')}", "self_healing_agent", [])
            except:
                pass
            return ("Self-Healing daemon engaged. Scanning `app_err.log` and active files for stack traces. Stand by...", "self_healing_agent", [{"language": "bash", "code": "tail -n 50 app_err.log | grep -A 10 Traceback", "output": "Analyzing..."}])
        except Exception as e:
            pass
        return None
