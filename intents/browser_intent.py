from .base_intent import BaseIntent

class BrowserPilotIntent(BaseIntent):
    KEYWORDS = [
        "open a browser and", "go to website and", "scroll through website",
        "live browser", "browser pilot", "browser agent"
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(phrase in norm_prompt for phrase in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import browser_use_agent
            from langchain_ollama import ChatOllama
            
            print(f"[BrowserAgent] Intercepted browser intent. Executing...", flush=True)
            
            import os
            ollama_base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            if not ollama_base.startswith("http://") and not ollama_base.startswith("https://"):
                ollama_base = f"http://{ollama_base}"
            llm = ChatOllama(model="qwen2.5:7b", base_url=ollama_base)
            result = browser_use_agent.run_browser_task(llm, user_prompt)

            if isinstance(result, dict) and result.get("status") == "error":
                err_msg = result.get("message", "Browser task failed.")
                return (
                    f"❌ **Live Browser Pilot Error:** {err_msg}",
                    "browser_agent",
                    []
                )

            out_str = str(result.get("result", result)) if isinstance(result, dict) else str(result)
            
            print(f"[BrowserAgent] Execution successful.", flush=True)
            return (
                f"**Live Browser Pilot Executed:**\n\n{out_str}",
                "browser_agent",
                [{"language": "python", "code": f"browser_use_agent.run_browser_task(llm, {repr(user_prompt)})", "output": "Execution Complete"}]
            )
        except Exception as e:
            import traceback
            print(f"[BrowserAgent] Error: {e}", flush=True)
            traceback.print_exc()
            return (
                f"❌ **Live Browser Pilot Error:** Failed to execute browser task: {e}",
                "browser_agent",
                []
            )
