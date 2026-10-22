from .base_intent import BaseIntent
import time

class OSAutomatorIntent(BaseIntent):
    KEYWORDS = ["open app", "minimize all", "maximize window", "press key", "type text"]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(p in norm_prompt for p in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import pyautogui
            if "minimize all" in norm_prompt:
                pyautogui.hotkey('win', 'd')
                return ("Minimized all windows.", "os_automator", [{"language": "python", "code": "pyautogui.hotkey('win', 'd')", "output": "Success"}])
            elif "press key" in norm_prompt:
                key = norm_prompt.split("press key")[-1].strip()
                pyautogui.press(key)
                return (f"Pressed key: {key}", "os_automator", [{"language": "python", "code": f"pyautogui.press('{key}')", "output": "Success"}])
            elif "type text" in norm_prompt:
                text = norm_prompt.split("type text")[-1].strip()
                pyautogui.write(text, interval=0.05)
                return (f"Typed text: {text}", "os_automator", [{"language": "python", "code": f"pyautogui.write('{text}')", "output": "Success"}])
            elif "open app" in norm_prompt:
                app_name = norm_prompt.split("open app")[-1].strip()
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.05)
                time.sleep(0.5)
                pyautogui.press('enter')
                return (f"Opened application: {app_name}", "os_automator", [{"language": "python", "code": "pyautogui Windows Search automation", "output": "Success"}])
        except Exception as e:
            print(f"[OS Automator] Error: {e}")
        return None
