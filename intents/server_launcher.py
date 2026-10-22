from .base_intent import BaseIntent
import os
import subprocess

class ServerLauncherIntent(BaseIntent):
    KEYWORDS = ["start deep ai server", "launch deep ai server", "open deep ai server", "run deep ai server"]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(p in norm_prompt for p in cls.KEYWORDS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            bat_path = r"c:\Users\User\Desktop\Start DEEP AI Server.bat"
            if os.path.exists(bat_path):
                subprocess.Popen(["cmd.exe", "/c", "start", '""', bat_path], shell=True)
                return ("🚀 **DEEP AI Server** is now booting up...", "system_launcher", [{"language": "powershell", "code": f'start "{bat_path}"', "output": "Server Launched"}])
            else:
                return ("❌ **DEEP AI Server** shortcut not found on Desktop.", "system_launcher", [])
        except Exception as e:
            print(f"[Launcher] Error: {e}")
        return None
