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
            
            llm = ChatOllama(model="qwen2.5:7b")
            result = browser_use_agent.run_browser_task(llm, user_prompt)
            out_str = str(result.get("result", result))
            
            print(f"[BrowserAgent] Execution successful.", flush=True)
            return (
                f"**Live Browser Pilot Executed:**\n\n{out_str}",
                "browser_agent",
                [{"language": "python", "code": f"browser_use_agent.run_browser_task(llm, '{user_prompt}')", "output": "Execution Complete"}]
            )
        except Exception as e:
            import traceback
            print(f"[BrowserAgent] Error: {e}", flush=True)
            traceback.print_exc()
        return None
