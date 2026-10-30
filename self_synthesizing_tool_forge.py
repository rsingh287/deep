"""
Self-Synthesizing Tool Forge for D.E.E.P. Sovereign Cognitive OS
================================================================
Provides autonomous tool synthesis, sandboxed verification, self-healing,
and dynamic hot-registration without server restarts.

Pipeline:
1. Natural language tool specification
2. Autonomous code + unit test synthesis via local Qwen 2.5 Coder
3. Zero-Trust AST static security analysis & boundary enforcement
4. Sandboxed test execution via subprocess runner
5. Autonomous self-healing loop on test failure (traceback feedback)
6. Permanent registration in dynamic tool manifest & master skills registry
"""

import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DYNAMIC_TOOLS_DIR = os.path.join(CURRENT_DIR, "dynamic_tools")
DYNAMIC_TESTS_DIR = os.path.join(DYNAMIC_TOOLS_DIR, "tests")
MANIFEST_PATH = os.path.join(DYNAMIC_TOOLS_DIR, "manifest.json")
MASTER_REGISTRY_PATH = os.path.join(CURRENT_DIR, "master_skills_registry.json")

os.makedirs(DYNAMIC_TOOLS_DIR, exist_ok=True)
os.makedirs(DYNAMIC_TESTS_DIR, exist_ok=True)

# Ensure dynamic_tools has an __init__.py so Python treats it as a package
init_file = os.path.join(DYNAMIC_TOOLS_DIR, "__init__.py")
if not os.path.exists(init_file):
    with open(init_file, "w", encoding="utf-8") as f:
        f.write("# D.E.E.P. Synthesized Tools Package\n")

test_init_file = os.path.join(DYNAMIC_TESTS_DIR, "__init__.py")
if not os.path.exists(test_init_file):
    with open(test_init_file, "w", encoding="utf-8") as f:
        f.write("# D.E.E.P. Synthesized Tools Test Package\n")

OLLAMA_API_BASE = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if not OLLAMA_API_BASE.startswith("http://") and not OLLAMA_API_BASE.startswith("https://"):
    OLLAMA_API_BASE = f"http://{OLLAMA_API_BASE}"


class ASTSecurityShield:
    """Zero-Trust AST Static Code Analyzer for synthesized tools."""

    BANNED_MODULES = {
        "winreg",
        "ctypes",
        "msvcrt",
        "win32api",
        "win32con",
        "subprocess",
    }

    BANNED_FUNCTIONS = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "globals",
        "locals",
        "vars",
    }

    BANNED_OS_CALLS = {
        "system",
        "popen",
        "spawn",
        "fork",
        "kill",
        "rmdir",
        "removedirs",
    }

    @classmethod
    def validate_code(cls, code_str: str) -> Tuple[bool, str]:
        """
        Parses python source code through an Abstract Syntax Tree (AST).
        Disallows dangerous built-ins, uncontained OS mutations, and privilege escalation.
        """
        try:
            tree = ast.parse(code_str)
        except SyntaxError as se:
            return False, f"AST_SYNTAX_ERROR: Line {se.lineno}: {se.msg}"

        has_function = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_function = True

            # 1. Check direct imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in cls.BANNED_MODULES:
                        return False, f"SECURITY_VIOLATION: Importing module '{root_mod}' is prohibited in synthesized tools."

            # 2. Check from ... import
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod in cls.BANNED_MODULES:
                        return False, f"SECURITY_VIOLATION: Importing from '{root_mod}' is prohibited."

            # 3. Check calls to banned functions
            elif isinstance(node, ast.Call):
                # Direct call: eval(), exec()
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.BANNED_FUNCTIONS:
                        return False, f"SECURITY_VIOLATION: Call to prohibited builtin '{node.func.id}()'."
                # Method call: os.system(), shutil.rmtree()
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in cls.BANNED_OS_CALLS:
                        return False, f"SECURITY_VIOLATION: Call to prohibited method '{node.func.attr}()'."

        if not has_function:
            return False, "STRUCTURE_ERROR: Synthesized tool must define at least one entrypoint function."

        return True, "AST security verification passed."


class ToolForgeManifest:
    """Manages persistent metadata and execution stats for synthesized tools."""

    @staticmethod
    def load() -> Dict[str, Any]:
        if not os.path.exists(MANIFEST_PATH):
            initial = {"version": "1.0", "tools": {}}
            ToolForgeManifest.save(initial)
            return initial
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"version": "1.0", "tools": {}}

    @staticmethod
    def save(data: Dict[str, Any]):
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def update_tool(tool_id: str, tool_meta: Dict[str, Any]):
        manifest = ToolForgeManifest.load()
        manifest["tools"][tool_id] = tool_meta
        ToolForgeManifest.save(manifest)

    @staticmethod
    def remove_tool(tool_id: str):
        manifest = ToolForgeManifest.load()
        if tool_id in manifest["tools"]:
            del manifest["tools"][tool_id]
            ToolForgeManifest.save(manifest)


class SelfSynthesizingToolForge:
    """The Autonomous Self-Synthesizing Tool Forge Engine."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SelfSynthesizingToolForge, cls).__new__(cls)
        return cls._instance

    def __init__(self, default_model: str = "qwen2.5-coder:7b"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.default_model = default_model
        self._initialized = True

    def _sanitize_name(self, name: str) -> str:
        """Converts arbitrary strings into valid, safe Python module identifiers."""
        clean = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower())
        clean = re.sub(r"^_+|__+|_+$", "", clean)
        if not clean or clean[0].isdigit():
            clean = f"tool_{clean}"
        return clean[:40]

    def synthesize_tool(
        self,
        prompt: str,
        tool_name: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes a standalone Python tool and companion unit tests from natural language.
        Returns synthesis report, AST security status, and file paths.
        """
        active_model = model or self.default_model
        t0 = time.time()

        system_instruction = (
            "You are D.E.E.P. Autonomous Tool Forge, an elite software synthesis engine. "
            "Write a production-ready, self-contained Python tool and companion unittest test suite. "
            "CRITICAL SECURITY RULES: "
            "1. Do NOT import ctypes, winreg, msvcrt, or subprocess. "
            "2. Do NOT use eval(), exec(), or os.system(). "
            "3. The tool must have an entrypoint function that accepts typed parameters with defaults and returns a dict or typed value. "
            "4. Return ONLY a valid JSON object with the following schema: "
            '{"tool_name": "snake_case_name", "description": "1 sentence description", "parameters": [{"name": "x", "type": "str", "default": ""}], "tool_code": "def ...", "test_code": "import unittest\\n..."}'
        )

        user_prompt = (
            f"Synthesize an autonomous Python tool for this specification:\n\n{prompt}\n\n"
            f"{'Suggested tool name: ' + tool_name if tool_name else 'Choose a clean snake_case tool name.'}"
        )

        try:
            res = requests.post(
                f"{OLLAMA_API_BASE}/api/generate",
                json={
                    "model": active_model,
                    "prompt": f"{system_instruction}\n\nUser Request: {user_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 1800},
                },
                timeout=45,
            )

            if res.status_code != 200:
                return {
                    "success": False,
                    "error": f"Ollama HTTP {res.status_code}: {res.text[:120]}",
                    "latency_ms": round((time.time() - t0) * 1000, 1),
                }

            raw_text = res.json().get("response", "").strip()
            parsed = self._extract_tool_payload(raw_text)

            if not parsed:
                return {
                    "success": False,
                    "error": "Failed to parse valid JSON tool schema from model output.",
                    "raw_response": raw_text[:300],
                }

            t_name = self._sanitize_name(tool_name or parsed.get("tool_name", "custom_tool"))
            tool_code = parsed.get("tool_code", "").strip()
            test_code = parsed.get("test_code", "").strip()
            description = parsed.get("description", prompt)
            parameters = parsed.get("parameters", [])

            # AST Security Verification
            is_safe, sec_reason = ASTSecurityShield.validate_code(tool_code)
            if not is_safe:
                return {
                    "success": False,
                    "error": f"AST Shield Blocked: {sec_reason}",
                    "tool_name": t_name,
                }

            # Auto-inject import of the tool into test suite if omitted by LLM
            if f"dynamic_tools.{t_name}" not in test_code and f"import {t_name}" not in test_code:
                test_code = f"from dynamic_tools.{t_name} import *\n" + test_code

            # Write code to dynamic_tools/
            tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{t_name}.py")
            test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{t_name}.py")

            with open(tool_file, "w", encoding="utf-8") as f:
                f.write(tool_code + "\n")

            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code + "\n")

            # Compute safety hash
            code_hash = hashlib.sha256(tool_code.encode("utf-8")).hexdigest()[:16]

            tool_metadata = {
                "id": t_name,
                "name": t_name.replace("_", " ").title(),
                "description": description,
                "parameters": parameters,
                "file_path": tool_file,
                "test_path": test_file,
                "code_hash": code_hash,
                "verification_status": "SYNTHESIZED_PENDING_TESTS",
                "test_pass_count": 0,
                "execution_count": 0,
                "author": f"D.E.E.P. Tool Forge ({active_model})",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_executed": None,
            }

            ToolForgeManifest.update_tool(t_name, tool_metadata)

            return {
                "success": True,
                "tool_name": t_name,
                "description": description,
                "parameters": parameters,
                "tool_file": tool_file,
                "test_file": test_file,
                "security_status": "PASSED_AST_VALIDATION",
                "latency_ms": round((time.time() - t0) * 1000, 1),
            }

        except Exception as e:
            return {"success": False, "error": f"Tool synthesis exception: {e}"}

    def _extract_tool_payload(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON structure from model response with markdown fence handling."""
        cleaned = re.sub(r"```json\s*", "", raw_text, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Try finding outermost JSON curly braces
        m = re.search(r"(\{[\s\S]*\})", cleaned)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass

        return None

    def verify_tool(self, tool_name: str, max_healing_attempts: int = 1) -> Dict[str, Any]:
        """
        Executes unit tests for the synthesized tool in an isolated subprocess.
        Automatically triggers the Self-Healing Loop if tests fail.
        """
        t_name = self._sanitize_name(tool_name)
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{t_name}.py")
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{t_name}.py")

        if not os.path.exists(test_file) or not os.path.exists(tool_file):
            return {"success": False, "error": f"Tool files for '{t_name}' not found."}

        attempt = 0
        while attempt <= max_healing_attempts:
            t0 = time.time()
            try:
                cmd = [sys.executable, "-m", "unittest", f"dynamic_tools.tests.test_{t_name}"]
                res = subprocess.run(
                    cmd,
                    cwd=CURRENT_DIR,
                    capture_output=True,
                    text=True,
                    timeout=8.0,
                )

                test_time_ms = round((time.time() - t0) * 1000, 1)

                if res.returncode == 0:
                    manifest = ToolForgeManifest.load()
                    meta = manifest["tools"].get(t_name, {})
                    meta["verification_status"] = "VERIFIED_OPERATIONAL"
                    meta["test_pass_count"] = meta.get("test_pass_count", 0) + 1
                    meta["verified_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    ToolForgeManifest.update_tool(t_name, meta)

                    # Register into Master Skills Registry
                    self._register_into_master_skills(meta)

                    return {
                        "success": True,
                        "tool_name": t_name,
                        "status": "VERIFIED_OPERATIONAL",
                        "test_output": res.stderr or res.stdout,
                        "latency_ms": test_time_ms,
                        "self_healed": attempt > 0,
                    }

                # If failed and attempts remain: trigger Self-Healing
                stderr_output = res.stderr or res.stdout
                print(f"[ToolForge] Verification attempt {attempt + 1} failed for '{t_name}'. Error:\n{stderr_output[:250]}")

                if attempt < max_healing_attempts:
                    attempt += 1
                    print(f"[ToolForge] 🩹 Initiating Autonomous Self-Healing for '{t_name}' (Attempt {attempt})...")
                    healed = self._self_heal_tool(t_name, tool_file, test_file, stderr_output)
                    if not healed:
                        break
                    continue
                else:
                    return {
                        "success": False,
                        "tool_name": t_name,
                        "status": "VERIFICATION_FAILED",
                        "error": stderr_output,
                        "latency_ms": test_time_ms,
                    }

            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "tool_name": t_name,
                    "status": "TIMEOUT",
                    "error": "Test execution exceeded 8.0s timeout limit (possible infinite loop).",
                }
            except Exception as e:
                return {"success": False, "tool_name": t_name, "error": str(e)}

        return {"success": False, "tool_name": t_name, "status": "VERIFICATION_FAILED"}

    def _self_heal_tool(
        self, tool_name: str, tool_file: str, test_file: str, error_trace: str
    ) -> bool:
        """Prompts coder model with the failing trace to self-heal the implementation."""
        with open(tool_file, "r", encoding="utf-8") as f:
            curr_tool_code = f.read()
        with open(test_file, "r", encoding="utf-8") as f:
            curr_test_code = f.read()

        prompt = (
            f"Autonomous Self-Healing Request for tool '{tool_name}'.\n"
            f"The unit test failed with the following traceback:\n```\n{error_trace}\n```\n\n"
            f"Current Tool Code:\n```python\n{curr_tool_code}\n```\n\n"
            f"Current Test Code:\n```python\n{curr_test_code}\n```\n\n"
            "Analyze the failure. Fix the tool code and/or test code so that all tests pass cleanly. "
            "Output ONLY a JSON object: "
            '{"tool_code": "...", "test_code": "..."}'
        )

        try:
            res = requests.post(
                f"{OLLAMA_API_BASE}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1600},
                },
                timeout=35,
            )

            if res.status_code == 200:
                payload = self._extract_tool_payload(res.json().get("response", ""))
                if payload and "tool_code" in payload:
                    new_tool_code = payload["tool_code"]
                    new_test_code = payload.get("test_code", curr_test_code)

                    if f"dynamic_tools.{tool_name}" not in new_test_code and f"import {tool_name}" not in new_test_code:
                        new_test_code = f"from dynamic_tools.{tool_name} import *\n" + new_test_code

                    is_safe, _ = ASTSecurityShield.validate_code(new_tool_code)
                    if is_safe:
                        with open(tool_file, "w", encoding="utf-8") as f:
                            f.write(new_tool_code + "\n")
                        with open(test_file, "w", encoding="utf-8") as f:
                            f.write(new_test_code + "\n")
                        print(f"[ToolForge] Self-heal patch applied for '{tool_name}'.")
                        return True
        except Exception as e:
            print(f"[ToolForge] Self-healing exception: {e}")

        return False

    def execute_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dynamically loads and executes a verified synthesized tool by name.
        Safe execution with execution timing and error isolation.
        """
        t_name = self._sanitize_name(tool_name)
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{t_name}.py")

        if not os.path.exists(tool_file):
            return {"success": False, "error": f"Tool '{t_name}' does not exist on disk."}

        args = arguments or {}
        t0 = time.perf_counter()

        try:
            # Dynamic module loading via importlib
            spec = importlib.util.spec_from_file_location(f"dynamic_tools.{t_name}", tool_file)
            if spec is None or spec.loader is None:
                return {"success": False, "error": f"Could not create module spec for '{t_name}'."}

            module = importlib.util.module_module = importlib.util.module_from_spec(spec)
            sys.modules[f"dynamic_tools.{t_name}"] = module
            spec.loader.exec_module(module)

            # Discover entrypoint function: <t_name>, run, or execute
            entrypoint = None
            if hasattr(module, t_name) and callable(getattr(module, t_name)):
                entrypoint = getattr(module, t_name)
            elif hasattr(module, "run") and callable(getattr(module, "run")):
                entrypoint = getattr(module, "run")
            elif hasattr(module, "execute") and callable(getattr(module, "execute")):
                entrypoint = getattr(module, "execute")
            else:
                # Fallback: first function defined in module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith("_"):
                        entrypoint = attr
                        break

            if entrypoint is None:
                return {"success": False, "error": f"No callable entrypoint function found in '{t_name}'."}

            # Execute with arguments
            result = entrypoint(**args)
            exec_time_ms = round((time.perf_counter() - t0) * 1000, 3)

            # Update telemetry
            manifest = ToolForgeManifest.load()
            if t_name in manifest["tools"]:
                manifest["tools"][t_name]["execution_count"] = manifest["tools"][t_name].get("execution_count", 0) + 1
                manifest["tools"][t_name]["last_executed"] = time.strftime("%Y-%m-%d %H:%M:%S")
                ToolForgeManifest.save(manifest)

            return {
                "success": True,
                "tool_name": t_name,
                "result": result,
                "execution_time_ms": exec_time_ms,
            }

        except Exception as e:
            return {
                "success": False,
                "tool_name": t_name,
                "error": f"Execution error: {e}",
                "execution_time_ms": round((time.time() - t0) * 1000, 2),
            }

    def list_synthesized_tools(self) -> List[Dict[str, Any]]:
        """Returns all dynamically synthesized tools from manifest."""
        manifest = ToolForgeManifest.load()
        return list(manifest.get("tools", {}).values())

    def delete_tool(self, tool_name: str) -> bool:
        """Removes a synthesized tool from disk and registry."""
        t_name = self._sanitize_name(tool_name)
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{t_name}.py")
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{t_name}.py")

        for p in [tool_file, test_file]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        ToolForgeManifest.remove_tool(t_name)
        self._unregister_from_master_skills(t_name)
        return True

    def _register_into_master_skills(self, meta: Dict[str, Any]):
        """Injects verified synthesized tool into master_skills_registry.json."""
        if not os.path.exists(MASTER_REGISTRY_PATH):
            return

        try:
            with open(MASTER_REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)

            skill_id = f"synthesized-{meta['id']}"
            existing = [item for item in registry if item.get("id") == skill_id]

            if not existing:
                registry.append({
                    "id": skill_id,
                    "name": meta["name"],
                    "scope": "Synthesized",
                    "plugin": "tool-forge",
                    "category": "🛠️ Synthesized Tool",
                    "description": meta.get("description", "Autonomously synthesized Python tool."),
                })
                with open(MASTER_REGISTRY_PATH, "w", encoding="utf-8") as f:
                    json.dump(registry, f, indent=2)
                print(f"[ToolForge] Registered '{skill_id}' in master skills registry.")
        except Exception as e:
            print(f"[ToolForge] Master registry injection notice: {e}")

    def _unregister_from_master_skills(self, tool_id: str):
        """Removes tool entry from master skills registry upon deletion."""
        if not os.path.exists(MASTER_REGISTRY_PATH):
            return
        try:
            with open(MASTER_REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)

            skill_id = f"synthesized-{tool_id}"
            registry = [item for item in registry if item.get("id") != skill_id]

            with open(MASTER_REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)
        except Exception:
            pass


# Global Singleton Instance
_tool_forge_instance = None

def get_tool_forge() -> SelfSynthesizingToolForge:
    global _tool_forge_instance
    if _tool_forge_instance is None:
        _tool_forge_instance = SelfSynthesizingToolForge()
    return _tool_forge_instance
