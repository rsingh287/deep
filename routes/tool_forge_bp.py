"""
Tool Forge Blueprint for D.E.E.P. Sovereign Cockpit
===================================================
Provides REST API endpoints for:
- Autonomous Python Tool Synthesis via local LLMs
- Sandboxed Test Execution and Verification
- Autonomous Self-Healing on Test Failures
- Dynamic Tool Execution & Parameter Passing
- Tool Lifecycle Management (listing, metadata inspection, deletion)
"""

from flask import Blueprint, jsonify, request
from self_synthesizing_tool_forge import get_tool_forge, ASTSecurityShield

tool_forge_bp = Blueprint("tool_forge", __name__)


@tool_forge_bp.route("/api/forge/tools", methods=["GET"])
def api_list_synthesized_tools():
    """Lists all dynamically synthesized tools from manifest."""
    try:
        forge = get_tool_forge()
        tools = forge.list_synthesized_tools()
        return jsonify({
            "success": True,
            "total_tools": len(tools),
            "tools": tools
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/synthesize", methods=["POST"])
def api_synthesize_tool():
    """
    Synthesizes a new tool from natural language specification.
    Payload: {"prompt": str, "tool_name": Optional[str], "auto_verify": Optional[bool], "model": Optional[str]}
    """
    try:
        data = request.json or {}
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"success": False, "error": "Prompt specification is required."}), 400

        tool_name = data.get("tool_name")
        model = data.get("model")
        auto_verify = data.get("auto_verify", True)

        forge = get_tool_forge()
        synth_res = forge.synthesize_tool(prompt=prompt, tool_name=tool_name, model=model)

        if not synth_res.get("success"):
            return jsonify(synth_res), 422

        # Auto-verify via sandbox runner if requested
        if auto_verify:
            t_name = synth_res["tool_name"]
            verify_res = forge.verify_tool(t_name)
            synth_res["verification"] = verify_res

        return jsonify(synth_res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/verify", methods=["POST"])
def api_verify_tool():
    """Runs sandboxed unit tests and self-healing loop for a synthesized tool."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        forge = get_tool_forge()
        res = forge.verify_tool(tool_name)
        return jsonify(res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/execute", methods=["POST"])
def api_execute_tool():
    """Executes a synthesized tool with supplied arguments."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        arguments = data.get("arguments", {})
        forge = get_tool_forge()
        res = forge.execute_tool(tool_name, arguments)
        return jsonify(res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/tools/<tool_name>", methods=["DELETE"])
def api_delete_tool(tool_name):
    """Deletes a synthesized tool and unregisters it."""
    try:
        forge = get_tool_forge()
        success = forge.delete_tool(tool_name)
        return jsonify({"success": success, "tool_name": tool_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
