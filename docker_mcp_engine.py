"""
Docker MCP Toolkit Integration Engine for D.E.E.P
Seamlessly bridges local Docker MCP servers (Playwright, DuckDuckGo Search, Fetch,
YouTube Transcripts, n8n, etc.) from the 'pappiprait' profile into D.E.E.P's AI runtime.
"""

import os
import json
import subprocess
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DockerMCPEngine")

PROFILE_NAME = "pappiprait"
_TOOLS_CACHE: Optional[List[Dict[str, Any]]] = None
_LAST_CACHE_TIME = 0
CACHE_TTL = 300  # 5 minutes


def is_docker_mcp_available() -> bool:
    """Verifies that docker mcp CLI is functional."""
    try:
        res = subprocess.run(["docker", "mcp", "version"], capture_output=True, text=True, timeout=4)
        return res.returncode == 0
    except Exception:
        return False


def get_profile_servers() -> List[str]:
    """Returns list of active server identifiers in the profile."""
    try:
        res = subprocess.run(["docker", "mcp", "profile", "server", "ls"], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return []
        servers = []
        for line in res.stdout.strip().split("\n"):
            if PROFILE_NAME in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    servers.append(parts[2])
        return servers
    except Exception as e:
        logger.error(f"Error listing profile servers: {e}")
        return []


def get_docker_mcp_tools(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Returns all available MCP tools from the Docker MCP profile."""
    global _TOOLS_CACHE, _LAST_CACHE_TIME
    now = time.time()
    if not force_refresh and _TOOLS_CACHE is not None and (now - _LAST_CACHE_TIME) < CACHE_TTL:
        return _TOOLS_CACHE

    try:
        res = subprocess.run(
            ["docker", "mcp", "tools", "ls", f"--gateway-arg=--profile={PROFILE_NAME}", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if res.returncode == 0 and res.stdout.strip():
            _TOOLS_CACHE = json.loads(res.stdout)
            _LAST_CACHE_TIME = now
            return _TOOLS_CACHE
    except Exception as e:
        logger.error(f"Error loading docker mcp tools: {e}")

    return _TOOLS_CACHE or []


def call_docker_mcp_tool(tool_name: str, arguments: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Executes an MCP tool call via the Docker MCP CLI.
    Example: call_docker_mcp_tool("search", {"query": "deep learning news"})
    """
    t0 = time.time()
    try:
        cmd = ["docker", "mcp", "tools", "call", tool_name, f"--gateway-arg=--profile={PROFILE_NAME}"]
        for k, v in arguments.items():
            if isinstance(v, (dict, list)):
                cmd.append(f"{k}={json.dumps(v)}")
            else:
                cmd.append(f"{k}={v}")

        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = round((time.time() - t0) * 1000, 2)
        
        if res.returncode != 0:
            return {
                "success": False,
                "error": res.stderr.strip() or res.stdout.strip() or "Non-zero exit code",
                "elapsedMs": elapsed
            }

        output = res.stdout.strip()
        # Remove tool execution header if present (e.g., 'Tool call took: 2.02s')
        clean_lines = []
        for line in output.split("\n"):
            if line.startswith("Tool call took:"):
                continue
            clean_lines.append(line)
        clean_output = "\n".join(clean_lines).strip()

        # Attempt to parse json if output is json
        try:
            parsed = json.loads(clean_output)
            return {"success": True, "data": parsed, "raw": clean_output, "elapsedMs": elapsed}
        except Exception:
            return {"success": True, "output": clean_output, "elapsedMs": elapsed}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Tool '{tool_name}' timed out after {timeout}s", "elapsedMs": round((time.time() - t0) * 1000, 2)}
    except Exception as e:
        return {"success": False, "error": str(e), "elapsedMs": round((time.time() - t0) * 1000, 2)}


# -------------------------------------------------------------
# High-Level Conveniences for D.E.E.P
# -------------------------------------------------------------
def docker_web_search(query: str) -> Dict[str, Any]:
    """Runs a web search using Docker's DuckDuckGo MCP tool."""
    return call_docker_mcp_tool("search", {"query": query})


def docker_fetch_url(url: str) -> Dict[str, Any]:
    """Fetches a URL and returns clean markdown via Docker's Fetch MCP tool."""
    return call_docker_mcp_tool("fetch", {"url": url})


def docker_get_youtube_transcript(url: str) -> Dict[str, Any]:
    """Fetches YouTube video transcript via Docker's YouTube Transcript MCP tool."""
    return call_docker_mcp_tool("get_youtube_transcript", {"url": url})


def get_docker_mcp_telemetry() -> Dict[str, Any]:
    """Returns telemetry of the Docker MCP subsystem."""
    avail = is_docker_mcp_available()
    servers = get_profile_servers() if avail else []
    tools = get_docker_mcp_tools() if avail else []
    
    return {
        "available": avail,
        "profile": PROFILE_NAME,
        "serverCount": len(servers),
        "servers": servers,
        "toolCount": len(tools),
        "toolNames": [t.get("name") for t in tools[:20]],
        "hasPlaywright": any("browser" in t.get("name", "") for t in tools),
        "hasSearch": any("search" == t.get("name") for t in tools),
        "hasFetch": any("fetch" == t.get("name") for t in tools),
        "hasN8n": any("workflow" in t.get("name", "") for t in tools)
    }
