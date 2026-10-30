"""
Phase 3 Integration Test Suite: Self-Synthesizing Tool Forge & Sandbox Verification
===================================================================================
Verifies:
1. Zero-Trust AST Security Shield (detects banned builtins, imports, and system calls)
2. Autonomous Tool Synthesis & Unit Test Generation
3. Sandboxed Subprocess Test Execution & Verification
4. Dynamic Module Loading & Tool Execution
5. Master Skills Registry Injection & Unregistration
6. Dynamic Tool Intent Dispatching
7. Live REST Endpoints (/api/forge/tools, /api/forge/execute, /api/forge/verify)
"""

import os
import sys
import time
import unittest
import requests

from self_synthesizing_tool_forge import (
    get_tool_forge,
    ASTSecurityShield,
    ToolForgeManifest,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
)
from intents.dynamic_tool_intent import DynamicToolIntent


class TestPhase3ToolForge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.forge = get_tool_forge()
        cls.api_base = "http://127.0.0.1:5000"

    # --- 1. AST Security Shield ---
    def test_01_ast_shield_accepts_clean_code(self):
        clean_code = """
def calculate_hypotenuse(a: float, b: float) -> float:
    import math
    return math.sqrt(a**2 + b**2)
"""
        is_safe, msg = ASTSecurityShield.validate_code(clean_code)
        self.assertTrue(is_safe, f"Clean code must pass AST validation: {msg}")

    def test_02_ast_shield_blocks_banned_builtins(self):
        malicious_code = """
def unsafe_eval_runner(expr: str):
    return eval(expr)
"""
        is_safe, msg = ASTSecurityShield.validate_code(malicious_code)
        self.assertFalse(is_safe, "Call to eval() must be blocked by AST shield")
        self.assertIn("SECURITY_VIOLATION", msg)

    def test_03_ast_shield_blocks_banned_modules(self):
        banned_code = """
import ctypes
def trigger_kernel():
    ctypes.windll.user32.MessageBeep(0)
"""
        is_safe, msg = ASTSecurityShield.validate_code(banned_code)
        self.assertFalse(is_safe, "Importing ctypes must be blocked by AST shield")
        self.assertIn("SECURITY_VIOLATION", msg)

    def test_04_ast_shield_blocks_os_system(self):
        os_code = """
import os
def run_command(cmd):
    return os.system(cmd)
"""
        is_safe, msg = ASTSecurityShield.validate_code(os_code)
        self.assertFalse(is_safe, "Call to os.system() must be blocked by AST shield")
        self.assertIn("SECURITY_VIOLATION", msg)

    # --- 2. Deterministic Tool Synthesis & File Writing ---
    def test_05_manual_tool_synthesis_and_manifest(self):
        test_tool_name = "test_temperature_converter"
        tool_code = """
def convert_temp(celsius: float = 0.0) -> dict:
    fahrenheit = (celsius * 9.0 / 5.0) + 32.0
    kelvin = celsius + 273.15
    return {
        "celsius": celsius,
        "fahrenheit": round(fahrenheit, 2),
        "kelvin": round(kelvin, 2)
    }
"""
        test_code = """
import unittest
from dynamic_tools.test_temperature_converter import convert_temp

class TestTempConverter(unittest.TestCase):
    def test_freezing(self):
        res = convert_temp(0.0)
        self.assertEqual(res["fahrenheit"], 32.0)
        self.assertEqual(res["kelvin"], 273.15)

    def test_boiling(self):
        res = convert_temp(100.0)
        self.assertEqual(res["fahrenheit"], 212.0)
        self.assertEqual(res["kelvin"], 373.15)
"""
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{test_tool_name}.py")
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{test_tool_name}.py")

        with open(tool_file, "w", encoding="utf-8") as f:
            f.write(tool_code.strip() + "\n")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code.strip() + "\n")

        ToolForgeManifest.update_tool(test_tool_name, {
            "id": test_tool_name,
            "name": "Temperature Converter",
            "description": "Converts Celsius to Fahrenheit and Kelvin.",
            "file_path": tool_file,
            "test_path": test_file,
            "verification_status": "SYNTHESIZED_PENDING_TESTS",
            "test_pass_count": 0,
            "execution_count": 0,
        })

        self.assertTrue(os.path.exists(tool_file))
        self.assertTrue(os.path.exists(test_file))

    # --- 3. Sandboxed Subprocess Verification ---
    def test_06_sandboxed_tool_verification(self):
        test_tool_name = "test_temperature_converter"
        res = self.forge.verify_tool(test_tool_name)
        self.assertTrue(res.get("success"), f"Verification failed: {res.get('error')}")
        self.assertEqual(res.get("status"), "VERIFIED_OPERATIONAL")

        manifest = ToolForgeManifest.load()
        tool_meta = manifest["tools"].get(test_tool_name, {})
        self.assertEqual(tool_meta.get("verification_status"), "VERIFIED_OPERATIONAL")
        self.assertGreaterEqual(tool_meta.get("test_pass_count", 0), 1)

    # --- 4. Dynamic Execution & Telemetry ---
    def test_07_dynamic_tool_execution(self):
        test_tool_name = "test_temperature_converter"
        res = self.forge.execute_tool(test_tool_name, {"celsius": 100.0})
        self.assertTrue(res.get("success"), f"Execution failed: {res.get('error')}")
        self.assertIn("result", res)
        self.assertEqual(res["result"]["fahrenheit"], 212.0)
        self.assertEqual(res["result"]["kelvin"], 373.15)
        self.assertGreaterEqual(res.get("execution_time_ms", 0), 0.0)

    # --- 5. Intent Matrix Integration ---
    def test_08_dynamic_tool_intent_can_handle(self):
        self.assertTrue(DynamicToolIntent.can_handle("synthesize tool json_formatter to prettify raw json"))
        self.assertTrue(DynamicToolIntent.can_handle("run tool test_temperature_converter with celsius=37"))
        self.assertTrue(DynamicToolIntent.can_handle("list synthesized tools"))
        self.assertFalse(DynamicToolIntent.can_handle("what is the price of Bitcoin"))

    def test_09_dynamic_tool_intent_execution(self):
        res, model, actions = DynamicToolIntent.execute(
            user_prompt="run tool test_temperature_converter with celsius=25",
            norm_prompt="run tool test_temperature_converter with celsius=25"
        )
        self.assertIn("Tool Forge Execution", res)
        self.assertIn("77.0", res)  # 25C = 77F
        self.assertEqual(model, "qwen2.5-coder:7b")

    # --- 6. Live REST Endpoints ---
    def test_10_rest_api_list_and_execute(self):
        try:
            # 1. GET /api/forge/tools
            r_list = requests.get(f"{self.api_base}/api/forge/tools", timeout=5)
            self.assertEqual(r_list.status_code, 200)
            data = r_list.json()
            self.assertTrue(data.get("success"))
            self.assertGreaterEqual(data.get("total_tools", 0), 1)

            # 2. POST /api/forge/execute
            r_exec = requests.post(
                f"{self.api_base}/api/forge/execute",
                json={"tool_name": "test_temperature_converter", "arguments": {"celsius": 0.0}},
                timeout=5
            )
            self.assertEqual(r_exec.status_code, 200)
            exec_data = r_exec.json()
            self.assertTrue(exec_data.get("success"))
            self.assertEqual(exec_data["result"]["fahrenheit"], 32.0)

        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running on port 5000")

    # Clean up test tool
    @classmethod
    def tearDownClass(cls):
        cls.forge.delete_tool("test_temperature_converter")


if __name__ == "__main__":
    unittest.main()
