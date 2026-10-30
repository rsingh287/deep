"""
Machine Dreaming & Continuous Meta-Learning Blueprint for D.E.E.P. Cockpit
==========================================================================
Provides REST API endpoints for:
- REM Machine Dreaming memory consolidation
- DPO Preference curation
- Local NVIDIA GPU LoRA training & convergence telemetry
- 5-Point Self-Benchmarking Readiness Audit
- Autonomous Model Hot-Swapping into Ollama
"""

from flask import Blueprint, jsonify, request
from nightly_meta_learner import (
    get_nightly_meta_learner,
    DPOPreferenceCurator,
    NightlyLoRATrainer,
    NightlyReadinessAudit,
    AutonomousModelHotSwapper,
    CHECKPOINT_PATH,
)
import os
import torch

dream_bp = Blueprint("dream", __name__)


@dream_bp.route("/api/dream/telemetry", methods=["GET"])
def api_dream_telemetry():
    """Returns current meta-learning telemetry, checkpoints, and readiness scores."""
    try:
        has_checkpoint = os.path.exists(CHECKPOINT_PATH)
        checkpoint_meta = {}
        if has_checkpoint:
            try:
                ckpt = torch.load(CHECKPOINT_PATH, map_location="cpu")
                checkpoint_meta = {
                    "rank": ckpt.get("rank", 16),
                    "epochs": ckpt.get("epochs", 5),
                    "final_loss": ckpt.get("final_loss"),
                    "samples_trained": ckpt.get("samples_trained"),
                    "device": ckpt.get("device"),
                    "timestamp": ckpt.get("timestamp"),
                }
            except Exception:
                pass

        return jsonify({
            "success": True,
            "has_checkpoint": has_checkpoint,
            "checkpoint_metadata": checkpoint_meta,
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/curate", methods=["POST"])
def api_dream_curate():
    """Triggers DPO preference pair extraction from recent interactions."""
    try:
        res = DPOPreferenceCurator.curate_preference_pairs()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/train_lora", methods=["POST"])
def api_dream_train_lora():
    """Triggers local GPU LoRA optimization loop."""
    try:
        data = request.json or {}
        epochs = int(data.get("epochs", 5))
        lr = float(data.get("lr", 1e-3))
        r = int(data.get("r", 16))

        res = NightlyLoRATrainer.train(epochs=epochs, lr=lr, r=r)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/readiness_audit", methods=["POST"])
def api_dream_readiness_audit():
    """Executes the 5-point enterprise readiness self-benchmarking battery."""
    try:
        res = NightlyReadinessAudit.run_audit()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/hot_swap", methods=["POST"])
def api_dream_hot_swap():
    """Compiles Modelfile and hot-swaps deep-sovereign in Ollama."""
    try:
        res = AutonomousModelHotSwapper.hot_swap_model()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/full_nightly_cycle", methods=["POST"])
def api_dream_full_cycle():
    """Executes all 4 stages of the Autonomous Evolution Loop in sequence."""
    try:
        learner = get_nightly_meta_learner()
        report = learner.run_full_nightly_cycle()
        return jsonify(report)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
