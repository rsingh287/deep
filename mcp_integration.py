"""
Unified MCP (Model Context Protocol) & Enhanced Native Tools Dispatcher
Integrates external MCP servers with high-performance native engines:
- enhanced_fs_engine (read_lines, append, delete, zip, parallel read)
- enhanced_knowledge_graph (update_observations, add_observations, query_graph)
- security_rbac_engine (RBAC gatekeeper, secret encryption, AST audit)
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional

try:
    import asyncio
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

import enhanced_fs_engine as efs
from enhanced_knowledge_graph import enhanced_kg
from security_rbac_engine import security_rbac
import docker_mcp_engine
import docker_engine

MCP_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_config.json")
ACTIVE_MCP_CLIENTS = {}
EXTERNAL_MCP_TOOLS_CACHE = {}

# -------------------------------------------------------------
# Tool Schemas for Enhanced Native Engine (Matching MCP format)
# -------------------------------------------------------------
ENHANCED_TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "memory__update_observations",
        "description": "Update existing observations in the knowledge graph in-place without deleting entities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "update": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entityName": {
                                "type": "string",
                                "description": "The name of the entity containing the observations."
                            },
                            "oldObservations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of observations to update."
                            },
                            "newObservations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of new observations to replace the old ones."
                            }
                        },
                        "required": ["entityName", "oldObservations", "newObservations"]
                    }
                }
            },
            "required": ["update"]
        }
    },
    {
        "name": "memory__add_observations",
        "description": "Add new observations to an entity with detailed metadata (timestamps, confidence score, source).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entityName": {"type": "string", "description": "Target entity name"},
                "observations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of observation facts"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 1.0,
                    "description": "Confidence score for observation accuracy"
                },
                "source": {
                    "type": "string",
                    "default": "agent",
                    "description": "Origin of the observation (e.g., user, telemetry, code_review)"
                }
            },
            "required": ["entityName", "observations"]
        }
    },
    {
        "name": "memory__query_graph",
        "description": "Query the knowledge graph based on specific relation types, entity types, keywords, or confidence levels.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entityName": {"type": "string", "description": "Filter by entity name substring"},
                "entityType": {"type": "string", "description": "Filter by entity type (e.g., MICROCONTROLLER, SENSOR, SOFTWARE)"},
                "relationType": {"type": "string", "description": "Filter by relation type (e.g., PROGRAMS, RELATES_TO)"},
                "minConfidence": {"type": "number", "default": 0.0, "description": "Minimum confidence threshold"},
                "searchText": {"type": "string", "description": "Search keyword in observation text"},
                "decryptSensitive": {"type": "boolean", "default": False, "description": "Decrypt sensitive observations if authorized"}
            }
        }
    },
    {
        "name": "filesystem__read_lines",
        "description": "Read the first N lines (head), last N lines (tail), or a specific line range from a file without loading the whole file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filePath": {"type": "string", "description": "Absolute or relative path to file"},
                "mode": {"type": "string", "enum": ["head", "tail", "range"], "default": "head"},
                "count": {"type": "integer", "default": 10, "description": "Number of lines to read"},
                "startLine": {"type": "integer", "description": "Start line (1-indexed) for range mode"},
                "endLine": {"type": "integer", "description": "End line (1-indexed) for range mode"}
            },
            "required": ["filePath"]
        }
    },
    {
        "name": "filesystem__append_file",
        "description": "Append text content to a file atomically without overwriting it.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filePath": {"type": "string", "description": "Target file path"},
                "content": {"type": "string", "description": "Text content to append"},
                "ensureNewline": {"type": "boolean", "default": True, "description": "Ensure content ends with a newline"}
            },
            "required": ["filePath", "content"]
        }
    },
    {
        "name": "filesystem__delete_file",
        "description": "Delete a file from the file system. Moves to quarantine (.trash) by default for safety.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file to delete."},
                "permanent": {"type": "boolean", "default": False, "description": "Set to true to bypass quarantine (requires ADMIN role)."}
            },
            "required": ["path"]
        }
    },
    {
        "name": "filesystem__read_multiple_files",
        "description": "Efficiently read multiple files in parallel with LRU/mtime caching and timing telemetry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths to read concurrently"
                },
                "maxSizeBytes": {"type": "integer", "default": 5242880, "description": "Maximum size per file"}
            },
            "required": ["paths"]
        }
    },
    {
        "name": "filesystem__create_symlink",
        "description": "Create a symbolic link or directory junction linking target path to link path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "targetPath": {"type": "string", "description": "Path to the existing target file or folder"},
                "linkPath": {"type": "string", "description": "Path of the new symlink to create"},
                "isDirectory": {"type": "boolean", "description": "True if linking directories"}
            },
            "required": ["targetPath", "linkPath"]
        }
    },
    {
        "name": "archive__compress_files",
        "description": "Compress multiple files or directories into a .zip or .tar.gz archive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sourcePaths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file or folder paths to compress"
                },
                "outputArchivePath": {"type": "string", "description": "Destination archive path (.zip or .tar.gz)"},
                "format": {"type": "string", "enum": ["zip", "tar.gz"], "default": "zip"}
            },
            "required": ["sourcePaths", "outputArchivePath"]
        }
    },
    {
        "name": "archive__decompress_file",
        "description": "Decompress an archive with strict Zip-Slip path traversal security checks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "archivePath": {"type": "string", "description": "Path to the .zip or .tar.gz archive"},
                "extractToDir": {"type": "string", "description": "Destination directory for extracted contents"}
            },
            "required": ["archivePath", "extractToDir"]
        }
    },
    {
        "name": "sandbox__execute_code",
        "description": "Execute Python, Node.js, or Bash code ephemerally inside an isolated, secure Docker container with strict RAM/CPU quotas and no network access.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Raw source code to execute safely"},
                "language": {"type": "string", "enum": ["python", "javascript", "bash"], "default": "python"},
                "timeout": {"type": "integer", "default": 30, "description": "Execution timeout in seconds"}
            },
            "required": ["code"]
        }
    }
]

# -------------------------------------------------------------
# Native Tool Execution Dispatcher
# -------------------------------------------------------------
def execute_native_tool(tool_name: str, args: Dict[str, Any], user_role: str = "ADMIN") -> Dict[str, Any]:
    t0 = time.time()
    try:
        # 1. memory__update_observations
        if tool_name == "memory__update_observations":
            allowed, reason = security_rbac.verify_permission(user_role, "memory:update")
            if not allowed:
                return {"success": False, "error": reason}
            update_list = args.get("update", [])
            res = enhanced_kg.update_observations(update_list)
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 2. memory__add_observations
        elif tool_name == "memory__add_observations":
            allowed, reason = security_rbac.verify_permission(user_role, "memory:write")
            if not allowed:
                return {"success": False, "error": reason}
            ent_name = args.get("entityName", "")
            obs = args.get("observations", [])
            conf = float(args.get("confidence", 1.0))
            src = args.get("source", "agent")
            res = enhanced_kg.add_observations(ent_name, obs, confidence=conf, source=src)
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 3. memory__query_graph
        elif tool_name == "memory__query_graph":
            allowed, reason = security_rbac.verify_permission(user_role, "memory:read")
            if not allowed:
                return {"success": False, "error": reason}
            res = enhanced_kg.query_graph(
                entity_name=args.get("entityName"),
                entity_type=args.get("entityType"),
                relation_type=args.get("relationType"),
                min_confidence=float(args.get("minConfidence", 0.0)),
                search_text=args.get("searchText"),
                decrypt_sensitive=bool(args.get("decryptSensitive", False)),
                user_role=user_role
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 4. filesystem__read_lines
        elif tool_name == "filesystem__read_lines":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:read_lines")
            if not allowed:
                return {"success": False, "error": reason}
            res = efs.read_lines(
                file_path=args.get("filePath") or args.get("path"),
                mode=args.get("mode", "head"),
                count=int(args.get("count", 10)),
                start_line=args.get("startLine"),
                end_line=args.get("endLine")
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 5. filesystem__append_file
        elif tool_name == "filesystem__append_file":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:append")
            if not allowed:
                return {"success": False, "error": reason}
            res = efs.append_file(
                file_path=args.get("filePath") or args.get("path"),
                content=args.get("content", ""),
                ensure_newline=bool(args.get("ensureNewline", True))
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 6. filesystem__delete_file
        elif tool_name == "filesystem__delete_file":
            permanent = bool(args.get("permanent", False))
            perm_needed = "filesystem:delete_permanent" if permanent else "filesystem:delete_quarantine"
            allowed, reason = security_rbac.verify_permission(user_role, perm_needed)
            if not allowed:
                return {"success": False, "error": reason, "filePath": args.get("path")}
            res = efs.delete_file(
                path=args.get("path") or args.get("filePath"),
                permanent=permanent,
                quarantine=not permanent
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 7. filesystem__read_multiple_files
        elif tool_name == "filesystem__read_multiple_files":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:read")
            if not allowed:
                return {"success": False, "error": reason}
            paths = args.get("paths", [])
            max_sz = int(args.get("maxSizeBytes", 5 * 1024 * 1024))
            res = efs.read_multiple_files_fast(paths, max_size_bytes=max_sz)
            return res

        # 8. filesystem__create_symlink
        elif tool_name == "filesystem__create_symlink":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:symlink")
            if not allowed:
                return {"success": False, "error": reason}
            res = efs.create_symlink(
                target_path=args.get("targetPath"),
                link_path=args.get("linkPath"),
                is_directory=args.get("isDirectory")
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 9. archive__compress_files
        elif tool_name == "archive__compress_files":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:archive")
            if not allowed:
                return {"success": False, "error": reason}
            res = efs.compress_files(
                source_paths=args.get("sourcePaths", []),
                output_archive_path=args.get("outputArchivePath"),
                format=args.get("format", "zip")
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 10. archive__decompress_file
        elif tool_name == "archive__decompress_file":
            allowed, reason = security_rbac.verify_permission(user_role, "filesystem:archive")
            if not allowed:
                return {"success": False, "error": reason}
            res = efs.decompress_file(
                archive_path=args.get("archivePath"),
                extract_to_dir=args.get("extractToDir")
            )
            res["elapsedMs"] = round((time.time() - t0) * 1000, 2)
            return res

        # 11. sandbox__execute_code (Docker Ephemeral Execution)
        elif tool_name == "sandbox__execute_code":
            allowed, reason = security_rbac.verify_permission(user_role, "sandbox:execute")
            if not allowed:
                return {"success": False, "error": reason}
            code = args.get("code", "")
            lang = args.get("language", "python")
            timeout = int(args.get("timeout", 30))
            return docker_engine.execute_code_snippet_sandbox(code, lang=lang, timeout=timeout)

        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

    except Exception as ex:
        return {"success": False, "error": str(ex), "elapsedMs": round((time.time() - t0) * 1000, 2)}


# -------------------------------------------------------------
# External MCP Client Support
# -------------------------------------------------------------
def load_mcp_config() -> Dict[str, Any]:
    if not os.path.exists(MCP_CONFIG_FILE):
        return {"mcpServers": {}}
    try:
        with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mcpServers": {}}


async def _connect_and_get_external_tools(name: str, config: Dict):
    if not HAS_MCP:
        return
    try:
        server_params = StdioServerParameters(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env")
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                EXTERNAL_MCP_TOOLS_CACHE[name] = [
                    {"name": f"{name}__{t.name}", "description": t.description, "inputSchema": t.inputSchema}
                    for t in tools.tools
                ]
    except Exception as e:
        print(f"[MCP] External connection notice for {name}: {e}")


def init_mcp_clients():
    if not HAS_MCP:
        return
    config = load_mcp_config()
    servers = config.get("mcpServers", {})

    async def _init_all():
        tasks = []
        for name, srv_conf in servers.items():
            tasks.append(_connect_and_get_external_tools(name, srv_conf))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    try:
        asyncio.run(_init_all())
    except Exception:
        pass


# -------------------------------------------------------------
# Unified Public API
# -------------------------------------------------------------
def get_all_tool_definitions() -> List[Dict[str, Any]]:
    """Returns all available tools (Native Enhanced Tools + Docker MCP Tools + External MCP Tools)."""
    tools = list(ENHANCED_TOOL_SCHEMAS)
    for srv_tools in EXTERNAL_MCP_TOOLS_CACHE.values():
        tools.extend(srv_tools)

    # Append Docker MCP tools if available
    try:
        if docker_mcp_engine.is_docker_mcp_available():
            d_tools = docker_mcp_engine.get_docker_mcp_tools()
            for dt in d_tools:
                tools.append({
                    "name": f"docker__{dt.get('name')}",
                    "description": f"[Docker MCP] {dt.get('description', '')}",
                    "inputSchema": dt.get("inputSchema", {})
                })
    except Exception as e:
        print("[MCP] Notice reading Docker MCP tools:", e)

    return tools


def call_tool(tool_name: str, args: Dict[str, Any], user_role: str = "ADMIN") -> Dict[str, Any]:
    """
    Unified caller:
    1. Checks if tool is in native enhanced suite -> executes immediately.
    2. Checks if tool is a Docker MCP tool (prefixed with `docker__`) -> executes via Docker MCP.
    3. Otherwise forwards to external MCP server if prefixed with `server__tool`.
    """
    # Check if native
    native_names = {t["name"] for t in ENHANCED_TOOL_SCHEMAS}
    if tool_name in native_names:
        return execute_native_tool(tool_name, args, user_role=user_role)

    # Check Docker MCP
    if tool_name.startswith("docker__"):
        actual_name = tool_name.replace("docker__", "")
        return docker_mcp_engine.call_docker_mcp_tool(actual_name, args)

    # Check external MCP
    if "__" in tool_name and HAS_MCP:
        server_name, actual_tool = tool_name.split("__", 1)
        config = load_mcp_config().get("mcpServers", {}).get(server_name)
        if config:
            async def _call():
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config.get("args", []),
                    env=config.get("env")
                )
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(actual_tool, arguments=args)
                        return {"success": True, "content": result.content}
            try:
                return asyncio.run(_call())
            except Exception as e:
                return {"success": False, "error": f"Error calling {tool_name}: {e}"}

    return {"success": False, "error": f"Tool '{tool_name}' not found in active registries."}


# Start background external sync if MCP available
if HAS_MCP:
    threading.Thread(target=init_mcp_clients, daemon=True).start()
