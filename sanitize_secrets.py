import os
import re

workspace = r"C:\Users\User\.gemini\antigravity\scratch\local_ai_gui"

replacements = {
    r'"password"\s*:\s*"[^"]+"': 'r"password": os.getenv("DB_PASSWORD", "")',
    r'password\s*=\s*"[^"]+"': 'password=os.getenv("DB_PASSWORD", "")',
}

for root, _, files in os.walk(workspace):
    if "venv" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception:
                continue
                
            new_content = content
            # Add import os if we replace something
            changed = False
            for old, new in replacements.items():
                if re.search(old, new_content):
                    new_content = re.sub(old, new, new_content)
                    changed = True
            
            if changed:
                if "import os" not in new_content:
                    new_content = "import os\n" + new_content
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                print(f"Sanitized secrets in {f}")

