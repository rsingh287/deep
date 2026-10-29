import ast
import json
import os
import re
import subprocess
from typing import List, Dict, Any


EXCLUDED_DIRS = {
    ".git", "__pycache__", "pg_data", ".venv", "venv",
    "node_modules", ".agents", ".trash", "dist", "build", "debug",
    "generated_apps", "disabled_startup_backup", "startup_backup"
}

RESOURCE_ALLOCATORS = {
    "get_db_connection": "Database Connection",
    "connect": "Database Connection",
    "VideoCapture": "Webcam VideoCapture Handle",
    "PyAudio": "PyAudio Audio Handle",
}


class InferASTVisitor(ast.NodeVisitor):
    """
    Facebook Infer-inspired AST static analyzer for Python:
    - Resource handle leaks (DB connections, cursors, OpenCV cameras, audio handles)
    - Silent exception swallowing (except: pass without logging)
    - SQL injection risks (f-strings / modulo in cursor.execute)
    """
    def __init__(self, filename: str, rel_path: str):
        self.filename = filename
        self.rel_path = rel_path
        self.findings: List[str] = []
        self._with_targets = set()

    def visit_With(self, node: ast.With):
        for item in node.items:
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self._with_targets.add(item.optional_vars.id)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # Check for unmanaged resource allocations
        if isinstance(node.value, ast.Call):
            func_name = ""
            if isinstance(node.value.func, ast.Name):
                func_name = node.value.func.id
            elif isinstance(node.value.func, ast.Attribute):
                func_name = node.value.func.attr

            if func_name in RESOURCE_ALLOCATORS:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # If not in 'with' statement, flag for inspection
                        if var_name not in self._with_targets:
                            # Verify if target file is a test/migration file
                            if not any(t in self.rel_path for t in ("test_", "migrate_")):
                                self.findings.append(
                                    f"{self.rel_path}:{node.lineno}: [Infer: Resource Handle Check] "
                                    f"'{var_name}' allocates {RESOURCE_ALLOCATORS[func_name]}. "
                                    f"Ensure deterministic closure in finally: block or context manager."
                                )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Check for silent exception swallowing
        is_silent = False
        if len(node.body) == 1:
            first = node.body[0]
            if isinstance(first, ast.Pass):
                is_silent = True
            elif isinstance(first, ast.Return) and (first.value is None or (isinstance(first.value, ast.Constant) and first.value.value is None)):
                is_silent = True

        if is_silent and not any(t in self.rel_path for t in ("test_", "mock")):
            exc_name = node.type.id if isinstance(node.type, ast.Name) else "Exception"
            self.findings.append(
                f"{self.rel_path}:{node.lineno}: [Infer: Silent Swallow] "
                f"except {exc_name} block silently suppresses error without logging or structured user feedback."
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Check for SQL injection in cursor.execute(f"...") or cursor.execute("..." % ...)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("execute", "execute_readonly_query"):
            if node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.JoinedStr):
                    self.findings.append(
                        f"{self.rel_path}:{node.lineno}: [Infer: SQL Injection Risk] "
                        f"Database execute() called with interpolated f-string instead of parameterized query."
                    )
                elif isinstance(arg0, ast.BinOp) and isinstance(arg0.op, ast.Mod):
                    self.findings.append(
                        f"{self.rel_path}:{node.lineno}: [Infer: SQL Injection Risk] "
                        f"Database execute() called with '%' string formatting instead of parameterized query."
                    )
        self.generic_visit(node)


def scan_embedded_c_file(file_path: str, rel_path: str = "") -> List[str]:
    """
    Embedded static analyzer checking PIC18F85K22 Trainer 2 rules:
    - LCD Line 1 Hardware Defect: primary feedback on Line 2
    - External crystal definition (4.9152 MHz)
    - Oscillator fuse configuration (HS2)
    - PORTD conflict avoidance (reserved for Red LED Bar)
    """
    if not rel_path:
        rel_path = os.path.basename(file_path)
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            # Check for LCD Data Bus mistakenly routed to PORTD
            if re.search(r"#define\s+LCD_DATA_LAT\s+LATD\b", line):
                findings.append(
                    f"{rel_path}:{idx}: [Infer: Embedded Hardware Rule] "
                    f"LCD_DATA_LAT is mapped to LATD! 16x2 LCD data bus must be on PORTH (LATH)."
                )

            # Check for crystal frequency mismatch
            if re.search(r"#define\s+_XTAL_FREQ\b", line):
                if "4915200" not in line and not line.strip().startswith("//"):
                    findings.append(
                        f"{rel_path}:{idx}: [Infer: Clock Frequency Alert] "
                        f"_XTAL_FREQ does not match 4.9152 MHz crystal (4915200UL)."
                    )

            # Check for HS oscillator fuse
            if re.search(r"#pragma\s+config\s+FOSC\s*=\s*HS1\b", line):
                findings.append(
                    f"{rel_path}:{idx}: [Infer: Config Fuse Warning] "
                    f"FOSC is configured as HS1. AGENTS.md specifies FOSC = HS2 for PIC18F85K22."
                )

            # Check for LCD Line 1 Hardware Defect: primary feedback on Line 2
            if re.search(r"\bLCD_Set_Cursor\s*\(\s*1\s*,", line):
                if not line.strip().startswith("//") and not line.strip().startswith("/*"):
                    findings.append(
                        f"{rel_path}:{idx}: [Infer: LCD Line 1 Hardware Defect] "
                        f"Line 1 (0x80..0x8F) is broken/unreadable on Trainer 2 board. "
                        f"Directives mandate primary UI and feedback render strictly on Line 2 (LCD_Set_Cursor(2, 1))."
                    )

            # Check for LM35 formula violation on MCP9701-E/TO analog sensor
            if ("/ 10.0" in line or "/ 10;" in line or "/10" in line) and ("temp" in line.lower() or "mv" in line.lower() or "adc" in line.lower()):
                if not line.strip().startswith("//") and "400" not in line and "19.5" not in line:
                    findings.append(
                        f"{rel_path}:{idx}: [Infer: Sensor Transfer Function Violation] "
                        f"Detected LM35 math (/ 10). Onboard sensor is MCP9701-E/TO requiring T_A = (V_mV - 400.0) / 19.5 with >=16 sample rolling average."
                    )

            # Check for PORTD conflict in buzzer functions (PORTD is the 8-LED bar)
            if re.search(r"\bLATD\s*=", line):
                # Check surrounding lines to see if it's inside a buzzer function
                context = "\n".join(lines[max(0, idx - 15):min(len(lines), idx + 5)])
                if any(w in context for w in ["Buzzer", "buzzer", "Beep", "Tone"]):
                    findings.append(
                        f"{rel_path}:{idx}: [Infer: PORTD Hardware Conflict] "
                        f"PORTD (LATD) toggled inside buzzer function. PORTD is reserved exclusively for the 8-LED Bar. Piezo Buzzer is on LATF / LATAbits.LATA5 / LATCbits.LATC3."
                    )
    except Exception as e:
        findings.append(f"{rel_path}: Failed to scan embedded C file: {e}")

    return findings


def run_infer_ast_scan(target_dir: str) -> Dict[str, Any]:
    """Runs deep AST static analysis across Python and Embedded C sources."""
    ast_findings: List[str] = []
    embedded_findings: List[str] = []
    files_analyzed = 0

    for root, dirs, files in os.walk(target_dir):
        # Exclude unwanted directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)

            if file.endswith(".py"):
                files_analyzed += 1
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                    tree = ast.parse(source, filename=rel_path)
                    visitor = InferASTVisitor(file, rel_path)
                    visitor.visit(tree)
                    ast_findings.extend(visitor.findings)
                except SyntaxError as se:
                    ast_findings.append(f"{rel_path}:{se.lineno}: [Syntax Error] {se.msg}")
                except Exception as ex:
                    ast_findings.append(f"{rel_path}: [Scan Error] {ex}")

            elif file.endswith((".c", ".h")):
                files_analyzed += 1
                c_findings = scan_embedded_c_file(full_path, rel_path)
                embedded_findings.extend(c_findings)

    return {
        "files_analyzed": files_analyzed,
        "ast_findings": ast_findings,
        "embedded_findings": embedded_findings,
    }


def run_code_scan(target_dir: str) -> str:
    """
    Runs Facebook Infer-style AST analysis, flake8, and vulture,
    returning an enterprise structured JSON report.
    """
    if not os.path.exists(target_dir):
        return json.dumps({"error": f"Directory not found: {target_dir}"})

    results = {
        "status": "success",
        "bugs": [],
        "infer_ast_analysis": [],
        "embedded_firmware_analysis": [],
        "dead_code": [],
        "errors": [],
    }

    # 1. Facebook Infer-style Deep AST & Embedded Analysis
    try:
        infer_res = run_infer_ast_scan(target_dir)
        results["infer_ast_analysis"] = infer_res["ast_findings"]
        results["embedded_firmware_analysis"] = infer_res["embedded_findings"]
        # Add deep findings to primary bugs list
        results["bugs"].extend(infer_res["ast_findings"])
        results["bugs"].extend(infer_res["embedded_findings"])
    except Exception as e:
        results["errors"].append(f"Infer AST scan failed: {e}")

    # 2. Run flake8 (Select F for logical errors, E9 for syntax errors)
    try:
        flake8_cmd = [
            "flake8",
            "--select=E9,F",
            "--exclude=" + ",".join(EXCLUDED_DIRS),
            target_dir,
        ]
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

    # 3. Run vulture (Dead code detection)
    try:
        vulture_cmd = [
            "vulture",
            "--exclude",
            ",".join(EXCLUDED_DIRS),
            target_dir,
        ]
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

    print(run_code_scan(os.path.dirname(os.path.abspath(__file__))))

