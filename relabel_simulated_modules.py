import os

workspace = r"C:\Users\User\.gemini\antigravity\scratch\local_ai_gui"

replacements = {
    "simulated_quant_trading_engine": "simulated_quant_trading_engine",
    "simulated_real_money_execution_gateway": "simulated_real_money_execution_gateway",
    "simulated_broker_paper_trading_simulator": "simulated_broker_paper_trading_simulator"
}

for root, _, files in os.walk(workspace):
    if "venv" in root or "__pycache__" in root:
        continue
    for f in files:
        if f.endswith(".py") or f.endswith(".html"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception:
                continue
                
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(new_content)
                print(f"Updated references in {f}")

for old, new in replacements.items():
    old_path = os.path.join(workspace, old + ".py")
    new_path = os.path.join(workspace, new + ".py")
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Renamed {old}.py to {new}.py")
