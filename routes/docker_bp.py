"""
Docker & Docker MCP Control Blueprint for D.E.E.P
Provides real-time telemetry, Compose stack management, and containerized MCP tool execution.
"""

from flask import Blueprint, jsonify, request
import docker_engine
import docker_mcp_engine

docker_bp = Blueprint("docker_bp", __name__, url_prefix="/api/docker")


@docker_bp.route("/telemetry", methods=["GET"])
def get_docker_telemetry():
    """Returns complete telemetry for Docker Desktop, MCP Toolkit, and Compose services."""
    try:
        daemon_ok, daemon_msg = docker_engine.ensure_docker_running()
        mcp_data = docker_mcp_engine.get_docker_mcp_telemetry()
        compose_status = docker_engine.manage_docker_compose("status")

        return jsonify({
            "success": True,
            "daemon": {
                "active": daemon_ok,
                "message": daemon_msg
            },
            "mcp": mcp_data,
            "compose": compose_status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@docker_bp.route("/mcp/tools", methods=["GET"])
def list_docker_mcp_tools():
    """Returns all 61+ MCP tools from Docker MCP Toolkit."""
    try:
        refresh = request.args.get("refresh", "false").lower() == "true"
        tools = docker_mcp_engine.get_docker_mcp_tools(force_refresh=refresh)
        return jsonify({
            "success": True,
            "count": len(tools),
            "profile": docker_mcp_engine.PROFILE_NAME,
            "tools": tools
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@docker_bp.route("/mcp/call", methods=["POST"])
def call_mcp_tool():
    """Executes a Docker MCP tool call."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})
        timeout = int(data.get("timeout", 30))

        if not tool_name:
            return jsonify({"success": False, "error": "Missing 'tool' parameter"}), 400

        result = docker_mcp_engine.call_docker_mcp_tool(tool_name, arguments, timeout=timeout)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@docker_bp.route("/sandbox/execute", methods=["POST"])
def execute_sandbox_snippet():
    """Runs source code inside an ephemeral, resource-constrained Docker container."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        code = data.get("code", "")
        lang = data.get("lang", "python")
        timeout = int(data.get("timeout", 30))

        if not code.strip():
            return jsonify({"success": False, "error": "Empty code payload"}), 400

        result = docker_engine.execute_code_snippet_sandbox(code, lang=lang, timeout=timeout)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@docker_bp.route("/compose/action", methods=["POST"])
def handle_compose_action():
    """Starts or stops D.E.E.P's Docker Compose stack (Redis, Qdrant, n8n)."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        action = data.get("action", "status")
        if action not in ("up", "down", "status"):
            return jsonify({"success": False, "error": f"Invalid action: {action}"}), 400

        res = docker_engine.manage_docker_compose(action)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
