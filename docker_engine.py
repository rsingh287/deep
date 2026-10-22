import os
import json
import subprocess
import time
import tempfile
from typing import Dict, Any, List, Optional

DOCKER_EXE_PATH = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"


def ensure_docker_running():
    try:
        res = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0:
            return True, "Docker daemon is active."

        # Try to launch Docker Desktop
        if os.path.exists(DOCKER_EXE_PATH):
            subprocess.Popen([DOCKER_EXE_PATH])
            return (
                False,
                "Docker Desktop service started in background. Please wait ~10 seconds for daemon to initialize.",
            )
        return (
            False,
            "Docker daemon is not running and Docker Desktop executable was not found.",
        )
    except Exception as e:
        return False, f"Docker check failed: {str(e)}"


def execute_in_sandbox(file_path: str, lang: str):
    ensure_docker_running()
    
    # Map languages to base docker images and run commands
    image_map = {
        "python": ("python:3.11-slim", ["python", "/sandbox/script.py"]),
        "node": ("node:18-alpine", ["node", "/sandbox/script.js"]),
        "javascript": ("node:18-alpine", ["node", "/sandbox/script.js"]),
        "js": ("node:18-alpine", ["node", "/sandbox/script.js"]),
        "typescript": ("node:18-alpine", ["npx", "ts-node", "/sandbox/script.ts"]),
        "ts": ("node:18-alpine", ["npx", "ts-node", "/sandbox/script.ts"]),
        "bash": ("ubuntu:22.04", ["bash", "/sandbox/script.sh"]),
        "sh": ("ubuntu:22.04", ["bash", "/sandbox/script.sh"]),
    }
    
    img_data = image_map.get(lang.lower())
    if not img_data:
        return f"❌ **Docker Error**: Language '{lang}' not supported for ephemeral sandbox execution.", None
        
    image_name, cmd = img_data
    
    # The file on host is copied into the container /sandbox directory
    # Get absolute paths
    host_file = os.path.abspath(file_path)
    
    # We will mount the directory containing the file as /sandbox, and run it.
    # To be safe, maybe just copy the file using docker run -v or via stdin?
    # Actually `-v` is easiest. Let's find the base name.
    file_dir = os.path.dirname(host_file)
    file_name = os.path.basename(host_file)
    
    cmd[-1] = f"/sandbox/{file_name}"
    
    try:
        # Run ephemerally (--rm) with security constraints
        run_args = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
            "--pids-limit", "50",
            "-v", f"{file_dir}:/sandbox",
            "-w", "/sandbox",
            image_name
        ] + cmd
        
        res = subprocess.run(
            run_args,
            capture_output=True,
            text=True,
            timeout=60
        )
        if res.returncode != 0:
            return res.stdout, res.stderr
        return res.stdout, None
    except subprocess.TimeoutExpired:
        return "", "TimeoutExpired: Sandbox execution exceeded 60 seconds."
    except Exception as e:
        return "", f"Sandbox Execution Error: {str(e)}"


def execute_code_snippet_sandbox(code: str, lang: str = "python", timeout: int = 30):
    """
    Executes raw source code directly inside an isolated, ephemeral Docker container.
    Provides memory isolation, no host network access, and prevents escaping.
    """
    t0 = time.time()
    ensure_docker_running()
    
    lang_norm = lang.lower().strip()
    if lang_norm in ("python", "py"):
        img = "python:3.11-slim"
        cmd = ["docker", "run", "--rm", "-i", "--network", "none", "--memory", "512m", "--cpus", "1.0", img, "python", "-"]
    elif lang_norm in ("javascript", "js", "node"):
        img = "node:18-alpine"
        cmd = ["docker", "run", "--rm", "-i", "--network", "none", "--memory", "512m", "--cpus", "1.0", img, "node", "-"]
    elif lang_norm in ("bash", "sh"):
        img = "ubuntu:22.04"
        cmd = ["docker", "run", "--rm", "-i", "--network", "none", "--memory", "512m", "--cpus", "1.0", img, "bash"]
    else:
        return {
            "success": False,
            "error": f"Language '{lang}' is not supported for ephemeral Docker execution.",
            "elapsedMs": 0
        }

    try:
        res = subprocess.run(cmd, input=code, capture_output=True, text=True, timeout=timeout)
        elapsed = round((time.time() - t0) * 1000, 2)
        if res.returncode != 0:
            return {
                "success": False,
                "stdout": res.stdout,
                "stderr": res.stderr.strip() or "Process exited with non-zero status",
                "exitCode": res.returncode,
                "elapsedMs": elapsed
            }
        return {
            "success": True,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exitCode": 0,
            "elapsedMs": elapsed
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Execution timed out after {timeout} seconds.",
            "elapsedMs": round((time.time() - t0) * 1000, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsedMs": round((time.time() - t0) * 1000, 2)
        }


def manage_docker_compose(action: str = "status") -> Dict[str, Any]:
    """Manages D.E.E.P's Redis & Qdrant Docker Compose stack."""
    compose_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker-compose.yml")
    if not os.path.exists(compose_path):
        return {"success": False, "error": "docker-compose.yml not found"}

    try:
        if action == "up":
            res = subprocess.run(
                ["docker", "compose", "-f", compose_path, "up", "-d"],
                capture_output=True, text=True, timeout=60
            )
            return {"success": res.returncode == 0, "output": res.stdout or res.stderr}
        elif action == "down":
            res = subprocess.run(
                ["docker", "compose", "-f", compose_path, "down"],
                capture_output=True, text=True, timeout=30
            )
            return {"success": res.returncode == 0, "output": res.stdout or res.stderr}
        else: # status
            res = subprocess.run(
                ["docker", "compose", "-f", compose_path, "ps", "--format", "json"],
                capture_output=True, text=True, timeout=10
            )
            if res.returncode == 0 and res.stdout.strip():
                try:
                    # In newer docker compose, output might be JSON objects per line
                    lines = res.stdout.strip().split("\n")
                    services = [json.loads(line) for line in lines if line.strip().startswith("{")]
                    return {"success": True, "services": services}
                except Exception:
                    return {"success": True, "raw": res.stdout.strip()}
            return {"success": True, "services": [], "raw": "No active compose services"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_docker_containers():
    try:
        res = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--format",
                "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode != 0:
            status_ok, msg = ensure_docker_running()
            return f"⚠️ **Docker Daemon Status**: {msg}"

        output = res.stdout.strip()
        if not output or len(output.split("\n")) <= 1:
            return "🐳 **Docker Engine Active**: No active or stopped containers found (`docker ps -a` empty)."

        return f"### 🐳 Docker Containers Telemetry (`docker ps -a`)\n```text\n{output}\n```"
    except Exception as e:
        return f"❌ **Docker Error**: {str(e)}"


def get_docker_images():
    try:
        res = subprocess.run(
            [
                "docker",
                "images",
                "--format",
                "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode != 0:
            status_ok, msg = ensure_docker_running()
            return f"⚠️ **Docker Daemon Status**: {msg}"

        output = res.stdout.strip()
        if not output or len(output.split("\n")) <= 1:
            return "🐳 **Docker Engine Active**: No local images found (`docker images` empty)."

        return f"### 📦 Local Docker Images Inventory (`docker images`)\n```text\n{output}\n```"
    except Exception as e:
        return f"❌ **Docker Error**: {str(e)}"


def generate_dockerfile_template(stack="python"):
    stack_low = stack.lower()
    if "node" in stack_low or "react" in stack_low:
        content = """# Production Node.js Dockerfile
FROM node:18-alpine WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]"""
    elif "postgres" in stack_low or "db" in stack_low:
        content = """# Docker Compose PostgreSQL + Redis Stack
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password777
      POSTGRES_DB: local_db
    ports:
      - "5432:5432"
  redis:
    image: redis:alpine
    ports:
      - "6379:6379" """
    else:
        content = """# Production Python FastAPI/Flask Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]"""

    return f"### 🛠️ Generated Production Docker Configuration (`{stack}`)\n```dockerfile\n{content}\n```"


def handle_docker_intent(prompt: str):
    p_low = prompt.lower().strip()

    triggers = [
        "docker",
        "docker ps",
        "docker containers",
        "docker images",
        "docker status",
        "dockerfile",
        "docker compose",
    ]
    if not any(k in p_low for k in triggers):
        return None

    if "docker ps" in p_low or "container" in p_low or "docker status" in p_low:
        return (
            get_docker_containers(),
            "autonomous_docker_engine",
            [
                {
                    "language": "powershell",
                    "code": "docker ps -a",
                    "output": "Fetched Docker Containers Telemetry",
                }
            ],
        )

    if "image" in p_low:
        return (
            get_docker_images(),
            "autonomous_docker_engine",
            [
                {
                    "language": "powershell",
                    "code": "docker images",
                    "output": "Fetched Docker Images Inventory",
                }
            ],
        )

    if "dockerfile" in p_low or "compose" in p_low or "generate docker" in p_low:
        stack = "python"
        if "node" in p_low:
            stack = "node"
        elif "postgres" in p_low or "db" in p_low:
            stack = "postgres"
        return (
            generate_dockerfile_template(stack),
            "autonomous_docker_engine",
            [
                {
                    "language": "dockerfile",
                    "code": f"# Dockerfile for {stack}",
                    "output": "Generated Docker Config",
                }
            ],
        )

    return (
        get_docker_containers(),
        "autonomous_docker_engine",
        [
            {
                "language": "powershell",
                "code": "docker ps -a",
                "output": "Fetched Docker Status",
            }
        ],
    )
