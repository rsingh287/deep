import json
import os
import subprocess


def run_code_scan(target_dir):
    """
    Runs flake8 (logic bugs/undefined names) and vulture (dead code)
    on the target directory and returns a structured JSON report.
    """
    if not os.path.exists(target_dir):
        return json.dumps({"error": f"Directory not found: {target_dir}"})

    results = {"status": "success", "bugs": [], "dead_code": [], "errors": []}

    # 1. Run flake8 (Select F for logical errors, E9 for syntax errors)
    # Ignore stylistic issues to focus purely on bugs
    try:
        # F: pyflakes (logical errors), E9: syntax errors
        flake8_cmd = ["flake8", "--select=E9,F", target_dir]
        res = subprocess.run(flake8_cmd, capture_output=True, text=True)
        if res.stdout:
            for line in res.stdout.strip().split("\n"):
                if line:
                    results["bugs"].append(line)
        if res.stderr:
            results["errors"].append(f"flake8 error: {res.stderr}")
    except FileNotFoundError:
        results["errors"].append("flake8 is not installed or not in PATH.")
    except Exception as e:
        results["errors"].append(f"flake8 execution failed: {str(e)}")

    # 2. Run vulture (Dead code detection)
    try:
        vulture_cmd = ["vulture", target_dir]
        res = subprocess.run(vulture_cmd, capture_output=True, text=True)
        if res.stdout:
            for line in res.stdout.strip().split("\n"):
                if line:
                    results["dead_code"].append(line)
        if res.stderr:
            results["errors"].append(f"vulture error: {res.stderr}")
    except FileNotFoundError:
        results["errors"].append("vulture is not installed or not in PATH.")
    except Exception as e:
        results["errors"].append(f"vulture execution failed: {str(e)}")

    return json.dumps(results, indent=2)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # Test local directory
    print(run_code_scan(os.path.dirname(os.path.abspath(__file__))))
