# -*- coding: utf-8 -*-
"""
routes/self_heal_bp.py — D.E.E.P. Sovereign Cognitive OS
========================================================
REST API endpoints for the Autonomous Self-Healing Sentinel & Resilience Subsystem.
"""

from flask import Blueprint, request, jsonify
from autonomous_self_healing_engine import get_self_healing_engine

self_heal_bp = Blueprint("self_heal_bp", __name__)


@self_heal_bp.route("/api/heal/system", methods=["POST"])
def trigger_system_self_heal():
    """Triggers an end-to-end multi-layer autonomous diagnostic and self-healing sweep."""
    try:
        engine = get_self_healing_engine()
        result = engine.run_full_system_heal()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@self_heal_bp.route("/api/heal/tool", methods=["POST"])
def heal_dynamic_tool():
    """Executes a multi-candidate patch tournament to auto-heal a specific failing tool."""
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool_name")
    if not tool_name:
        return jsonify({"success": False, "error": "Missing 'tool_name' in request body."}), 400

    failing_input = data.get("failing_input") or {}
    error_message = data.get("error_message") or "Runtime error triggered by user audit."

    try:
        engine = get_self_healing_engine()
        result = engine.heal_specific_tool(
            tool_name=tool_name,
            failing_input=failing_input,
            error_message=error_message,
        )
        status_code = 200 if result.get("success") else 422
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@self_heal_bp.route("/api/heal/telemetry", methods=["GET"])
def get_healing_telemetry():
    """Fetches real-time telemetry on self-healing incidents, active quarantines, and circuits."""
    try:
        engine = get_self_healing_engine()
        data = engine.get_healing_telemetry()
        return jsonify({"success": True, "telemetry": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@self_heal_bp.route("/api/heal/reset_circuits", methods=["POST"])
def reset_circuits():
    """Canary-probes and resets tripped circuit breakers."""
    data = request.get_json(silent=True) or {}
    force = bool(data.get("force", False))
    try:
        engine = get_self_healing_engine()
        res = engine.reset_tripped_circuits(force=force)
        return jsonify({"success": True, "result": res}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@self_heal_bp.route("/api/heal/quarantine", methods=["POST"])
def quarantine_tool():
    """Isolates a failing dynamic tool from production invocation."""
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool_name")
    reason = data.get("reason", "Manual quarantine triggered via Cockpit HUD")
    if not tool_name:
        return jsonify({"success": False, "error": "Missing 'tool_name'."}), 400

    try:
        engine = get_self_healing_engine()
        ok = engine.quarantine_tool(tool_name, reason=reason)
        return jsonify({"success": ok, "tool_name": tool_name, "status": "QUARANTINED" if ok else "NOT_FOUND"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@self_heal_bp.route("/api/heal/unquarantine", methods=["POST"])
def unquarantine_tool():
    """Re-audits and restores a quarantined tool to active production."""
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool_name")
    if not tool_name:
        return jsonify({"success": False, "error": "Missing 'tool_name'."}), 400

    try:
        engine = get_self_healing_engine()
        ok = engine.unquarantine_tool(tool_name)
        return jsonify({"success": ok, "tool_name": tool_name, "status": "ACTIVE" if ok else "NOT_QUARANTINED"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
