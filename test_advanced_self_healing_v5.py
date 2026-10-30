# -*- coding: utf-8 -*-
"""
test_advanced_self_healing_v5.py — D.E.E.P. Sovereign Cognitive OS
===================================================================
Authoritative Unit Test Suite for Level 5 Autonomous Self-Healing Sentinel:
  1. SystemAnomalyDetector 6-Layer Diagnostic Matrix
  2. Multi-Candidate HealingPatchTournament (AST, LLM, Rollback)
  3. AST Semantic Mutation across 6 Error Classes (ZeroDivision, KeyError, TypeError, AttributeError, IndexError, ValueError)
  4. Full-Spectrum Autonomous Self-Healing Sweep
  5. Tool Immune Quarantine & Unquarantine Lifecycle
  6. Circuit Breaker Canary Probing & Auto-Reset
  7. REST API Endpoints Integration (/api/heal/*)
  8. Natural Language Self-Healing Intent
"""

import os
import sys
import json
import time
import unittest

from autonomous_self_healing_engine import (
    SystemAnomalyDetector,
    HealingPatchTournament,
    AutonomousSelfHealingEngine,
    get_self_healing_engine,
)
from hystrix_circuit_breaker import global_circuit_registry, CircuitState
from self_synthesizing_tool_forge import (
    SelfSynthesizingToolForge,
    ToolForgeManifest,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
)
from app import app


class TestAdvancedSelfHealingV5(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = get_self_healing_engine()
        cls.forge = SelfSynthesizingToolForge()
        cls.client = app.test_client()

    def test_01_six_layer_diagnostic_matrix(self):
        """Test SystemAnomalyDetector inspecting all 6 architectural layers."""
        # Layer 1: Memory & Processes
        l1 = SystemAnomalyDetector.audit_process_and_memory()
        self.assertEqual(l1["layer"], "process_memory")
        self.assertIn("ram_used_percent", l1)
        self.assertIn("freed_cyclic_objects", l1)

        # Layer 2: Storage & Database
        l2 = SystemAnomalyDetector.audit_database_and_vector_core()
        self.assertEqual(l2["layer"], "database_vector_core")
        self.assertIn("sqlite_status", l2)

        # Layer 3: Circuit Breakers
        l3 = SystemAnomalyDetector.audit_circuit_breakers()
        self.assertEqual(l3["layer"], "circuit_breakers")
        self.assertGreaterEqual(l3["total_circuits"], 1)

        # Layer 4: Hardware Mutexes
        l4 = SystemAnomalyDetector.audit_hardware_mutexes()
        self.assertEqual(l4["layer"], "hardware_mutexes")
        self.assertEqual(l4["mcu_line2_defect_guard"], "ENFORCED_LINE2_ONLY")

        # Layer 5: Network Sockets
        l5 = SystemAnomalyDetector.audit_network_and_sockets()
        self.assertEqual(l5["layer"], "network_sockets")

        # Layer 6: Dynamic Tool Immune
        l6 = SystemAnomalyDetector.audit_dynamic_tools_catalog()
        self.assertEqual(l6["layer"], "dynamic_tools_immune")
        self.assertIn("quarantined_tools", l6)

        print(f"[Self-Healing L1-L6 Audit] RAM: {l1['ram_used_percent']}% | Circuits: {l3['total_circuits']} | Tools: {l6['total_tools']}")

    def test_02_ast_semantic_mutation_error_classes(self):
        """Test HealingPatchTournament AST mutations across 6 major Python error types."""
        # 1. ZeroDivisionError
        code_div = "def run(args):\n    return a / b"
        patched_div = HealingPatchTournament.generate_ast_candidate(code_div, "division by zero", "ZeroDivisionError")
        self.assertIn("if b != 0 else 0.0", patched_div)

        # 2. KeyError
        code_key = 'def run(args):\n    return args["value"]'
        patched_key = HealingPatchTournament.generate_ast_candidate(code_key, "KeyError: 'value'", "KeyError")
        self.assertIn('args.get("value", 0)', patched_key)

        # 3. TypeError
        code_type = "def run(args:\n    return args.keys()"
        patched_type = HealingPatchTournament.generate_ast_candidate(code_type, "TypeError: expected dict", "TypeError")
        self.assertIn("isinstance(args, dict)", patched_type)

        # 4. AttributeError
        code_attr = "def run(args:\n    return args.get_data()"
        patched_attr = HealingPatchTournament.generate_ast_candidate(code_attr, "AttributeError: 'NoneType'", "AttributeError")
        self.assertIn("if args is None:", patched_attr)

        # 5. IndexError
        code_idx = "def run(args):\n    return items[0]"
        patched_idx = HealingPatchTournament.generate_ast_candidate(code_idx, "IndexError: list index out of range", "IndexError")
        self.assertIn("len(items) > 0", patched_idx)

        # 6. ValueError
        code_val = "def run(args):\n    return float(x)"
        patched_val = HealingPatchTournament.generate_ast_candidate(code_val, "ValueError: could not convert string", "ValueError")
        self.assertIn("isdigit()", patched_val)

        print("[Self-Healing AST Healer] Successfully validated 6 Error Classes (ZeroDivision, KeyError, TypeError, AttributeError, IndexError, ValueError)")

    def test_03_full_system_healing_sweep(self):
        """Test AutonomousSelfHealingEngine executing complete 6-layer sweep."""
        res = self.engine.run_full_system_heal()
        self.assertEqual(res["status"], "success")
        self.assertIn(res["system_equilibrium"], ("OPTIMAL", "STABILIZED"))
        self.assertGreaterEqual(len(res["actions_executed"]), 5)
        self.assertIn("diagnostic_layers", res)
        print(f"[Full System Heal] Equilibrium: {res['system_equilibrium']} | Duration: {res['duration_ms']}ms | Actions: {len(res['actions_executed'])}")

    def test_04_tool_immune_quarantine_lifecycle(self):
        """Test Tool Immune System quarantine isolation and unquarantine restoration."""
        tool_name = "test_quarantine_dummy"
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{tool_name}.py")
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{tool_name}.py")

        dummy_code = "def run(args: dict) -> dict:\n    return {'success': True, 'val': 100}\n"
        dummy_test = f"import unittest\nfrom dynamic_tools.{tool_name} import run\nclass T(unittest.TestCase):\n    def test_r(self):\n        self.assertTrue(run({{}})['success'])\n"

        reg = self.forge.register_and_verify_tool(tool_name, dummy_code, dummy_test, description="Quarantine test tool")
        self.assertTrue(reg["success"])

        # 1. Quarantine tool
        q_ok = self.engine.quarantine_tool(tool_name, reason="Simulated execution crash loop")
        self.assertTrue(q_ok)

        m = ToolForgeManifest.load()
        self.assertTrue(m["tools"][tool_name].get("quarantined"))

        # 2. Unquarantine tool
        unq_ok = self.engine.unquarantine_tool(tool_name)
        self.assertTrue(unq_ok)

        m2 = ToolForgeManifest.load()
        self.assertFalse(m2["tools"][tool_name].get("quarantined"))
        print(f"[Tool Immune Quarantine] Tool '{tool_name}' successfully passed Quarantine -> Isolation -> Restoration lifecycle.")

    def test_05_circuit_breaker_canary_auto_reset(self):
        """Test canary probing and auto-resetting tripped circuit breakers."""
        breaker = global_circuit_registry.get_or_create("test_canary_breaker", failure_threshold=2)
        # Force trip breaker
        breaker.trip()
        self.assertEqual(breaker.state, CircuitState.OPEN)

        # Run canary reset
        reset_res = self.engine.reset_tripped_circuits(force=True)
        self.assertIn("test_canary_breaker", reset_res["resets_performed"])
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        print(f"[Circuit Canary Healer] Trip -> Canary Probe -> Auto-Reset to CLOSED verified.")

    def test_06_patch_tournament_healing_execution(self):
        """Test autonomous patch tournament healing a fragile tool with regression test synthesis."""
        tool_name = "v5_fragile_stats"
        code = '''
def run(args: dict) -> dict:
    total = args["total"]
    count = args["count"]
    average = total / count
    return {"average": average, "success": True}
'''
        test_code = f'''
import unittest
from dynamic_tools.{tool_name} import run

class TestFragileStats(unittest.TestCase):
    def test_nominal(self):
        res = run({{"total": 10, "count": 2}})
        self.assertEqual(res.get("average"), 5.0)

if __name__ == "__main__":
    unittest.main()
'''
        reg = self.forge.register_and_verify_tool(tool_name, code, test_code, description="Stats calculator")
        self.assertTrue(reg["success"])

        # Heal the tool with missing key and zero count
        heal_res = self.engine.heal_specific_tool(
            tool_name=tool_name,
            failing_input={"total": 50, "count": 0},
            error_message="ZeroDivisionError: division by zero",
        )
        self.assertTrue(heal_res["success"], f"Healing failed: {heal_res.get('error')}")
        self.assertIn("winning_strategy", heal_res)
        self.assertGreaterEqual(heal_res["fitness"], 50.0)
        print(f"[Patch Tournament] Winner: {heal_res['winning_strategy']} | Fitness: {heal_res['fitness']} | New Version: v{heal_res['new_version']}")

    def test_07_rest_api_self_heal_endpoints(self):
        """Test Flask REST API routes (/api/heal/system, /api/heal/telemetry, /api/heal/reset_circuits)."""
        # 1. /api/heal/telemetry
        r_telem = self.client.get("/api/heal/telemetry")
        self.assertEqual(r_telem.status_code, 200)
        d_telem = json.loads(r_telem.data)
        self.assertTrue(d_telem["success"])
        self.assertIn("quarantined_tools_count", d_telem["telemetry"])

        # 2. /api/heal/reset_circuits
        r_circ = self.client.post("/api/heal/reset_circuits", json={"force": False})
        self.assertEqual(r_circ.status_code, 200)

        # 3. /api/heal/system
        r_sys = self.client.post("/api/heal/system")
        self.assertEqual(r_sys.status_code, 200)
        d_sys = json.loads(r_sys.data)
        self.assertEqual(d_sys["status"], "success")

        print("[REST API Gate] /api/heal/telemetry, /api/heal/reset_circuits, /api/heal/system verified with HTTP 200.")

    def test_08_natural_language_self_healing_intent(self):
        """Test SelfHealingIntent handling natural language repair commands."""
        from intents.self_healing_intent import SelfHealingIntent

        self.assertTrue(SelfHealingIntent.can_handle("self heal"))
        self.assertTrue(SelfHealingIntent.can_handle("repair system"))
        self.assertTrue(SelfHealingIntent.can_handle("fix error"))

        msg, agent, artifacts = SelfHealingIntent.execute("please self heal the system", "self heal the system")
        self.assertEqual(agent, "self_healing_agent")
        self.assertIn("Self-Healing Sentinel", msg)
        self.assertIn("Status:", msg)
        print("[Intent Gate] Natural language 'self heal' intent successfully triggered 6-layer protocol.")


if __name__ == "__main__":
    unittest.main()
