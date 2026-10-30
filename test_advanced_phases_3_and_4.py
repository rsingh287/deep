"""
Advanced Phases 3 & 4 Verification Test Suite
============================================
Comprehensive test suite verifying advanced cognitive features:

Advanced Phase 3 (Tool Forge v2):
1. AST Shield Sandbox Escape Defense (socket, introspection, __subclasses__)
2. Sandboxed Secret Sanitization (environment credential scrubbing)
3. Immutable Versioning & Snapshot Rollback (ToolVersionManager)
4. Reflexion Engine Diagnostic Error Parsing
5. Multi-Tool Composite DAG Pipeline Chaining (ToolChainPipeline)
6. Semantic Tool Discovery & Natural Language Auto-Dispatch (SemanticToolIndex)

Advanced Phase 4 (Machine Dreaming & Meta-Learning v2):
7. Mathematical Bradley-Terry DPO Loss & Reward Margin Convergence
8. Elastic Weight Consolidation (EWC) Fisher Information Computation
9. Shadow Canary A/B Quality & Latency Benchmark (CanaryHotSwapper)
10. Autonomous Background Sleep Daemon Lifecycle (NightlyDreamDaemon)
11. Advanced Cockpit REST Blueprint Endpoints
"""

import json
import os
import sys
import time
import unittest
import requests
import torch

from self_synthesizing_tool_forge import (
    get_tool_forge,
    ASTSecurityShield,
    SandboxedEnvironment,
    ToolVersionManager,
    ReflexionEngine,
    SemanticToolIndex,
    ToolChainPipeline,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
)
from nightly_meta_learner import (
    NightlyLoRATrainer,
    ElasticWeightConsolidation,
    CanaryHotSwapper,
    NightlyDreamDaemon,
    get_nightly_meta_learner,
    CHECKPOINT_PATH,
)


class TestAdvancedPhases3And4(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.forge = get_tool_forge()
        cls.api_base = "http://127.0.0.1:5000"

        # Register two test tools for chaining and versioning
        cls.tool_1_name = "adv_temp_c_to_f"
        tool_1_code = """
def c_to_f(celsius: float = 0.0) -> dict:
    f = (celsius * 9.0 / 5.0) + 32.0
    return {"celsius": celsius, "fahrenheit": round(f, 2)}
"""
        test_1_code = """
import unittest
from dynamic_tools.adv_temp_c_to_f import c_to_f

class TestCtoF(unittest.TestCase):
    def test_c_to_f(self):
        res = c_to_f(0.0)
        self.assertEqual(res["fahrenheit"], 32.0)
"""
        cls.tool_2_name = "adv_temp_evaluator"
        tool_2_code = """
def eval_temp(fahrenheit: float = 32.0) -> dict:
    status = "FREEZING" if fahrenheit <= 32.0 else "COMFORTABLE" if fahrenheit < 85.0 else "HOT"
    return {"fahrenheit": fahrenheit, "classification": status}
"""
        test_2_code = """
import unittest
from dynamic_tools.adv_temp_evaluator import eval_temp

class TestEval(unittest.TestCase):
    def test_eval(self):
        res = eval_temp(32.0)
        self.assertEqual(res["classification"], "FREEZING")
"""
        # Save and verify both tools
        for t_name, code, t_code, desc in [
            (cls.tool_1_name, tool_1_code, test_1_code, "Converts Celsius to Fahrenheit degrees."),
            (cls.tool_2_name, tool_2_code, test_2_code, "Evaluates Fahrenheit into climate classifications."),
        ]:
            t_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{t_name}.py")
            test_f = os.path.join(DYNAMIC_TESTS_DIR, f"test_{t_name}.py")
            with open(t_file, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")
            with open(test_f, "w", encoding="utf-8") as f:
                f.write(t_code.strip() + "\n")

            from self_synthesizing_tool_forge import ToolForgeManifest
            ToolForgeManifest.update_tool(t_name, {
                "id": t_name,
                "name": t_name.replace("_", " ").title(),
                "description": desc,
                "parameters": [{"name": "celsius" if "c_to_f" in t_name else "fahrenheit", "type": "float", "default": 0.0}],
                "file_path": t_file,
                "test_path": test_f,
                "verification_status": "VERIFIED_OPERATIONAL",
                "test_pass_count": 1,
                "execution_count": 0,
            })
            ToolVersionManager.save_version(t_name, code, t_code, "Setup initial version")

    # =========================================================================
    # ADVANCED PHASE 3: TOOL FORGE V2
    # =========================================================================

    def test_01_ast_shield_escape_defense(self):
        """Validates blocking of socket networking and Python introspection escapes."""
        # 1. Banned network socket
        socket_code = """
import socket
def fetch_ip():
    s = socket.socket()
    return s.connect(('1.1.1.1', 80))
"""
        is_safe, msg = ASTSecurityShield.validate_code(socket_code)
        self.assertFalse(is_safe)
        self.assertIn("socket", msg)

        # 2. Introspection breakout (__subclasses__)
        introspection_code = """
def escape_sandbox():
    return object.__subclasses__()
"""
        is_safe, msg = ASTSecurityShield.validate_code(introspection_code)
        self.assertFalse(is_safe)
        self.assertIn("__subclasses__", msg)

    def test_02_sandboxed_secret_sanitization(self):
        """Verifies environment variables are scrubbed of secrets before subprocess spawning."""
        os.environ["DUMMY_OPENAI_API_KEY"] = "sk-secret-123456"
        os.environ["DATABASE_URL"] = "postgres://deep:pass@localhost:5432/deep_db"
        os.environ["SYSTEM_TOKEN"] = "token-xyz"

        sanitized = SandboxedEnvironment.get_sanitized_env()

        self.assertNotIn("DUMMY_OPENAI_API_KEY", sanitized)
        self.assertNotIn("DATABASE_URL", sanitized)
        self.assertNotIn("SYSTEM_TOKEN", sanitized)
        self.assertIn("PATH", sanitized)

    def test_03_immutable_versioning_and_rollback(self):
        """Tests snapshot creation and rolling back to a previous stable version."""
        tool_name = self.tool_1_name
        v1_versions = ToolVersionManager.list_versions(tool_name)
        self.assertGreaterEqual(len(v1_versions), 1)

        # Apply a modification (v2)
        v2_code = """
def c_to_f(celsius: float = 0.0) -> dict:
    f = (celsius * 1.8) + 32.0
    return {"celsius": celsius, "fahrenheit": round(f, 4), "version": 2}
"""
        v2_test = """
import unittest
from dynamic_tools.adv_temp_c_to_f import c_to_f
class TestCtoF(unittest.TestCase):
    def test_v2(self):
        self.assertEqual(c_to_f(0.0)["version"], 2)
"""
        v2_num = ToolVersionManager.save_version(tool_name, v2_code, v2_test, "Upgraded precision to 4 decimals")
        self.assertEqual(v2_num, len(v1_versions) + 1)

        # Write v2 code to disk
        t_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{tool_name}.py")
        with open(t_file, "w", encoding="utf-8") as f:
            f.write(v2_code.strip() + "\n")

        # Rollback to v1
        rb_res = ToolVersionManager.rollback(tool_name)
        self.assertTrue(rb_res.get("success"), f"Rollback failed: {rb_res.get('error')}")
        self.assertEqual(rb_res.get("restored_version"), v1_versions[-1]["version"])

        # Check restored file
        with open(t_file, "r", encoding="utf-8") as f:
            restored_code = f.read()
        self.assertNotIn('"version": 2', restored_code)

    def test_04_reflexion_engine_diagnostics(self):
        """Verifies traceback parsing and diagnostic hint generation."""
        mock_trace = """
Traceback (most recent call last):
  File "C:\\code\\dynamic_tools\\tests\\test_dummy.py", line 14, in test_calc
    self.assertEqual(res["result"], 42)
AssertionError: 30 != 42
"""
        diag = ReflexionEngine.diagnose_failure(mock_trace)
        self.assertEqual(diag["error_type"], "AssertionError")
        self.assertIn("30 != 42", diag["details"])
        self.assertEqual(diag["failing_line"], "test_dummy.py:14")
        self.assertIn("Expected output differs", diag["diagnostic_hint"])

    def test_05_multi_tool_chain_pipeline(self):
        """Executes a 2-step composite DAG pipeline passing output from tool 1 into tool 2."""
        pipeline_steps = [
            {
                "step_id": "step_c_to_f",
                "tool_name": self.tool_1_name,
                "arguments": {"celsius": "$input.celsius"},
            },
            {
                "step_id": "step_evaluate",
                "tool_name": self.tool_2_name,
                "arguments": {"fahrenheit": "$steps.step_c_to_f.result.fahrenheit"},
            },
        ]

        chain_res = ToolChainPipeline.execute_chain(
            pipeline_name="weather_eval_dag",
            steps=pipeline_steps,
            initial_input={"celsius": 0.0},
        )

        self.assertTrue(chain_res.get("success"), f"Pipeline execution failed: {chain_res.get('error')}")
        self.assertEqual(chain_res.get("total_steps"), 2)
        final_out = chain_res.get("final_output")
        self.assertIsInstance(final_out, dict)
        self.assertEqual(final_out.get("fahrenheit"), 32.0)
        self.assertEqual(final_out.get("classification"), "FREEZING")
        self.assertEqual(len(chain_res.get("traces")), 2)

    def test_06_semantic_tool_discovery_and_auto_dispatch(self):
        """Verifies semantic tool search and autonomous argument extraction & dispatch."""
        # 1. Semantic Discovery
        matches = SemanticToolIndex.discover("convert temperature degrees celsius", top_k=2)
        self.assertGreaterEqual(len(matches), 1)
        best_match = matches[0]
        self.assertEqual(best_match["tool"]["id"], self.tool_1_name)
        self.assertGreaterEqual(best_match["score"], 0.25)

        # 2. Natural Language Auto-Dispatch
        dispatch_res = self.forge.auto_dispatch("please run adv_temp_c_to_f with celsius=100")
        self.assertTrue(dispatch_res.get("success"), f"Auto-dispatch failed: {dispatch_res.get('error')}")
        self.assertEqual(dispatch_res["result"]["fahrenheit"], 212.0)

    # =========================================================================
    # ADVANCED PHASE 4: MACHINE DREAMING & META-LEARNER V2
    # =========================================================================

    def test_07_mathematical_dpo_reward_margin(self):
        """Verifies Bradley-Terry DPO optimization, positive reward margin, and reward accuracy."""
        epochs = 3
        dpo_res = NightlyLoRATrainer.train(epochs=epochs, lr=1e-3, r=16, beta=0.1, ewc_lambda=25.0)
        self.assertTrue(dpo_res.get("success"), f"DPO training failed: {dpo_res.get('error')}")

        # Final loss must decrease or remain well-optimized
        initial_loss = dpo_res["initial_loss"]
        final_loss = dpo_res["final_loss"]
        self.assertLess(final_loss, initial_loss)

        # Reward margin must be positive
        reward_margin = dpo_res.get("final_reward_margin", 0.0)
        self.assertGreater(reward_margin, 0.0, f"Reward margin must be positive: {reward_margin}")

        # Reward accuracy must reach >= 90%
        reward_acc = dpo_res.get("final_reward_accuracy_pct", 0.0)
        self.assertGreaterEqual(reward_acc, 90.0, f"Reward accuracy must reach high fidelity: {reward_acc}%")

        print(
            f"\n[DPO Benchmark] 3-Epoch Optimization: Loss {initial_loss:.4f} -> {final_loss:.4f} | "
            f"Reward Margin: +{reward_margin:.4f} | Reward Acc: {reward_acc}% ({dpo_res.get('device')})"
        )

    def test_08_elastic_weight_consolidation_fisher_matrix(self):
        """Validates Fisher Information Matrix computation across canonical anchors."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        from lora_self_learning import DeepWorkstationLoRAModel

        model = DeepWorkstationLoRAModel(dim=768, vocab_size=512, r=16).to(device)
        fisher_diag, optimal_params = ElasticWeightConsolidation.compute_fisher_information(
            model, device, dim=768, vocab_size=512
        )

        self.assertIn("lora_q.lora_A", fisher_diag)
        self.assertIn("lora_q.lora_B", fisher_diag)

        total_fisher_mass = sum(f.sum().item() for f in fisher_diag.values())
        self.assertGreater(total_fisher_mass, 0.0, "Fisher Information mass must be strictly positive")

        # Test zero EWC loss at optimal parameters
        zero_ewc = ElasticWeightConsolidation.compute_ewc_loss(model, fisher_diag, optimal_params, ewc_lambda=100.0)
        self.assertAlmostEqual(zero_ewc.item(), 0.0, places=4)

    def test_09_shadow_canary_ab_benchmark(self):
        """Verifies shadow canary evaluation against golden probes."""
        canary = CanaryHotSwapper.evaluate_canary("deep-sovereign:latest")
        self.assertTrue(canary.get("success"))
        self.assertGreaterEqual(canary.get("canary_score", 0), 70)
        self.assertTrue(canary.get("canary_passed"))
        self.assertEqual(len(canary.get("probes")), 3)
        print(f"[Canary Benchmark] Score: {canary['canary_score']}/100 in {canary['total_benchmark_time_ms']}ms")

    def test_10_nightly_dream_daemon_lifecycle(self):
        """Tests starting, querying, and stopping the background dream daemon."""
        daemon = NightlyDreamDaemon(idle_threshold_seconds=600, check_interval_seconds=5)
        status_before = daemon.get_status()
        self.assertFalse(status_before.get("daemon_running"))

        daemon.start()
        status_running = daemon.get_status()
        self.assertTrue(status_running.get("daemon_running"))
        self.assertEqual(status_running.get("idle_threshold_seconds"), 600)
        self.assertTrue(status_running.get("cuda_available"))

        daemon.stop()
        status_stopped = daemon.get_status()
        self.assertFalse(status_stopped.get("daemon_running"))

    def test_11_advanced_rest_endpoints(self):
        """Tests live REST endpoints for chaining, discovery, canary, and daemon."""
        try:
            # 1. POST /api/forge/chain/execute
            r_chain = requests.post(
                f"{self.api_base}/api/forge/chain/execute",
                json={
                    "pipeline_name": "rest_weather_pipeline",
                    "steps": [
                        {
                            "step_id": "step_c_to_f",
                            "tool_name": self.tool_1_name,
                            "arguments": {"celsius": "$input.celsius"},
                        },
                        {
                            "step_id": "step_eval",
                            "tool_name": self.tool_2_name,
                            "arguments": {"fahrenheit": "$steps.step_c_to_f.result.fahrenheit"},
                        },
                    ],
                    "initial_input": {"celsius": 100.0},
                },
                timeout=5,
            )
            if r_chain.status_code == 200:
                data = r_chain.json()
                self.assertTrue(data.get("success"))
                self.assertEqual(data["final_output"]["classification"], "HOT")

            # 2. POST /api/forge/discover
            r_disc = requests.post(
                f"{self.api_base}/api/forge/discover",
                json={"query": "convert celsius", "top_k": 2},
                timeout=5,
            )
            if r_disc.status_code == 200:
                self.assertTrue(r_disc.json().get("success"))

            # 3. GET /api/dream/daemon_status
            r_daemon = requests.get(f"{self.api_base}/api/dream/daemon_status", timeout=5)
            if r_daemon.status_code == 200:
                self.assertIn("cuda_available", r_daemon.json())

        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server not running on port 5000")

    @classmethod
    def tearDownClass(cls):
        cls.forge.delete_tool(cls.tool_1_name)
        cls.forge.delete_tool(cls.tool_2_name)


if __name__ == "__main__":
    unittest.main()
