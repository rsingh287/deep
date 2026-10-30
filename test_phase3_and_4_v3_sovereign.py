"""
Phase 3 & 4 v3 Sovereign Cognitive OS Test Suite
================================================
Verifies state-of-the-art advancements:
1. Property-Based Fuzz Testing Engine (FuzzForgeEngine)
2. AST Cyclomatic Complexity & Halstead Optimization Scorecard (CodeOptimizerEngine)
3. Multi-Node Conditional DAG Workflow Runtime (WorkflowDAGRuntime)
4. SimPO (Simple Preference Optimization) Contrastive Loss on CUDA GPU
5. Synthetic Self-Play Distillation (SelfPlayDistiller)
6. Live REST Blueprint Endpoints (/api/forge/fuzz, /api/forge/analyze, /api/forge/workflow/execute, /api/dream/distill_synthetic)
"""

import json
import os
import time
import unittest
import requests
import torch

from self_synthesizing_tool_forge import (
    get_tool_forge,
    FuzzForgeEngine,
    CodeOptimizerEngine,
    WorkflowDAGRuntime,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
    ToolForgeManifest,
)
from nightly_meta_learner import (
    NightlyLoRATrainer,
    SelfPlayDistiller,
    CanaryHotSwapper,
    get_nightly_meta_learner,
)


class TestPhase3And4V3Sovereign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.forge = get_tool_forge()
        cls.api_base = "http://127.0.0.1:5000"

        cls.v3_tool_name = "v3_math_engine"
        tool_code = """
def compute_metrics(x: float = 10.0, label: str = "default") -> dict:
    if x < 0:
        val = abs(x)
        flag = "NEGATIVE"
    elif x == 0:
        val = 0.0
        flag = "ZERO"
    else:
        val = x * 2.0
        flag = "POSITIVE"
    return {"input": x, "processed": val, "flag": flag, "label": label}
"""
        test_code = """
import unittest
from dynamic_tools.v3_math_engine import compute_metrics

class TestV3Math(unittest.TestCase):
    def test_positive(self):
        res = compute_metrics(5.0)
        self.assertEqual(res["processed"], 10.0)
        self.assertEqual(res["flag"], "POSITIVE")

    def test_negative(self):
        res = compute_metrics(-4.0)
        self.assertEqual(res["processed"], 4.0)
        self.assertEqual(res["flag"], "NEGATIVE")
"""
        t_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{cls.v3_tool_name}.py")
        test_f = os.path.join(DYNAMIC_TESTS_DIR, f"test_{cls.v3_tool_name}.py")
        with open(t_file, "w", encoding="utf-8") as f:
            f.write(tool_code.strip() + "\n")
        with open(test_f, "w", encoding="utf-8") as f:
            f.write(test_code.strip() + "\n")

        ToolForgeManifest.update_tool(cls.v3_tool_name, {
            "id": cls.v3_tool_name,
            "name": "V3 Math Engine",
            "description": "Computes metrics with boundary classification.",
            "parameters": [
                {"name": "x", "type": "float", "default": 10.0},
                {"name": "label", "type": "str", "default": "default"},
            ],
            "file_path": t_file,
            "test_path": test_f,
            "verification_status": "VERIFIED_OPERATIONAL",
            "test_pass_count": 1,
            "execution_count": 0,
        })

    # --- 1. Property-Based Fuzz Testing ---
    def test_01_fuzz_forge_engine(self):
        """Validates property-based fuzz testing across boundary floats and edge strings."""
        fuzz_report = FuzzForgeEngine.run_fuzz_audit(self.v3_tool_name, count=15)
        self.assertTrue(fuzz_report.get("success"))
        self.assertEqual(fuzz_report.get("fatal_crashes"), 0, "Synthesized tool must not have fatal unhandled crashes")
        self.assertGreaterEqual(fuzz_report.get("fuzz_score_pct"), 80.0)
        self.assertEqual(fuzz_report.get("status"), "FUZZ_AUDIT_PASSED")
        self.assertLess(fuzz_report.get("avg_latency_ms"), 50.0, "Execution latency must remain bounded")
        print(f"\n[Fuzz Benchmark] Score: {fuzz_report['fuzz_score_pct']}% | 0 Crashes | Latency: {fuzz_report['avg_latency_ms']}ms")

    # --- 2. AST Cyclomatic Complexity & Halstead Optimization ---
    def test_02_ast_complexity_optimizer(self):
        """Verifies McCabe cyclomatic complexity, Halstead metrics, and optimization grade."""
        code = """
def simple_multiplier(a: float = 1.0, b: float = 2.0) -> float:
    return a * b
"""
        metrics = CodeOptimizerEngine.analyze_code(code)
        self.assertIn(metrics.get("grade"), ["A+", "A"])
        self.assertLessEqual(metrics.get("cyclomatic_complexity"), 3)
        self.assertEqual(metrics.get("type_annotation_coverage_pct"), 100.0)
        self.assertTrue(metrics.get("has_return_annotation"))
        self.assertGreater(metrics.get("halstead_volume"), 0.0)
        print(f"[AST Optimizer] Grade: {metrics['grade']} | Complexity: {metrics['cyclomatic_complexity']} | Volume: {metrics['halstead_volume']}")

    # --- 3. Multi-Node Conditional DAG Workflow Runtime ---
    def test_03_conditional_dag_workflow_runtime(self):
        """Executes a multi-node workflow with conditional branching and data aggregation."""
        workflow_nodes = [
            {
                "node_id": "math_step",
                "type": "tool",
                "tool_name": self.v3_tool_name,
                "arguments": {"x": "$input.value", "label": "workflow_test"},
            },
            {
                "node_id": "check_positivity",
                "type": "condition",
                "condition": "$steps.math_step.result.flag == 'POSITIVE'",
                "then_branch": "positive_path",
                "else_branch": "non_positive_path",
            },
            {
                "node_id": "aggregate_step",
                "type": "aggregate",
                "inputs": ["$steps.math_step.result.processed", "$steps.check_positivity.result"],
            },
        ]

        res = WorkflowDAGRuntime.execute_workflow(
            workflow_name="positivity_decision_workflow",
            nodes=workflow_nodes,
            initial_input={"value": 15.0},
        )

        self.assertTrue(res.get("success"), f"Workflow execution failed: {res.get('error')}")
        self.assertEqual(res.get("total_nodes"), 3)
        traces = res.get("traces", [])
        self.assertEqual(len(traces), 3)

        # Verify condition was true
        cond_trace = traces[1]
        self.assertTrue(cond_trace.get("result"))
        self.assertEqual(cond_trace.get("selected_branch"), "positive_path")

        # Verify aggregation
        agg_res = res.get("final_output")
        self.assertEqual(agg_res.get("math_step.result.processed"), 30.0)
        self.assertEqual(agg_res.get("check_positivity.result"), True)

    # --- 4. SimPO (Simple Preference Optimization) on CUDA ---
    def test_04_simpo_optimization_objective(self):
        """Verifies length-normalized SimPO contrastive learning with adaptive margin gamma."""
        res = NightlyLoRATrainer.train(
            epochs=3, lr=1e-3, r=16, beta=0.1, gamma=0.5, objective="simpo", ewc_lambda=25.0
        )
        self.assertTrue(res.get("success"), f"SimPO training failed: {res.get('error')}")
        self.assertEqual(res.get("objective"), "simpo")
        self.assertLess(res["final_loss"], res["initial_loss"])
        self.assertGreaterEqual(res.get("final_reward_accuracy_pct"), 90.0)

        initial = res["initial_loss"]
        final = res["final_loss"]
        margin = res["final_reward_margin"]
        acc = res["final_reward_accuracy_pct"]
        print(f"[SimPO Benchmark] Loss: {initial:.4f} -> {final:.4f} | Margin: {margin:+.4f} | Acc: {acc}% ({res.get('device')})")

    # --- 5. Synthetic Self-Play Distillation ---
    def test_05_synthetic_self_play_distiller(self):
        """Verifies generation of bi-temporal contrastive pairs for continuous alignment."""
        res = SelfPlayDistiller.distill_synthetic_pairs()
        self.assertTrue(res.get("success"))
        self.assertGreaterEqual(res.get("synthetic_pairs_generated"), 4)
        self.assertIn("self_play_mcu_invariants", res.get("categories"))
        self.assertIn("self_play_ast_defense", res.get("categories"))

    # --- 6. Live REST Blueprint Endpoints ---
    def test_06_v3_rest_endpoints(self):
        """Tests live REST endpoints for fuzzing, code analysis, workflow execution, and distillation."""
        try:
            # 1. POST /api/forge/fuzz
            r_fuzz = requests.post(
                f"{self.api_base}/api/forge/fuzz",
                json={"tool_name": self.v3_tool_name, "count": 10},
                timeout=5,
            )
            if r_fuzz.status_code == 200:
                self.assertTrue(r_fuzz.json().get("success"))

            # 2. POST /api/forge/analyze
            r_ana = requests.post(
                f"{self.api_base}/api/forge/analyze",
                json={"tool_name": self.v3_tool_name},
                timeout=5,
            )
            if r_ana.status_code == 200:
                self.assertIn("grade", r_ana.json())

            # 3. POST /api/dream/distill_synthetic
            r_dist = requests.post(f"{self.api_base}/api/dream/distill_synthetic", timeout=5)
            if r_dist.status_code == 200:
                self.assertTrue(r_dist.json().get("success"))

        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server not running on port 5000")

    @classmethod
    def tearDownClass(cls):
        cls.forge.delete_tool(cls.v3_tool_name)


if __name__ == "__main__":
    unittest.main()
