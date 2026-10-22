import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
log_path = r"C:\Users\User\.gemini\antigravity-ide\brain\18a4d78c-28cb-4871-bd3f-1fb08b821a0d\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get("type") == "USER_INPUT" and step.get("step_index", 0) < 195:
                print(f"=== STEP {step.get('step_index')} ===")
                print(step.get("content"))
        except Exception:
            pass
