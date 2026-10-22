"""
PCB Circuit Design, Simulation & Manufacturing Fabrication Blueprint
Local AI PC Cockpit
"""

import os
from flask import Blueprint, request, jsonify, render_template, send_file
import pcb_engine

pcb_bp = Blueprint("pcb", __name__)

@pcb_bp.route("/pcb")
def pcb_studio_view():
    """Renders the dedicated PCB Studio, Simulation & Fab Package Dashboard."""
    try:
        return render_template("pcb_studio.html")
    except Exception as e:
        return f"Error loading PCB Studio: {e}", 500


@pcb_bp.route("/api/pcb/circuits", methods=["GET"])
def api_pcb_list_circuits():
    """Lists all available standard and custom AI-designed circuit templates."""
    try:
        circuits = pcb_engine.get_available_circuits()
        return jsonify({"status": "success", "circuits": circuits})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@pcb_bp.route("/api/pcb/ai-plan", methods=["POST"])
def api_pcb_ai_plan():
    """Synthesizes a brand new circuit architecture from a natural language plan."""
    try:
        data = request.get_json() or {}
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"status": "error", "message": "Prompt cannot be empty"}), 400

        synthesized = pcb_engine.synthesize_ai_circuit(prompt)
        cid = synthesized.get("id")

        # Run pre-flight checks on the new circuit
        components, nets, resolved_name = pcb_engine.build_circuit_template(cid)
        sim = pcb_engine.CircuitSimulator(components, nets)
        report = sim.run_preflight_checks(v_in=5.0)

        return jsonify({
            "status": "success",
            "circuit": synthesized,
            "project_name": resolved_name,
            "report": report
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@pcb_bp.route("/api/pcb/simulate", methods=["POST"])
def api_pcb_simulate():
    """Runs SPICE-grade pre-flight simulation and thermal smoke test."""
    try:
        data = request.get_json() or {}
        template_type = data.get("template_type", "ldo_power")
        v_in = float(data.get("v_in", 5.0))

        components, nets, resolved_name = pcb_engine.build_circuit_template(template_type)
        sim = pcb_engine.CircuitSimulator(components, nets)
        report = sim.run_preflight_checks(v_in=v_in)

        return jsonify({
            "status": "success",
            "project_name": resolved_name,
            "report": report
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@pcb_bp.route("/api/pcb/generate", methods=["POST"])
def api_pcb_generate():
    """Runs full pipeline: simulation + layout + Gerber/Drill/BOM/CPL generation + ZIP bundling."""
    try:
        data = request.get_json() or {}
        project_name = data.get("project_name", "")
        template_type = data.get("template_type", "ldo_power")
        v_in = float(data.get("v_in", 5.0))

        result = pcb_engine.run_complete_pcb_pipeline(project_name, template_type, v_in=v_in)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@pcb_bp.route("/api/pcb/download/<project_name>", methods=["GET"])
def api_pcb_download_zip(project_name: str):
    """Downloads the manufacturing ZIP package ready for JLCPCB / PCBWay."""
    try:
        clean_name = pcb_engine.re.sub(r"[^a-zA-Z0-9_\-]", "_", project_name)
        zip_path = os.path.join(
            pcb_engine.OUTPUT_BASE_DIR,
            clean_name,
            f"Gerber_{clean_name}_Fabrication_Package.zip"
        )
        if not os.path.exists(zip_path):
            # Run generation if not already built
            pcb_engine.run_complete_pcb_pipeline(clean_name, "ldo_power")

        if os.path.exists(zip_path):
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f"Gerber_{clean_name}_Fabrication_Package.zip",
                mimetype="application/zip"
            )
        return jsonify({"status": "error", "message": "Fabrication ZIP not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
