"""
SAST Code Auditor Engine
Provides static application security testing, code vulnerability auditing,
and hardcoded secret detection for local Python and JavaScript codebases.
"""

import json
import os
import re

SECURITY_PATTERNS = {
    "hardcoded_secret": r"(?i)(password|secret|api_key|token)\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]",
    "sql_injection_risk": r"(?i)execute\s*\(\s*f['\"].*?\{.*?\}",
    "insecure_hash": r"(?i)hashlib\.(md5|sha1)\(",
    "eval_usage": r"(?i)\beval\s*\(",
    "exec_usage": r"(?i)\bexec\s*\(",
}


def scan_directory_for_vulnerabilities(directory_path: str) -> str:
    """Scans all .py and .js files in a directory for security vulnerabilities."""
    if not os.path.exists(directory_path):
        return json.dumps({"error": f"Directory {directory_path} not found."})

    findings = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        for vuln_type, pattern in SECURITY_PATTERNS.items():
                            if re.search(pattern, line):
                                findings.append(
                                    {
                                        "file": file_path,
                                        "line_number": i + 1,
                                        "vulnerability": vuln_type,
                                        "snippet": line.strip()[:100],
                                    }
                                )
                except Exception as e:
                    findings.append({"file": file_path, "error": str(e)})

    return json.dumps(
        {
            "scanned_directory": directory_path,
            "total_findings": len(findings),
            "findings": findings,
        },
        indent=2,
    )


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # Example usage
    print(
        scan_directory_for_vulnerabilities(os.path.dirname(os.path.abspath(__file__)))
    )
