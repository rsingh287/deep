"""
Machine Dreaming & Continuous Meta-Learning Blueprint v3 for D.E.E.P. Cockpit
=============================================================================
Provides REST API endpoints for:
- REM Machine Dreaming memory consolidation
- DPO Preference curation and Synthetic Self-Play Distillation
- Local NVIDIA GPU LoRA training & convergence telemetry (SimPO & DPO + EWC)
- 5-Point Self-Benchmarking Readiness Audit
- Shadow Canary A/B Latency & Quality Benchmark
- Autonomous Model Hot-Swapping into Ollama
- Background Dream Daemon State & Control
"""

import os
from flask import Blueprint, jsonify, request
import torch

from nightly_meta_learner import (
    get_nightly_meta_learner,
    DPOPreferenceCurator,
    SelfPlayDistiller,
    NightlyLoRATrainer,
    NightlyReadinessAudit,
    CanaryHotSwapper,
    AutonomousModelHotSwapper,
    NightlyDreamDaemon,
    CHECKPOINT_PATH,
)

dream_bp = Blueprint("dream", __name__)


@dream_bp.route("/api/dream/telemetry", methods=["GET"])
def api_dream_telemetry():
    """Returns current meta-learning telemetry, checkpoints, EWC metrics, and readiness scores."""
    try:
        has_checkpoint = os.path.exists(CHECKPOINT_PATH)
        checkpoint_meta = {}
        if has_checkpoint:
            try:
                ckpt = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
                checkpoint_meta = {
                    "rank": ckpt.get("rank", 16),
                    "epochs": ckpt.get("epochs", 5),
                    "objective": ckpt.get("objective", "simpo"),
                    "initial_loss": ckpt.get("initial_loss"),
                    "final_loss": ckpt.get("final_loss"),
                    "final_reward_margin": ckpt.get("reward_margin_history", [-1])[-1] if ckpt.get("reward_margin_history") else None,
                    "final_reward_accuracy_pct": ckpt.get("reward_acc_history", [-1])[-1] if ckpt.get("reward_acc_history") else None,
                    "fisher_mass": ckpt.get("fisher_mass"),
                    "samples_trained": ckpt.get("samples_trained"),
                    "device": ckpt.get("device"),
                    "timestamp": ckpt.get("timestamp"),
                }
            except Exception:
                pass

        daemon = NightlyDreamDaemon()
        return jsonify({
            "success": True,
            "has_checkpoint": has_checkpoint,
            "checkpoint_metadata": checkpoint_meta,
            "daemon_status": daemon.get_status(),
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


@dream_bp.route("/api/dream/distill_synthetic", methods=["POST"])
def api_distill_synthetic():
    """Generates synthetic self-play contrastive preference pairs from knowledge graph."""
    try:
        res = SelfPlayDistiller.distill_synthetic_pairs()
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/train_lora", methods=["POST"])
def api_dream_train_lora():
    """Triggers local GPU LoRA optimization loop with SimPO/DPO and EWC."""
    try:
        data = request.json or {}
        epochs = int(data.get("epochs", 5))
        lr = float(data.get("lr", 1e-3))
        r = int(data.get("r", 16))
        beta = float(data.get("beta", 0.1))
        gamma = float(data.get("gamma", 0.5))
        objective = data.get("objective", "simpo")
        ewc_lambda = float(data.get("ewc_lambda", 50.0))

        res = NightlyLoRATrainer.train(
            epochs=epochs,
            lr=lr,
            r=r,
            beta=beta,
            gamma=gamma,
            objective=objective,
            ewc_lambda=ewc_lambda,
        )
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


@dream_bp.route("/api/dream/canary_benchmark", methods=["POST"])
def api_dream_canary_benchmark():
    """Runs shadow canary latency and compliance benchmark on candidate model."""
    try:
        data = request.json or {}
        model = data.get("model", "deep-sovereign:latest")
        res = CanaryHotSwapper.evaluate_canary(model)
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


@dream_bp.route("/api/dream/daemon_status", methods=["GET"])
def api_dream_daemon_status():
    """Returns background dream daemon status and idle vitals."""
    try:
        daemon = NightlyDreamDaemon()
        return jsonify(daemon.get_status())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/daemon/start", methods=["POST"])
def api_dream_daemon_start():
    """Starts the background sleep-cycle dream daemon."""
    try:
        daemon = NightlyDreamDaemon()
        daemon.start()
        return jsonify({"success": True, "status": "STARTED", "daemon": daemon.get_status()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/daemon/stop", methods=["POST"])
def api_dream_daemon_stop():
    """Stops the background sleep-cycle dream daemon."""
    try:
        daemon = NightlyDreamDaemon()
        daemon.stop()
        return jsonify({"success": True, "status": "STOPPED"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@dream_bp.route("/api/dream/full_nightly_cycle", methods=["POST"])
def api_dream_full_cycle():
    """Executes all stages of the Autonomous Evolution Loop in sequence."""
    try:
        data = request.json or {}
        objective = data.get("objective", "simpo")
        learner = get_nightly_meta_learner()
        report = learner.run_full_nightly_cycle(objective=objective)
        return jsonify(report)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
