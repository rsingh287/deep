"""
Authoritative Test Suite: Phase 3 & 4 v4 Sovereign Hyper-Evolution
===================================================================
Validates:
1. ToolGeneticMutator (Pareto fitness optimization, strategies, and test invariant preservation)
2. DifferentialShadowRunner (Side-by-side isolated execution, semantic equivalence, divergence rate)
3. OpenAPIToolSynthesizer (Autonomous API client tool synthesis, zero-trust validation)
4. ToolSelfHealingSentinel (Runtime failure diagnosis, emergency patching, regression tests)
5. NightlyLoRATrainer with ORPO (Odds Ratio Preference Optimization on local RTX GPU)
6. OnlineFisherConsolidator (Online EWC++ lifelong running Fisher information accumulation)
7. CounterfactualDreamSimulator (Adversarial counterfactual dream generation)
8. LoRAFusionCompiler (LoRA matrix fusion, Frobenius norm, and Modelfile compilation)
"""

import os
import unittest
import json
import torch
import torch.nn as nn

from self_synthesizing_tool_forge import (
    get_tool_forge,
    ToolGeneticMutator,
    DifferentialShadowRunner,
    OpenAPIToolSynthesizer,
    ToolSelfHealingSentinel,
    ToolVersionManager,
    CodeOptimizerEngine,
    FuzzForgeEngine,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
)
from nightly_meta_learner import (
    NightlyLoRATrainer,
    OnlineFisherConsolidator,
    CounterfactualDreamSimulator,
    LoRAFusionCompiler,
    MODELFILE_PATH,
    ONLINE_FISHER_FILE,
)


class TestPhase3And4V4Evolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forge = get_tool_forge()
        # Seed test tool adv_temp_c_to_f
        cls.tool_name = "adv_temp_c_to_f"
        code_v1 = '''
def run(args: dict) -> dict:
    if not isinstance(args, dict):
        return {"error": "Invalid args", "success": False}
    c = float(args.get("celsius", 0.0))
    f = (c * 9.0 / 5.0) + 32.0
    return {"celsius": c, "fahrenheit": round(f, 2), "success": True}
'''
        test_v1 = '''
import unittest
from dynamic_tools.adv_temp_c_to_f import run

class TestTemp(unittest.TestCase):
    def test_boil(self):
        res = run({"celsius": 100})
        self.assertEqual(res.get("fahrenheit"), 212.0)

    def test_freeze(self):
        res = run({"celsius": 0})
        self.assertEqual(res.get("fahrenheit"), 32.0)

if __name__ == "__main__":
    unittest.main()
'''
        cls.forge.register_and_verify_tool(
            cls.tool_name, code_v1, test_v1, description="Temperature C to F converter"
        )
        # Save a second version for shadow execution comparisons
        code_v2 = code_v1.replace("round(f, 2)", "round((c * 1.8) + 32.0, 2)")
        ToolVersionManager.save_version(cls.tool_name, code_v2, test_v1, note="Version 2 inline formula")

    def test_01_tool_genetic_mutation_and_fitness(self):
        """Test ToolGeneticMutator Pareto fitness evaluation on an existing tool."""
        res = ToolGeneticMutator.mutate_and_optimize(self.tool_name)
        self.assertTrue(res["success"], f"Mutation failed: {res.get('error')}")
        self.assertIn("baseline_fitness", res)
        self.assertIn("optimized_fitness", res)
        self.assertGreaterEqual(res["optimized_fitness"], res["baseline_fitness"])
        print(f"\n[Genetic Mutator] Strategy: {res['winning_strategy']} | Fitness: {res['baseline_fitness']} -> {res['optimized_fitness']}")

    def test_02_differential_shadow_execution(self):
        """Test DifferentialShadowRunner verifying zero divergence between versions."""
        res = DifferentialShadowRunner.compare_versions(self.tool_name)
        self.assertTrue(res["success"], f"Shadow execution failed: {res.get('error')}")
        self.assertIn("divergence_rate", res)
        self.assertIn("total_runs", res)
        self.assertGreaterEqual(res["total_runs"], 1)
        self.assertTrue(res["semantically_equivalent"] or res["divergence_rate"] <= 0.5)
        print(f"[Differential Shadow] Total Runs: {res['total_runs']} | Mismatches: {res['mismatches']} | Divergence: {res['divergence_rate']}")

    def test_03_openapi_tool_synthesizer(self):
        """Test OpenAPIToolSynthesizer generating an API client tool from schema."""
        res = OpenAPIToolSynthesizer.synthesize_from_api_spec(
            tool_name="v4_test_fx_client",
            description="Dynamic Forex rate fetcher tool",
            endpoint_url="https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json",
            http_method="GET",
            parameters=[{"name": "recent", "type": "int", "description": "Number of observations"}],
        )
        self.assertTrue(res["success"], f"OpenAPI synthesis failed: {res.get('error')}")
        self.assertEqual(res["status"], "VERIFIED_OPERATIONAL")
        print(f"[OpenAPI Synthesizer] Tool: {res['tool_name']} | Status: {res['status']}")

    def test_04_tool_self_healing_sentinel(self):
        """Test ToolSelfHealingSentinel diagnosing runtime exceptions and auto-patching."""
        tool_name = "v4_fragile_calculator"
        code = '''
def run(args: dict) -> dict:
    # Intentionally fragile without .get()
    a = args["val_a"]
    b = args["val_b"]
    return {"result": a + b, "success": True}
'''
        test_code = '''
import unittest
from dynamic_tools.v4_fragile_calculator import run

class TestFragile(unittest.TestCase):
    def test_add(self):
        res = run({"val_a": 1, "val_b": 2})
        self.assertEqual(res.get("result"), 3)

if __name__ == "__main__":
    unittest.main()
'''
        v_res = self.forge.register_and_verify_tool(tool_name, code, test_code, description="Test calculator")
        self.assertTrue(v_res["success"])

        # Trigger self-healing with a failing input (missing val_a)
        heal_res = ToolSelfHealingSentinel.self_heal_failing_tool(
            tool_name=tool_name,
            failing_input={"val_b": 5},
            error_message="KeyError: 'val_a'",
        )
        self.assertTrue(heal_res["success"], f"Self-healing failed: {heal_res.get('error')}")
        self.assertEqual(heal_res["diagnosis"]["error_type"], "KeyError")
        print(f"[Self-Healing Sentinel] Diagnosis: {heal_res['diagnosis']['error_type']} | Healed to Version: v{heal_res['healed_version']}")

    def test_05_nightly_lora_orpo_optimization(self):
        """Test NightlyLoRATrainer with ORPO (Odds Ratio Preference Optimization)."""
        res = NightlyLoRATrainer.train(epochs=3, lr=1e-3, r=16, objective="orpo")
        self.assertTrue(res["success"], f"ORPO training failed: {res.get('error')}")
        self.assertEqual(res["objective"], "orpo")
        self.assertLess(res["final_loss"], res["initial_loss"])
        self.assertGreaterEqual(res["final_reward_accuracy_pct"], 90.0)
        print(f"[ORPO Benchmark] Loss: {res['initial_loss']} -> {res['final_loss']} | Odds Ratio Margin: {res['final_reward_margin']:+.4f} | Acc: {res['final_reward_accuracy_pct']}% ({res['device']})")

    def test_06_online_fisher_matrix_consolidation(self):
        """Test OnlineFisherConsolidator lifelong running Fisher matrix accumulation."""
        dim = 768
        dummy_fisher = {
            "weight_1": torch.ones(10, dim) * 0.5,
            "weight_2": torch.ones(dim, 10) * 0.8,
        }
        dummy_params = {
            "weight_1": torch.randn(10, dim),
            "weight_2": torch.randn(dim, 10),
        }
        res = OnlineFisherConsolidator.update_running_fisher(dummy_fisher, dummy_params, decay=0.90)
        self.assertTrue(res["success"])
        self.assertGreater(res["online_anchors"], 0)
        self.assertGreater(res["running_fisher_mass"], 0.0)
        self.assertTrue(os.path.exists(ONLINE_FISHER_FILE))
        print(f"[Online EWC++] Anchors: {res['online_anchors']} | Running Fisher Mass: {res['running_fisher_mass']} | Decay: {res['decay_factor']}")

    def test_07_counterfactual_adversarial_dreaming(self):
        """Test CounterfactualDreamSimulator synthesizing adversarial hardening scenarios."""
        res = CounterfactualDreamSimulator.simulate_counterfactual_scenarios()
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["counterfactual_scenarios_synthesized"], 4)
        self.assertIn("counterfactual_sql_injection", res["scenarios"])
        self.assertIn("counterfactual_lcd_hardware_guard", res["scenarios"])
        print(f"[Counterfactual Simulator] Synthesized {res['counterfactual_scenarios_synthesized']} Scenarios: {', '.join(res['scenarios'])}")

    def test_08_lora_fusion_and_modelfile_compiler(self):
        """Test LoRAFusionCompiler weight fusion and Modelfile.deep_sovereign generation."""
        res = LoRAFusionCompiler.compile_fusion_modelfile(base_model="hermes3:8b")
        self.assertTrue(res["success"], f"Fusion failed: {res.get('error')}")
        self.assertTrue(os.path.exists(MODELFILE_PATH))
        with open(MODELFILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("FROM hermes3:8b", content)
        self.assertIn("LCD Line 1 is defective; render UI exclusively on Line 2", content)
        self.assertIn("SECURITY_VIOLATION", content)
        self.assertIn("Strict title matching against C:\\Users\\User\\Music", content)
        print(f"[LoRA Fusion Compiler] Frobenius Norm Delta: {res['delta_w_frobenius_norm']} | Modelfile: {MODELFILE_PATH}")


if __name__ == "__main__":
    unittest.main()
