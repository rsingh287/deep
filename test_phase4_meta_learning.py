"""
Phase 4 Integration Test Suite: Nightly Meta-Learner & Continuous Fine-Tuning
=============================================================================
Verifies:
1. DPO Preference Data Curation (chosen vs rejected formatting)
2. Local GPU LoRA Training & Loss Convergence on NVIDIA RTX
3. 5-Point Enterprise Self-Benchmarking Readiness Audit
4. Autonomous Modelfile Synthesis
5. Live REST Endpoints (/api/dream/telemetry, /api/dream/curate, /api/dream/readiness_audit)
"""

import os
import sys
import time
import unittest
import torch
import requests

from nightly_meta_learner import (
    get_nightly_meta_learner,
    DPOPreferenceCurator,
    NightlyLoRATrainer,
    NightlyReadinessAudit,
    AutonomousModelHotSwapper,
    DPO_DATASET_FILE,
    CHECKPOINT_PATH,
    MODELFILE_PATH,
)


class TestPhase4MetaLearning(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.learner = get_nightly_meta_learner()
        cls.api_base = "http://127.0.0.1:5000"

    # --- 1. DPO Preference Curation ---
    def test_01_dpo_preference_curation(self):
        res = DPOPreferenceCurator.curate_preference_pairs()
        self.assertTrue(res.get("success"), f"DPO curation failed: {res.get('error')}")
        self.assertGreaterEqual(res.get("total_pairs_curated", 0), 3)
        self.assertTrue(os.path.exists(DPO_DATASET_FILE))

        # Inspect file content
        with open(DPO_DATASET_FILE, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertGreaterEqual(len(lines), 3)

        sample = None
        import json
        for l in lines:
            d = json.loads(l)
            if "chosen" in d and "rejected" in d:
                sample = d
                break

        self.assertIsNotNone(sample, "Curated dataset must contain chosen and rejected fields")
        self.assertIn("prompt", sample)
        self.assertIn("category", sample)

    # --- 2. GPU LoRA Training & Convergence ---
    def test_02_gpu_lora_training_convergence(self):
        epochs = 3
        res = NightlyLoRATrainer.train(epochs=epochs, lr=1e-3, r=16)
        self.assertTrue(res.get("success"), f"LoRA training failed: {res.get('error')}")
        self.assertEqual(res.get("epochs"), epochs)
        self.assertTrue(os.path.exists(CHECKPOINT_PATH))

        # Verify loss convergence (initial vs final)
        initial_loss = res["initial_loss"]
        final_loss = res["final_loss"]
        self.assertLess(final_loss, initial_loss, f"Loss must decrease during training: {initial_loss} -> {final_loss}")
        print(f"\n[Test Benchmark] LoRA 3-Epoch Loss Convergence: {initial_loss:.4f} -> {final_loss:.4f} in {res.get('duration_seconds')}s ({res.get('device')})")

        # Verify saved PyTorch checkpoint
        ckpt = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
        self.assertIn("lora_A", ckpt)
        self.assertIn("lora_B", ckpt)
        self.assertIn("scaling", ckpt)
        self.assertEqual(ckpt["rank"], 16)

    # --- 3. Self-Benchmarking Readiness Audit ---
    def test_03_readiness_audit_dimensions(self):
        audit = NightlyReadinessAudit.run_audit()
        self.assertTrue(audit.get("success"))
        self.assertGreaterEqual(audit["readiness_score"], 80, f"Readiness score below threshold: {audit['readiness_score']}/100")
        self.assertEqual(audit["status"], "PASSED_AUDIT")

        dims = audit["dimensions"]
        self.assertTrue(dims["dimension_1_guardrail_defense"]["passed"])
        self.assertTrue(dims["dimension_2_voice_brevity"]["passed"])
        self.assertTrue(dims["dimension_3_mcu_hardware_directives"]["passed"])
        self.assertTrue(dims["dimension_4_local_music_strict"]["passed"])
        self.assertTrue(dims["dimension_5_code_synthesis"]["passed"])
        print(f"[Test Benchmark] Readiness Audit Score: {audit['readiness_score']}/100 [PASSED_AUDIT]")

    # --- 4. Autonomous Modelfile Synthesis ---
    def test_04_modelfile_generation(self):
        modelfile = AutonomousModelHotSwapper.generate_modelfile()
        self.assertTrue(os.path.exists(modelfile))

        with open(modelfile, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("FROM", content)
        self.assertIn("SYSTEM", content)
        self.assertIn("Executive Voice Brevity", content)
        self.assertIn("PIC18F85K22", content)
        self.assertIn("MCP9701", content)
        self.assertIn("temperature 0.2", content)

    # --- 5. Live REST Endpoints ---
    def test_05_rest_api_dream_endpoints(self):
        try:
            # 1. GET /api/dream/telemetry
            r_tele = requests.get(f"{self.api_base}/api/dream/telemetry", timeout=5)
            self.assertEqual(r_tele.status_code, 200)
            data_tele = r_tele.json()
            self.assertTrue(data_tele.get("success"))
            self.assertTrue(data_tele.get("has_checkpoint"))
            self.assertTrue(data_tele.get("cuda_available"))

            # 2. POST /api/dream/curate
            r_cur = requests.post(f"{self.api_base}/api/dream/curate", timeout=5)
            self.assertEqual(r_cur.status_code, 200)
            data_cur = r_cur.json()
            self.assertTrue(data_cur.get("success"))

            # 3. POST /api/dream/readiness_audit
            r_aud = requests.post(f"{self.api_base}/api/dream/readiness_audit", timeout=5)
            self.assertEqual(r_aud.status_code, 200)
            data_aud = r_aud.json()
            self.assertTrue(data_aud.get("success"))
            self.assertEqual(data_aud.get("status"), "PASSED_AUDIT")

        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server is not currently running on port 5000")


if __name__ == "__main__":
    unittest.main()
