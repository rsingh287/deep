"""
Tool Forge Blueprint v3 for D.E.E.P. Sovereign Cockpit
======================================================
Provides REST API endpoints for:
- Autonomous Python Tool Synthesis via local LLMs
- Sandboxed Test Execution and Reflexion Verification
- Multi-Turn Diagnostic Self-Healing on Test Failures
- Property-Based Fuzz Testing & Invariant Validation (FuzzForgeEngine)
- AST Complexity Profiling & Optimization Scorecards (CodeOptimizerEngine)
- Conditional Multi-Node Workflow DAG Execution (WorkflowDAGRuntime)
- Composite Multi-Tool Pipeline Chaining (ToolChainPipeline)
- Semantic Tool Discovery & Natural Language Auto-Dispatch (SemanticToolIndex)
- Immutable Snapshot Versioning & One-Click Rollback (ToolVersionManager)
- Tool Lifecycle Management (listing, metadata inspection, deletion)
"""

from flask import Blueprint, jsonify, request
from self_synthesizing_tool_forge import (
    get_tool_forge,
    ASTSecurityShield,
    SemanticToolIndex,
    ToolVersionManager,
    ToolChainPipeline,
    FuzzForgeEngine,
    CodeOptimizerEngine,
    WorkflowDAGRuntime,
)

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
            "tools": tools,
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

        if auto_verify:
            t_name = synth_res["tool_name"]
            verify_res = forge.verify_tool(t_name)
            synth_res["verification"] = verify_res

        return jsonify(synth_res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/verify", methods=["POST"])
def api_verify_tool():
    """Runs sandboxed unit tests and Reflexion self-healing loop for a synthesized tool."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        max_healing = int(data.get("max_healing_attempts", 3))
        forge = get_tool_forge()
        res = forge.verify_tool(tool_name, max_healing_attempts=max_healing)
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


@tool_forge_bp.route("/api/forge/fuzz", methods=["POST"])
def api_fuzz_tool():
    """Executes property-based fuzz test battery to prove boundary invariants."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        count = int(data.get("count", 15))
        forge = get_tool_forge()
        res = forge.fuzz_tool(tool_name, count=count)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/analyze", methods=["POST"])
def api_analyze_tool():
    """Inspects AST complexity and returns optimization scorecard."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        forge = get_tool_forge()
        res = forge.analyze_tool(tool_name)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/workflow/execute", methods=["POST"])
def api_execute_workflow():
    """
    Executes a multi-node workflow DAG with conditional branching and dataflow aggregation.
    Payload: {"workflow_name": str, "nodes": [...], "initial_input": Optional[dict]}
    """
    try:
        data = request.json or {}
        workflow_name = data.get("workflow_name", "conditional_workflow")
        nodes = data.get("nodes", [])
        if not nodes:
            return jsonify({"success": False, "error": "Workflow 'nodes' list is required."}), 400

        initial_input = data.get("initial_input", {})
        forge = get_tool_forge()
        res = forge.execute_workflow(workflow_name, nodes, initial_input)
        return jsonify(res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/chain/execute", methods=["POST"])
def api_execute_chain():
    """Executes a composite multi-tool pipeline DAG with parameter interpolation."""
    try:
        data = request.json or {}
        pipeline_name = data.get("pipeline_name", "composite_pipeline")
        steps = data.get("steps", [])
        if not steps:
            return jsonify({"success": False, "error": "Pipeline 'steps' list is required."}), 400

        initial_input = data.get("initial_input", {})
        forge = get_tool_forge()
        res = forge.execute_chain(pipeline_name, steps, initial_input)
        return jsonify(res)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/discover", methods=["POST"])
def api_discover_tools():
    """Semantic search against synthesized tools."""
    try:
        data = request.json or {}
        query = data.get("query", "")
        top_k = int(data.get("top_k", 3))
        results = SemanticToolIndex.discover(query, top_k=top_k)
        return jsonify({
            "success": True,
            "query": query,
            "matches": results,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/auto_dispatch", methods=["POST"])
def api_auto_dispatch():
    """Discovers most relevant tool from query, extracts arguments, and executes."""
    try:
        data = request.json or {}
        query = data.get("query", "")
        if not query:
            return jsonify({"success": False, "error": "Query is required for auto_dispatch."}), 400

        forge = get_tool_forge()
        res = forge.auto_dispatch(query)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/rollback", methods=["POST"])
def api_rollback_tool():
    """Rolls back a synthesized tool to its previous version."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400

        res = ToolVersionManager.rollback(tool_name)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/versions/<tool_name>", methods=["GET"])
def api_list_versions(tool_name):
    """Returns version history of a tool."""
    try:
        versions = ToolVersionManager.list_versions(tool_name)
        return jsonify({
            "success": True,
            "tool_name": tool_name,
            "versions": versions,
        })
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


@tool_forge_bp.route("/api/forge/mutate", methods=["POST"])
def api_mutate_tool():
    """Runs autonomous genetic mutation and Pareto fitness optimization on a tool."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400
        strategies = data.get("strategies")
        forge = get_tool_forge()
        res = forge.mutate_and_optimize_tool(tool_name, strategies=strategies)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/shadow_compare", methods=["POST"])
def api_shadow_compare():
    """Runs differential shadow execution comparing two tool versions for semantic equivalence."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400
        ver_a = data.get("version_a")
        ver_b = data.get("version_b")
        test_inputs = data.get("test_inputs")
        forge = get_tool_forge()
        res = forge.differential_shadow_compare(tool_name, ver_a=ver_a, ver_b=ver_b, test_inputs=test_inputs)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/synthesize_openapi", methods=["POST"])
def api_synthesize_openapi():
    """Autonomously synthesizes a dynamic tool from an OpenAPI/REST endpoint schema."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        endpoint_url = data.get("endpoint_url")
        if not tool_name or not endpoint_url:
            return jsonify({"success": False, "error": "tool_name and endpoint_url are required."}), 400
        description = data.get("description", "Autonomously synthesized API integration tool.")
        http_method = data.get("http_method", "GET")
        parameters = data.get("parameters", [])
        forge = get_tool_forge()
        res = forge.synthesize_from_openapi(tool_name, description, endpoint_url, http_method, parameters)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tool_forge_bp.route("/api/forge/self_heal", methods=["POST"])
def api_self_heal_tool():
    """Triggers emergency self-healing on a failing synthesized tool."""
    try:
        data = request.json or {}
        tool_name = data.get("tool_name")
        failing_input = data.get("failing_input", {})
        error_message = data.get("error_message", "Unknown runtime failure")
        if not tool_name:
            return jsonify({"success": False, "error": "tool_name is required."}), 400
        forge = get_tool_forge()
        res = forge.self_heal_tool(tool_name, failing_input, error_message)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
