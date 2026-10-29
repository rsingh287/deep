import json
import subprocess
import traceback

import requests
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Antigravity Skills API")

# Allow the frontend to connect from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SkillRequest(BaseModel):
    skill_name: str
    prompt: str
    model: str = ""


class SkillResponse(BaseModel):
    status: str
    result: str
    data: dict = {}


import os
import ipaddress
import urllib.parse

OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

DEEP_WORKSPACE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "generated_apps", "deep_workspace"
)
os.makedirs(DEEP_WORKSPACE, exist_ok=True)


def is_safe_fetch_url(target_url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(target_url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            pass
        return True
    except Exception:
        return False


def execute_ollama_prompt(model: str, prompt: str, system: str = "") -> str:
    if not model:
        model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

    url = f"{OLLAMA_BASE_URL}/api/chat"

    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes code or text to a file in the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative file path (e.g. 'index.html' or 'css/styles.css')",
                        },
                        "content": {
                            "type": "string",
                            "description": "The complete content to write into the file.",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_directory",
                "description": "Creates a folder in the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "Relative directory path (e.g. 'assets' or 'js')",
                        }
                    },
                    "required": ["dir_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_webpage",
                "description": "Fetches and reads text content from a webpage URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The full URL to read (e.g. 'https://en.wikipedia.org/wiki/Git')",
                        }
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "execute_git_command",
                "description": "Executes a git command inside the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The git command and arguments (e.g. 'clone https://github.com/user/repo.git', 'status', 'log')",
                        }
                    },
                    "required": ["command"],
                },
            },
        },
    ]

    messages = []
    if system:
        messages.append(
            {
                "role": "system",
                "content": system
                + "\nYou have tools to write files and folders to my local hard drive (in the deep_workspace folder), clone git repos, and read websites. Use them if I ask you to write code, create a project, fetch info, or manage git! IMPORTANT: When replying to the user, ALWAYS provide a helpful, detailed response explaining what you did or what you plan to do. NEVER reply with just a single word like 'noted' or 'okay'.",
            }
        )
    else:
        messages.append(
            {
                "role": "system",
                "content": "You are D.E.E.P., an advanced autonomous AI. You have tools to write files, manage git, and fetch websites. IMPORTANT: When replying to the user, ALWAYS provide a detailed, helpful response. NEVER reply with just 'noted' or 'okay'.",
            }
        )

    messages.append({"role": "user", "content": prompt})

    try:
        # Loop for tool calling
        for _ in range(10):
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "tools": tools,
            }

            response = requests.post(url, json=payload, timeout=600)
            if response.status_code != 200:
                return f"Error: {response.text}"

            res_data = response.json()
            message = res_data.get("message", {})
            messages.append(message)

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                return message.get("content", "")

            # Execute tools
            for tc in tool_calls:
                func_name = tc.get("function", {}).get("name")
                args = tc.get("function", {}).get("arguments", {})

                tool_result = ""
                try:
                    if func_name == "write_file":
                        safe_path = os.path.normpath(
                            os.path.join(DEEP_WORKSPACE, args.get("file_path", ""))
                        )
                        if not safe_path.startswith(DEEP_WORKSPACE):
                            tool_result = "Security Error: Path traversal detected."
                        else:
                            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                            with open(safe_path, "w", encoding="utf-8") as f:
                                f.write(args.get("content", ""))
                            tool_result = f"Successfully wrote to {safe_path}"
                    elif func_name == "create_directory":
                        safe_path = os.path.normpath(
                            os.path.join(DEEP_WORKSPACE, args.get("dir_path", ""))
                        )
                        if not safe_path.startswith(DEEP_WORKSPACE):
                            tool_result = "Security Error: Path traversal detected."
                        else:
                            os.makedirs(safe_path, exist_ok=True)
                            tool_result = f"Successfully created directory {safe_path}"
                    elif func_name == "fetch_webpage":
                        url = args.get("url", "")
                        if not is_safe_fetch_url(url):
                            tool_result = "Security Error: Access to private or local loopback networks is blocked."
                        else:
                            try:
                                resp = requests.get(url, timeout=30)
                                resp.raise_for_status()
                                soup = BeautifulSoup(resp.text, "html.parser")
                                for script in soup(["script", "style"]):
                                    script.extract()
                                text = soup.get_text(separator=" ", strip=True)
                                tool_result = text[:10000]  # Limit to 10k chars
                            except Exception as e:
                                tool_result = f"Error fetching webpage: {e}"
                    elif func_name == "execute_git_command":
                        cmd = args.get("command", "")
                        try:
                            import shlex
                            parts = shlex.split(cmd, posix=False) if os.name == "nt" else shlex.split(cmd)
                            if not parts:
                                raise ValueError("Empty git command.")
                            if parts[0].lower() != "git":
                                parts.insert(0, "git")
                            result = subprocess.run(
                                parts,
                                cwd=DEEP_WORKSPACE,
                                capture_output=True,
                                text=True,
                                shell=False,
                                timeout=120,
                            )
                            tool_result = (
                                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                            )
                        except Exception as e:
                            tool_result = f"Git execution failed: {e}"
                    else:
                        tool_result = f"Unknown tool: {func_name}"
                except Exception as ex:
                    tool_result = f"Tool execution failed: {ex}"

                messages.append(
                    {"role": "tool", "content": tool_result, "name": func_name}
                )

        return messages[-1].get("content", "Tool execution loop exceeded.")

    except Exception as e:
        return f"Error: {e}"


def run_web_architect(prompt: str) -> str:
    """Invokes the web architect skill to build a website."""
    # We can import the existing logic or just call the function if it's in the same dir
    try:
        import importlib
        import web_architect_skill
        importlib.reload(web_architect_skill)
        from web_architect_skill import build_premium_website

        # extract a topic or project name from the prompt
        result_str = build_premium_website(project_name="api_gen_site", topic=prompt)
        return result_str
    except Exception as e:
        print(f"Web Architect Error: {traceback.format_exc()}")
        return f"Failed to build website: {e}"


@app.post("/api/execute_skill", response_model=SkillResponse)
async def execute_skill(req: SkillRequest):
    skill = req.skill_name.lower().strip()
    prompt = req.prompt.strip()

    print(f"[Skills API] Received request for skill: '{skill}' with prompt: '{prompt}'")

    if skill in ["web-architect", "web-architect-pro-max", "frontend-design", "tasteskill-anti-slop", "ui-ux-pro-max"]:
        result = run_web_architect(prompt)
        return SkillResponse(status="success", result=result)

    if skill == "file-gen-tools":
        from file_gen_tools_skill import run_file_gen_tools

        result = run_file_gen_tools(prompt)
        return SkillResponse(status="success", result=result)

    if skill == "job-tailor":
        from job_tailor_skill import run_job_tailor

        # Assuming prompt contains URL and resume text separated by a newline
        parts = prompt.split("\n", 1)
        url = parts[0] if len(parts) > 0 else ""
        text = parts[1] if len(parts) > 1 else ""
        result = run_job_tailor(url, text)
        return SkillResponse(status="success", result=result)

    if skill == "doc-parser":
        from document_parser_skill import run_document_parser

        # prompt is the file path
        result = run_document_parser(prompt)
        return SkillResponse(status="success", result=result)

    if skill == "grammar-auditor":
        from grammar_auditor_skill import run_grammar_auditor

        result = run_grammar_auditor(prompt)
        return SkillResponse(status="success", result=result)

    if skill == "code-cleaner":
        from code_cleaner_skill import run_code_cleaner

        result = run_code_cleaner(prompt)
        return SkillResponse(status="success", result=result)

    # Dynamically match against the 840 loaded skills
    try:
        with open("master_skills_registry.json", "r", encoding="utf-8") as f:
            registry = json.load(f)

        # Find skill by ID or exact Name match
        matched_skill = next(
            (
                s
                for s in registry
                if s["id"].lower() == skill or s["name"].lower() == skill
            ),
            None,
        )

        target_model = req.model.strip() if req.model else os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

        if matched_skill:
            print(f"[Skills API] Skill '{matched_skill['name']}' loaded from registry!")
            description = matched_skill.get("description", "")
            system_prompt = f"You are the '{matched_skill['name']}' expert. Your capabilities: {description}\nAddress the user's request using these capabilities."
            result = execute_ollama_prompt(target_model, prompt, system=system_prompt)
            return SkillResponse(
                status="success", result=result, data={"skill_info": matched_skill}
            )

    except Exception as e:
        print(f"[Skills API] Warning: Could not query registry: {e}")

    target_model = req.model.strip() if req.model else os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

    if skill == "general":
        # General chat/assistant fallback
        result = execute_ollama_prompt(target_model, prompt)
        return SkillResponse(status="success", result=result)

    else:
        # Generic fallback for unhandled/unknown skills
        system_prompt = (
            f"You are acting as the {skill} skill. Assist the user with their request."
        )
        result = execute_ollama_prompt(target_model, prompt, system=system_prompt)
        return SkillResponse(status="success", result=result)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("Starting Antigravity Skills API on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
