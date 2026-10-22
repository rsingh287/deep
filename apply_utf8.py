import os
import re

dir_path = r"C:\Users\User\.gemini\antigravity\scratch\local_ai_gui"
snippet = """    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""

count = 0
for root, dirs, files in os.walk(dir_path):
    if "venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Could not read {file}: {e}")
                continue
            
            if 'sys.stdout.reconfigure' in content:
                continue
            
            match = re.search(r'^if __name__ == [\'"]__main__[\'"]:\s*$', content, flags=re.MULTILINE)
            if match:
                idx = match.end()
                new_content = content[:idx] + "\n" + snippet + content[idx:]
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                count += 1
                print(f"Updated {file}")
print(f"Total updated: {count}")
