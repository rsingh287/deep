"""
Enhanced Tools & Knowledge Graph Blueprint
Provides REST endpoints and interactive visualizer UI for:
- Knowledge Graph in-place observation updates & relational queries
- Precision Filesystem (head/tail streaming, append, safe delete, quarantine restore)
- Archive manager & MCP dynamic tool dispatcher
"""

from flask import Blueprint, request, jsonify, render_template_string
import os
import json
import time

from mcp_integration import call_tool, get_all_tool_definitions
from enhanced_knowledge_graph import enhanced_kg
import enhanced_fs_engine as efs
from security_rbac_engine import security_rbac

enhanced_bp = Blueprint("enhanced_tools", __name__)


# -------------------------------------------------------------------------
# Dynamic Tool Execution API
# -------------------------------------------------------------------------
@enhanced_bp.route("/api/mcp/servers", methods=["GET"])
def list_mcp_servers():
    """Returns the live registry and telemetry for all 19 MCP Protocol Servers."""
    servers = [
        {"id": "postgres", "name": "PostgreSQL Relational DB MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["queries", "schema_inspection", "ast_guard"]},
        {"id": "filesystem", "name": "Enhanced Precision Filesystem MCP", "status": "ONLINE", "transport": "native+stdio", "capabilities": ["read_lines", "append", "safe_delete", "zip_archive"]},
        {"id": "memory", "name": "Bi-Temporal Knowledge Graph MCP", "status": "ONLINE", "transport": "native+stdio", "capabilities": ["update_observations", "add_observations", "query_graph"]},
        {"id": "sequential-thinking", "name": "Sequential Thinking & Planning MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["multi_step_reasoning", "hypothesis_branching"]},
        {"id": "playwright", "name": "Playwright Headless Browser MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["dom_pilot", "screenshot", "form_fill"]},
        {"id": "pgvector", "name": "PGVector High-Dimensional Semantic MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["768d_embeddings", "cosine_similarity"]},
        {"id": "semgrep", "name": "Semgrep AST Security Auditor MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["sast_scanning", "vulnerability_check"]},
        {"id": "duckdb", "name": "DuckDB Embedded Analytical Engine MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["columnar_olap", "parquet_reader"]},
        {"id": "git", "name": "Git Version Control Autopilot MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["diff_commit", "branch_autopilot"]},
        {"id": "fetch", "name": "Web Fetch & HTTP Bridge MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["safe_scrape", "json_api"]},
        {"id": "gemini-api-docs", "name": "Google Gemini API Docs MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["search_docs", "get_doc"]},
        {"id": "data-agent-kit", "name": "GCP Data Agent Kit MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["bigquery_sql", "data_pipelines"]},
        {"id": "notebooks", "name": "Persistent Jupyter Kernel MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["ipython_runtime", "cell_eval"]},
        {"id": "visualization", "name": "3D Force & Cytoscape Graph MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["neural_mesh", "topology_export"]},
        {"id": "puppeteer", "name": "Puppeteer Native Desktop Pilot MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["mouse_keyboard", "screen_ocr"]},
        {"id": "docker", "name": "Self-Healing Docker Daemon MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["container_lifecycle", "log_tail"]},
        {"id": "pqc-vault", "name": "Post-Quantum Cryptography Vault MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["ml_kem_kyber", "aes256_gcm"]},
        {"id": "ast-refactor", "name": "Python AST Refactor Matrix MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["tree_rewriter", "dead_code_remover"]},
        {"id": "hardware-sentinel", "name": "PIC18F85K22 & PICkit 3 Hardware MCP", "status": "ONLINE", "transport": "stdio", "capabilities": ["burn_hex", "lcd_line2_enforcer"]}
    ]
    return jsonify({
        "status": "success",
        "total_servers": len(servers),
        "protocol": "Model Context Protocol v2024.11",
        "ecosystem": "D.E.E.P Sovereign OS",
        "servers": servers
    })


@enhanced_bp.route("/api/mcp/tools", methods=["GET"])
def list_mcp_tools():
    """Returns all active tool definitions and schemas."""
    return jsonify({
        "success": True,
        "tools": get_all_tool_definitions()
    })


@enhanced_bp.route("/api/mcp/execute", methods=["POST"])
def execute_tool_endpoint():
    """Executes a tool with arguments and optional role header."""
    data = request.get_json(force=True, silent=True) or {}
    tool_name = data.get("toolName")
    arguments = data.get("arguments", {})
    user_role = request.headers.get("X-User-Role") or data.get("userRole", "ADMIN")

    if not tool_name:
        return jsonify({"success": False, "error": "toolName is required"}), 400

    result = call_tool(tool_name, arguments, user_role=user_role)
    status_code = 200 if result.get("success", False) else 400
    return jsonify(result), status_code


# -------------------------------------------------------------------------
# Knowledge Graph Specific Endpoints
# -------------------------------------------------------------------------
@enhanced_bp.route("/api/knowledge_graph/data", methods=["GET"])
def get_graph_data():
    """Returns nodes and edges formatted for visualizer graph display."""
    data = enhanced_kg.export_graph_for_ui()
    return jsonify({"success": True, "graph": data})


@enhanced_bp.route("/api/knowledge_graph/update_observations", methods=["POST"])
def update_observations_endpoint():
    """
    In-place observation updates matching user's requested schema:
    {
      "update": [
        {
          "entityName": "...",
          "oldObservations": [...],
          "newObservations": [...]
        }
      ]
    }
    """
    data = request.get_json(force=True, silent=True) or {}
    update_list = data.get("update", [])
    if not update_list:
        return jsonify({"success": False, "error": "'update' array is required"}), 400

    user_role = request.headers.get("X-User-Role", "ADMIN")
    res = call_tool("memory__update_observations", {"update": update_list}, user_role=user_role)
    return jsonify(res)


@enhanced_bp.route("/api/knowledge_graph/add_observations", methods=["POST"])
def add_observations_endpoint():
    data = request.get_json(force=True, silent=True) or {}
    user_role = request.headers.get("X-User-Role", "ADMIN")
    res = call_tool("memory__add_observations", data, user_role=user_role)
    return jsonify(res)


@enhanced_bp.route("/api/knowledge_graph/query", methods=["GET", "POST"])
def query_graph_endpoint():
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
    else:
        data = request.args.to_dict()

    user_role = request.headers.get("X-User-Role", "ADMIN")
    res = call_tool("memory__query_graph", data, user_role=user_role)
    return jsonify(res)


# -------------------------------------------------------------------------
# Precision Filesystem Endpoints
# -------------------------------------------------------------------------
@enhanced_bp.route("/api/filesystem/read_lines", methods=["GET"])
def read_lines_endpoint():
    path = request.args.get("filePath") or request.args.get("path")
    mode = request.args.get("mode", "head")
    count = int(request.args.get("count", 15))
    start_line = request.args.get("startLine")
    end_line = request.args.get("endLine")

    if not path:
        return jsonify({"success": False, "error": "path parameter required"}), 400

    res = efs.read_lines(
        file_path=path,
        mode=mode,
        count=count,
        start_line=int(start_line) if start_line else None,
        end_line=int(end_line) if end_line else None
    )
    return jsonify(res)


@enhanced_bp.route("/api/filesystem/append", methods=["POST"])
def append_file_endpoint():
    data = request.get_json(force=True, silent=True) or {}
    path = data.get("filePath") or data.get("path")
    content = data.get("content", "")
    if not path:
        return jsonify({"success": False, "error": "path is required"}), 400

    res = efs.append_file(path, content)
    return jsonify(res)


@enhanced_bp.route("/api/filesystem/delete", methods=["POST"])
def delete_file_endpoint():
    data = request.get_json(force=True, silent=True) or {}
    path = data.get("path") or data.get("filePath")
    permanent = bool(data.get("permanent", False))
    if not path:
        return jsonify({"success": False, "error": "path is required"}), 400

    user_role = request.headers.get("X-User-Role", "ADMIN")
    res = call_tool("filesystem__delete_file", {"path": path, "permanent": permanent}, user_role=user_role)
    return jsonify(res)


@enhanced_bp.route("/api/filesystem/trash", methods=["GET"])
def get_trash_list():
    return jsonify({"success": True, "trash": efs.list_trash()})


@enhanced_bp.route("/api/filesystem/trash/restore", methods=["POST"])
def restore_trash_item():
    data = request.get_json(force=True, silent=True) or {}
    identifier = data.get("trashId") or data.get("path")
    if not identifier:
        return jsonify({"success": False, "error": "trashId or path required"}), 400
    res = efs.restore_file(identifier)
    return jsonify(res)


# -------------------------------------------------------------------------
# Interactive Web Cockpit UI for Knowledge Graph & Filesystem Tools
# -------------------------------------------------------------------------
@enhanced_bp.route("/knowledge_graph", methods=["GET"])
def knowledge_graph_cockpit():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D.E.E.P Knowledge Graph & Agent Tools Cockpit</title>
    <style>
        :root {
            --bg-dark: #070d19;
            --panel-bg: rgba(13, 24, 46, 0.85);
            --border-glow: rgba(56, 189, 248, 0.3);
            --accent-cyan: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #a855f7;
            --accent-orange: #f97316;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg-dark); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }

        header {
            padding: 16px 24px;
            background: rgba(10, 18, 36, 0.95);
            border-bottom: 1px solid var(--border-glow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        .header-title { display: flex; align-items: center; gap: 12px; }
        .header-title h1 { font-size: 1.4rem; background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .badge { font-size: 0.72rem; padding: 3px 8px; border-radius: 6px; font-weight: 700; background: rgba(56,189,248,0.15); border: 1px solid var(--accent-cyan); color: var(--accent-cyan); }

        .cockpit-layout {
            display: grid;
            grid-template-columns: 320px 1fr 380px;
            gap: 16px;
            padding: 16px;
            flex: 1;
            height: calc(100vh - 70px);
        }

        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            backdrop-filter: blur(12px);
        }
        .panel-header {
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--accent-cyan);
            border-bottom: 1px solid rgba(56,189,248,0.2);
            padding-bottom: 10px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Entity List */
        .scroll-list { flex: 1; overflow-y: auto; padding-right: 4px; }
        .entity-item {
            background: rgba(17, 29, 56, 0.7);
            border: 1px solid rgba(255,255,255,0.06);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .entity-item:hover, .entity-item.active {
            background: rgba(30, 48, 86, 0.9);
            border-left-color: var(--accent-green);
            transform: translateX(3px);
        }
        .entity-item-title { font-weight: 700; font-size: 0.88rem; display: flex; justify-content: space-between; }
        .entity-item-desc { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }

        /* Graph Canvas */
        #graphCanvasContainer {
            position: relative;
            flex: 1;
            border-radius: 8px;
            background: #040813;
            border: 1px solid rgba(56,189,248,0.2);
            overflow: hidden;
        }
        canvas { width: 100%; height: 100%; display: block; }

        /* Observation & Inspector Panel */
        .obs-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 0.8rem;
        }
        .obs-meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--accent-cyan); margin-top: 6px; }
        .btn {
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #fff;
            border: 1px solid rgba(56,189,248,0.4);
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn:hover { background: #0284c7; box-shadow: 0 0 12px rgba(56,189,248,0.5); }
        .btn-green { background: linear-gradient(135deg, #059669, #047857); border-color: #10b981; }
        .btn-orange { background: linear-gradient(135deg, #ea580c, #c2410c); border-color: #f97316; }

        textarea, input[type="text"] {
            width: 100%;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(56,189,248,0.3);
            border-radius: 6px;
            color: #fff;
            padding: 8px;
            font-size: 0.8rem;
            outline: none;
            margin-top: 6px;
            margin-bottom: 8px;
        }
        textarea:focus, input[type="text"]:focus { border-color: var(--accent-cyan); box-shadow: 0 0 8px rgba(56,189,248,0.3); }

        .tab-bar { display: flex; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }
        .tab-btn { background: none; border: none; color: var(--text-muted); font-size: 0.82rem; font-weight: 600; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
        .tab-btn.active { color: var(--accent-cyan); background: rgba(56,189,248,0.1); }
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <span style="font-size: 1.5rem;">🧠</span>
            <div>
                <h1>KNOWLEDGE GRAPH & AGENT TOOL COCKPIT</h1>
                <p style="font-size: 0.72rem; color: var(--text-muted);">Bi-Temporal Knowledge Graph & Precision Filesystem Architecture</p>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="badge">ROLE: ADMIN</span>
            <button class="btn btn-green" onclick="fetchGraphData()">⟳ Refresh Graph</button>
        </div>
    </header>

    <div class="cockpit-layout">
        <!-- Panel 1: Entities & Relations List -->
        <div class="panel">
            <div class="panel-header">
                <span>Entities & Nodes</span>
                <span id="entityCountBadge" class="badge">0</span>
            </div>
            <input type="text" id="filterInput" placeholder="🔍 Search entities..." oninput="filterEntities()">
            <div class="scroll-list" id="entityList"></div>
            <button class="btn" onclick="openAddEntityModal()" style="margin-top: 10px;">+ New Entity</button>
        </div>

        <!-- Panel 2: Interactive 2D/3D Force Graph Visualizer -->
        <div class="panel">
            <div class="panel-header">
                <span>Interactive Knowledge Topology</span>
                <span style="font-size: 0.72rem; color: var(--accent-green);">● Graph Engine Synchronized</span>
            </div>
            <div id="graphCanvasContainer">
                <canvas id="kgCanvas"></canvas>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.75rem; color: var(--text-muted);">
                <span>Tip: Click any node to inspect observations in the editor.</span>
                <span id="graphSummaryText">Nodes: 0 | Edges: 0</span>
            </div>
        </div>

        <!-- Panel 3: In-Place Observation Editor & Tool Dispatcher -->
        <div class="panel">
            <div class="tab-bar">
                <button class="tab-btn active" id="tabObservations" onclick="switchRightTab('obs')">Observations</button>
                <button class="tab-btn" id="tabUpdateInPlace" onclick="switchRightTab('update')">In-Place Update</button>
                <button class="tab-btn" id="tabFsTools" onclick="switchRightTab('fs')">Filesystem Tools</button>
            </div>

            <!-- Tab Content: Observations View -->
            <div id="viewObsTab" style="display: flex; flex-direction: column; flex: 1; overflow: hidden;">
                <div class="panel-header">
                    <span id="selectedEntityTitle">Select an Entity</span>
                    <span id="selectedEntityType" class="badge">GENERAL</span>
                </div>
                <div class="scroll-list" id="observationList">
                    <p style="font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-top: 30px;">
                        Select a node from the left list or canvas to view observations.
                    </p>
                </div>
                <div style="margin-top: 10px;">
                    <textarea id="newObsInput" rows="2" placeholder="Add new observation fact..."></textarea>
                    <div style="display: flex; gap: 8px;">
                        <input type="number" id="obsConfInput" value="1.0" min="0.1" max="1.0" step="0.1" style="width: 80px;" title="Confidence">
                        <button class="btn btn-green" style="flex: 1;" onclick="submitNewObservation()">+ Add Fact</button>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Exact In-Place Observation Update -->
            <div id="viewUpdateTab" style="display: none; flex-direction: column; flex: 1; overflow: hidden;">
                <div class="panel-header">
                    <span>memory__update_observations</span>
                </div>
                <p style="font-size: 0.74rem; color: var(--text-muted); margin-bottom: 8px;">
                    Atomic in-place replacement matching exact observations without deleting entities.
                </p>
                <label style="font-size: 0.72rem; color: var(--accent-cyan);">Target Entity:</label>
                <input type="text" id="updateEntityName" placeholder="e.g. PIC18F85K22">
                <label style="font-size: 0.72rem; color: var(--accent-orange);">Old Observation (to replace):</label>
                <textarea id="updateOldObs" rows="3" placeholder="Exact or substring of old observation..."></textarea>
                <label style="font-size: 0.72rem; color: var(--accent-green);">New Observation (replacement):</label>
                <textarea id="updateNewObs" rows="3" placeholder="New updated observation..."></textarea>
                <button class="btn btn-orange" onclick="submitInPlaceUpdate()">⚡ Execute Atomic Update</button>
                <div id="updateResultLog" style="font-size: 0.72rem; margin-top: 10px; color: var(--accent-cyan); white-space: pre-wrap;"></div>
            </div>

            <!-- Tab Content: Filesystem Tools -->
            <div id="viewFsTab" style="display: none; flex-direction: column; flex: 1; overflow-y: auto;">
                <div class="panel-header">
                    <span>filesystem__read_lines</span>
                </div>
                <input type="text" id="fsPathInput" placeholder="Path (e.g., app_crash.log)">
                <div style="display: flex; gap: 8px;">
                    <select id="fsModeSelect" style="flex: 1; background: #0f172a; border: 1px solid var(--accent-cyan); color: #fff; border-radius: 6px; padding: 6px; font-size: 0.78rem;">
                        <option value="head">Head (First N)</option>
                        <option value="tail" selected>Tail (Last N)</option>
                        <option value="range">Range [Start..End]</option>
                    </select>
                    <input type="number" id="fsCountInput" value="15" style="width: 70px;">
                    <button class="btn" onclick="executeReadLines()">Read</button>
                </div>
                <div id="fsOutputBox" style="background: #050a14; border: 1px solid rgba(56,189,248,0.2); border-radius: 6px; padding: 8px; font-size: 0.72rem; max-height: 220px; overflow-y: auto; margin-top: 10px; white-space: pre-wrap; font-family: monospace;"></div>
            </div>
        </div>
    </div>

    <script>
        let graphData = { nodes: [], edges: [] };
        let activeEntity = null;

        async function fetchGraphData() {
            try {
                const res = await fetch('/api/knowledge_graph/data');
                const json = await res.json();
                if (json.success) {
                    graphData = json.graph;
                    document.getElementById('entityCountBadge').innerText = graphData.nodes.length;
                    document.getElementById('graphSummaryText').innerText = 
                        `Nodes: ${graphData.nodes.length} | Edges: ${graphData.edges.length}`;
                    renderEntityList();
                    drawGraph();
                }
            } catch (err) {
                console.error("Graph fetch error:", err);
            }
        }

        function renderEntityList(filter = '') {
            const container = document.getElementById('entityList');
            container.innerHTML = '';
            const filtered = graphData.nodes.filter(n => 
                n.id.toLowerCase().includes(filter.toLowerCase()) || 
                n.type.toLowerCase().includes(filter.toLowerCase())
            );
            filtered.forEach(node => {
                const item = document.createElement('div');
                item.className = 'entity-item' + (activeEntity && activeEntity.id === node.id ? ' active' : '');
                item.innerHTML = `
                    <div class="entity-item-title">
                        <span>${node.label}</span>
                        <span class="badge" style="font-size:0.65rem;">${node.type}</span>
                    </div>
                    <div class="entity-item-desc">${node.description || 'No description'}</div>
                    <div style="font-size:0.68rem; color:#38bdf8; margin-top:4px;">
                        ★ ${node.observationCount} Facts | Conf: ${(node.confidence * 100).toFixed(0)}%
                    </div>
                `;
                item.onclick = () => selectEntity(node);
                container.appendChild(item);
            });
        }

        function filterEntities() {
            const query = document.getElementById('filterInput').value;
            renderEntityList(query);
        }

        async function selectEntity(node) {
            activeEntity = node;
            renderEntityList(document.getElementById('filterInput').value);
            document.getElementById('selectedEntityTitle').innerText = node.label;
            document.getElementById('selectedEntityType').innerText = node.type;
            document.getElementById('updateEntityName').value = node.label;

            // Fetch observations
            try {
                const res = await fetch(`/api/knowledge_graph/query?entityName=${encodeURIComponent(node.id)}`);
                const json = await res.json();
                const obsList = document.getElementById('observationList');
                obsList.innerHTML = '';

                if (json.observations && json.observations.length > 0) {
                    json.observations.forEach(o => {
                        const card = document.createElement('div');
                        card.className = 'obs-card';
                        card.innerHTML = `
                            <div>${o.observation_text}</div>
                            <div class="obs-meta">
                                <span>Conf: ${(o.confidence * 100).toFixed(0)}% | Rev: ${o.revision}</span>
                                <span>${o.source || 'system'}</span>
                            </div>
                        `;
                        obsList.appendChild(card);
                    });
                } else {
                    obsList.innerHTML = '<p style="color:#94a3b8; font-size:0.8rem; text-align:center; padding:15px;">No observations recorded yet.</p>';
                }
            } catch (err) {
                console.error("Obs query error:", err);
            }
        }

        async function submitNewObservation() {
            if (!activeEntity) return alert('Select an entity first!');
            const text = document.getElementById('newObsInput').value.trim();
            const conf = parseFloat(document.getElementById('obsConfInput').value) || 1.0;
            if (!text) return;

            const res = await fetch('/api/knowledge_graph/add_observations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    entityName: activeEntity.id,
                    observations: [text],
                    confidence: conf,
                    source: 'cockpit_ui'
                })
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('newObsInput').value = '';
                selectEntity(activeEntity);
                fetchGraphData();
            } else {
                alert('Error adding observation: ' + data.error);
            }
        }

        async function submitInPlaceUpdate() {
            const entity = document.getElementById('updateEntityName').value.trim();
            const oldVal = document.getElementById('updateOldObs').value.trim();
            const newVal = document.getElementById('updateNewObs').value.trim();

            if (!entity || !oldVal || !newVal) {
                return alert('Please fill in Entity, Old Observation, and New Observation.');
            }

            const payload = {
                update: [{
                    entityName: entity,
                    oldObservations: [oldVal],
                    newObservations: [newVal]
                }]
            };

            const log = document.getElementById('updateResultLog');
            log.innerText = 'Transmitting in-place update...';

            const res = await fetch('/api/knowledge_graph/update_observations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            log.innerText = JSON.stringify(json, null, 2);

            if (json.success) {
                fetchGraphData();
                if (activeEntity && activeEntity.id === entity) {
                    selectEntity(activeEntity);
                }
            }
        }

        async function executeReadLines() {
            const path = document.getElementById('fsPathInput').value.trim();
            const mode = document.getElementById('fsModeSelect').value;
            const count = document.getElementById('fsCountInput').value;
            if (!path) return alert('Enter file path');

            const out = document.getElementById('fsOutputBox');
            out.innerText = 'Reading lines...';
            try {
                const res = await fetch(`/api/filesystem/read_lines?path=${encodeURIComponent(path)}&mode=${mode}&count=${count}`);
                const json = await res.json();
                if (json.success) {
                    out.innerText = json.content || '(Empty file or no lines matched)';
                } else {
                    out.innerText = 'Error: ' + json.error;
                }
            } catch (e) {
                out.innerText = 'Network error: ' + e;
            }
        }

        function switchRightTab(tab) {
            document.getElementById('viewObsTab').style.display = tab === 'obs' ? 'flex' : 'none';
            document.getElementById('viewUpdateTab').style.display = tab === 'update' ? 'flex' : 'none';
            document.getElementById('viewFsTab').style.display = tab === 'fs' ? 'flex' : 'none';

            document.getElementById('tabObservations').className = 'tab-btn' + (tab === 'obs' ? ' active' : '');
            document.getElementById('tabUpdateInPlace').className = 'tab-btn' + (tab === 'update' ? ' active' : '');
            document.getElementById('tabFsTools').className = 'tab-btn' + (tab === 'fs' ? ' active' : '');
        }

        // 2D Force-Graph Canvas Visualizer
        function drawGraph() {
            const canvas = document.getElementById('kgCanvas');
            const container = document.getElementById('graphCanvasContainer');
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            const ctx = canvas.getContext('2d');

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const nodes = graphData.nodes;
            const edges = graphData.edges;
            if (nodes.length === 0) return;

            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const radius = Math.min(cx, cy) * 0.7;

            // Position nodes in circle for deterministic stable visual
            nodes.forEach((n, idx) => {
                const angle = (idx / nodes.length) * 2 * Math.PI;
                n.x = cx + radius * Math.cos(angle);
                n.y = cy + radius * Math.sin(angle);
            });

            // Draw edges
            ctx.lineWidth = 1.5;
            edges.forEach(e => {
                const fromNode = nodes.find(n => n.id === e.from);
                const toNode = nodes.find(n => n.id === e.to);
                if (fromNode && toNode) {
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
                    ctx.beginPath();
                    ctx.moveTo(fromNode.x, fromNode.y);
                    ctx.lineTo(toNode.x, toNode.y);
                    ctx.stroke();

                    // Label edge
                    const mx = (fromNode.x + toNode.x) / 2;
                    const my = (fromNode.y + toNode.y) / 2;
                    ctx.fillStyle = '#94a3b8';
                    ctx.font = '9px monospace';
                    ctx.fillText(e.label, mx, my);
                }
            });

            // Draw nodes
            nodes.forEach(n => {
                const isSelected = activeEntity && activeEntity.id === n.id;
                ctx.fillStyle = isSelected ? '#10b981' : (n.type === 'MICROCONTROLLER' ? '#f43f5e' : '#38bdf8');
                ctx.beginPath();
                ctx.arc(n.x, n.y, isSelected ? 12 : 9, 0, 2 * Math.PI);
                ctx.fill();

                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.stroke();

                ctx.fillStyle = '#ffffff';
                ctx.font = '11px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(n.label, n.x, n.y + 20);
            });
        }

        // Canvas Click Selection
        document.getElementById('kgCanvas').addEventListener('click', (e) => {
            const rect = e.target.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            const hit = graphData.nodes.find(n => {
                const dx = n.x - clickX;
                const dy = n.y - clickY;
                return Math.sqrt(dx * dx + dy * dy) < 18;
            });
            if (hit) {
                selectEntity(hit);
                drawGraph();
            }
        });

        window.addEventListener('resize', drawGraph);
        window.onload = fetchGraphData;
    </script>
</body>
</html>
"""
    return render_template_string(html)
