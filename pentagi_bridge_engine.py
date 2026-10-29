"""
PentAGI Bridge Engine for D.E.E.P (Dynamic Executive Edge Platform)
Provides autonomous red-team testing, dynamic application security testing (DAST),
Docker stack lifecycle control, and Zero-Trust scope guardrails for PentAGI.
"""

import os
import re
import json
import time
import ipaddress
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("PentAGIBridge")

PENTAGI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pentagi")
COMPOSE_FILE = os.path.join(PENTAGI_DIR, "docker-compose.yml")
PENTAGI_URL = os.getenv("PENTAGI_URL", "http://127.0.0.1:8443")

# Zero-Trust Target Whitelist: Permitted subnets and hostnames for autonomous testing
ALLOWED_HOSTNAMES = {"localhost", "127.0.0.1", "0.0.0.0", "host.docker.internal"}
ALLOWED_PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


def validate_target_scope(target: str) -> Tuple[bool, str]:
    """
    Validates that a pentest target strictly complies with D.E.E.P's Zero-Trust guardrails.
    Autonomous scanning is permitted ONLY on localhost, Docker subnets, and local lab networks.
    """
    if not target or not target.strip():
        return False, "Target address cannot be empty."

    clean_target = target.strip().lower()

    # Strip protocol and path if provided
    clean_target = re.sub(r"^https?://", "", clean_target)
    clean_target = clean_target.split("/")[0]
    host = clean_target.split(":")[0]

    # Check allowed hostnames
    if host in ALLOWED_HOSTNAMES:
        return True, f"Target '{host}' verified within local development scope."

    # Check IP against allowed private networks
    try:
        ip = ipaddress.ip_address(host)
        for net in ALLOWED_PRIVATE_NETWORKS:
            if ip in net:
                return True, f"Target IP '{ip}' verified within authorized private network ({net})."
        return False, (
            f"SECURITY BLOCK: Target '{ip}' is a public IP address. "
            "Autonomous scans on non-local networks are strictly blocked without human authorization."
        )
    except ValueError:
        pass

    # Block arbitrary external domain names
    if "." in host and not host.endswith(".local") and not host.endswith(".internal"):
        return False, (
            f"SECURITY BLOCK: Target domain '{host}' is an external or unverified host. "
            "Autonomous attacks are restricted to local and lab staging environments."
        )

    return True, f"Target '{host}' accepted for local assessment."


def get_pentagi_status() -> Dict[str, Any]:
    """Checks whether Docker is running and inspects PentAGI container states."""
    try:
        # Check docker ps for pentagi containers
        res = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=pentagi", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode != 0:
            return {
                "active": False,
                "docker_running": False,
                "message": "Docker daemon is not currently active.",
                "containers": []
            }

        lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
        containers = []
        is_up = False

        for line in lines:
            parts = line.split("\t")
            name = parts[0]
            status = parts[1] if len(parts) > 1 else ""
            ports = parts[2] if len(parts) > 2 else ""
            running = "Up" in status
            if "pentagi" in name and running:
                is_up = True
            containers.append({"name": name, "status": status, "ports": ports, "running": running})

        return {
            "active": is_up,
            "docker_running": True,
            "message": "PentAGI service stack is operational." if is_up else "PentAGI containers exist but are stopped.",
            "containers": containers,
            "url": PENTAGI_URL
        }
    except Exception as e:
        return {
            "active": False,
            "docker_running": False,
            "message": f"Error inspecting PentAGI stack: {str(e)}",
            "containers": []
        }


def start_pentagi_stack() -> Dict[str, Any]:
    """Spins up the PentAGI Docker Compose stack on demand."""
    if not os.path.exists(COMPOSE_FILE):
        return {"success": False, "error": f"Docker compose file not found at {COMPOSE_FILE}"}

    try:
        res = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "up", "-d"],
            capture_output=True,
            text=True,
            timeout=90
        )
        if res.returncode == 0:
            return {
                "success": True,
                "message": "PentAGI multi-agent stack started successfully.",
                "url": PENTAGI_URL,
                "output": res.stdout.strip()
            }
        return {
            "success": False,
            "error": res.stderr.strip() or res.stdout.strip() or "Failed to start PentAGI compose stack."
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Starting PentAGI timed out. Check Docker Desktop resources."}
    except Exception as e:
        return {"success": False, "error": f"Failed to invoke docker compose: {str(e)}"}


def stop_pentagi_stack() -> Dict[str, Any]:
    """Stops the PentAGI stack to free memory and VRAM."""
    if not os.path.exists(COMPOSE_FILE):
        return {"success": False, "error": "Docker compose file not found."}

    try:
        res = subprocess.run(
            ["docker", "compose", "-f", COMPOSE_FILE, "down"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": res.returncode == 0,
            "message": "PentAGI stack terminated and resources reclaimed.",
            "output": res.stdout.strip() or res.stderr.strip()
        }
    except Exception as e:
        return {"success": False, "error": f"Error stopping PentAGI: {str(e)}"}


def run_preflight_recon(target: str) -> Dict[str, Any]:
    """
    Performs initial safe reconnaissance and service fingerprinting against the target.
    """
    is_valid, msg = validate_target_scope(target)
    if not is_valid:
        return {"success": False, "error": msg}

    clean_target = re.sub(r"^https?://", "", target.strip()).split("/")[0]
    host = clean_target.split(":")[0]
    port = clean_target.split(":")[1] if ":" in clean_target else "5000"

    # Fast socket probe
    import socket
    is_open = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        res = sock.connect_ex((host, int(port)))
        is_open = (res == 0)
        sock.close()
    except Exception:
        is_open = False

    findings = []
    if is_open:
        findings.append({
            "service": "HTTP/TCP",
            "port": port,
            "state": "OPEN",
            "severity": "INFO",
            "description": f"Target host {host} has service responding on port {port}."
        })
    else:
        findings.append({
            "service": "TCP",
            "port": port,
            "state": "CLOSED_OR_FILTERED",
            "severity": "LOW",
            "description": f"No active listener detected on port {port}."
        })

    return {
        "success": True,
        "target": target,
        "host": host,
        "port": port,
        "service_open": is_open,
        "findings": findings,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


def format_executive_voice(status: str, target: str, open_ports: int = 1) -> str:
    """
    Produces executive verbal brevity output under 15 words for J.A.R.V.I.S. / F.R.I.D.A.Y.
    Rule: Crisp, 1-2 natural sentences, no markdown, no URLs.
    """
    operator = os.getenv("OPERATOR_NAME", "Commander")
    if status == "blocked":
        return f"{operator}, security assessment on that target was blocked by zero-trust guardrails."
    elif status == "offline":
        return f"{operator}, PentAGI Docker service is offline. Boot the stack to proceed."
    elif status == "ready":
        return f"{operator}, PentAGI security assessment on {target} initialized successfully."
    else:
        return f"{operator}, security audit complete on {target}. Report logged to cockpit."
