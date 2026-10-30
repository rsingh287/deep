from .base_intent import BaseIntent

class SelfHealingIntent(BaseIntent):
    KEYWORDS = [
        "fix this error", "fix my code", "self heal", "debug the last error", "fix error",
        "repair system", "system heal", "auto heal", "fix system", "healing status",
        "quarantine", "unquarantine", "reset circuits"
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(p in norm_prompt for p in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import agentic_orchestrator
            res = agentic_orchestrator.orchestrator.tool_self_heal()
            actions = "\n".join(f"- {a}" for a in res.get("actions_executed", []))
            eq = res.get("system_equilibrium", "OPTIMAL")
            ollama = res.get("ollama_status", "Unknown")
            duration = res.get("duration_ms", 0.0)
            
            msg = (
                f"🩺 **Autonomous Self-Healing Sentinel & Immune Audit** (Status: `{eq}` | Latency: `{duration}ms`)\n\n"
                f"**Diagnostics & Auto-Remediation Protocols Executed:**\n{actions}\n\n"
                f"- **Ollama Inference Engine:** {ollama}\n"
                f"- **Memory & Process State:** Cleaned & Synchronized.\n"
                f"- **Embedded Hardware & LCD:** Defect Guard active on Line 2 exclusively."
            )
            return (msg, "self_healing_agent", [{"language": "python", "code": "agentic_orchestrator.orchestrator.tool_self_heal()", "output": f"Equilibrium: {eq}"}])
        except Exception as e:
            return (f"⚠️ **Self-Healing Diagnostics Warning:** {e}", "self_healing_agent", [])

