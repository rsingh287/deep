import ctypes
import datetime
import os
import sys


class PCAutomationEngine:
    def __init__(self):
        self.screenshots_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "screenshots")
        )
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def take_screenshot(self):
        try:
            from PIL import ImageGrab

            screenshot = ImageGrab.grab()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                self.screenshots_dir, f"screenshot_{timestamp}.png"
            )
            screenshot.save(file_path)

            return f"📸 **Desktop Screenshot Saved!**\n\nI have successfully captured your screen.\n- **Location**: `{file_path}`"
        except Exception as e:
            return f"⚠️ **Error taking screenshot**: {e}\n\nMake sure `Pillow` is installed: `pip install Pillow`"

    def lock_workstation(self):
        try:
            if sys.platform == "win32":
                ctypes.windll.user32.LockWorkStation()
                return "🔒 **PC Locked!** I have secured your workstation."
            else:
                return "⚠️ Lock Workstation is currently only supported on Windows."
        except Exception as e:
            return f"⚠️ **Error locking PC**: {e}"

    def empty_recycle_bin(self):
        try:
            if sys.platform == "win32":
                SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
                # SHERB_NOCONFIRMATION = 1, SHERB_NOPROGRESSUI = 2, SHERB_NOSOUND = 4
                result = SHEmptyRecycleBin(None, None, 7)
                if result == 0:
                    return "🗑️ **Recycle Bin Emptied!** Your trash has been cleared."
                else:
                    return "🗑️ **Recycle Bin was already empty** or an error occurred."
            else:
                return "⚠️ Empty Recycle Bin is currently only supported on Windows."
        except Exception as e:
            return f"⚠️ **Error emptying recycle bin**: {e}"


def handle_pc_automation_intent(prompt_low: str):
    engine = PCAutomationEngine()

    screenshot_triggers = ["screenshot", "screen shot", "capture screen"]
    if any(k in prompt_low for k in screenshot_triggers):
        report = engine.take_screenshot()
        return (
            report,
            "autonomous_pc_automation_engine",
            [
                {
                    "language": "python",
                    "code": "take_screenshot()",
                    "output": "Captured and saved Desktop Screenshot",
                }
            ],
        )

    lock_triggers = [
        "lock pc",
        "lock my pc",
        "lock computer",
        "lock screen",
        "lock workstation",
    ]
    if any(k in prompt_low for k in lock_triggers):
        report = engine.lock_workstation()
        return (
            report,
            "autonomous_pc_automation_engine",
            [
                {
                    "language": "python",
                    "code": "lock_workstation()",
                    "output": "Locked Windows Session",
                }
            ],
        )

    trash_triggers = [
        "empty trash",
        "empty recycle bin",
        "clear trash",
        "clear recycle bin",
    ]
    if any(k in prompt_low for k in trash_triggers):
        report = engine.empty_recycle_bin()
        return (
            report,
            "autonomous_pc_automation_engine",
            [
                {
                    "language": "python",
                    "code": "empty_recycle_bin()",
                    "output": "Cleared Recycle Bin",
                }
            ],
        )

    return None
