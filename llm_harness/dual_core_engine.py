"""
Dual-Core Agent Harness (Hermes 3 + Qwen 2.5-Coder)
Orchestrates a collaborative runtime:
- Hermes 3: Strategic Executive Planner, Uncensored ReAct, Goal Decomposition, and Tool Arbiter.
- Qwen 2.5-Coder: High-Precision Compiler, Code Synthesis, AST Validator, and JSON Payload Formatter.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
import requests

try:
    import mcp_integration
except ImportError:
    mcp_integration = None

OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")
if not OLLAMA_API.startswith("http://") and not OLLAMA_API.startswith("https://"):
    OLLAMA_API = f"http://{OLLAMA_API}"

PLANNER_MODEL_DEFAULT = "hermes3:8b"
CODER_MODEL_DEFAULT = "qwen2.5-coder:7b"


def get_available_ollama_models() -> List[str]:
    """Retrieve list of locally installed Ollama model tags."""
    try:
        resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=2)
        if resp.status_code == 200:
            return [m.get("name", "") for m in resp.json().get("models", [])]
    except Exception:
        pass
    return []


def resolve_models():
    """Dynamically resolve planner and coder model names with graceful fallbacks."""
    installed = get_available_ollama_models()

    planner = PLANNER_MODEL_DEFAULT
    if not any("hermes3" in m.lower() for m in installed):
        # Fallback to DeepSeek-R1 or Qwen if Hermes is still pulling
        if any("deepseek-r1" in m.lower() for m in installed):
            planner = "deepseek-r1:8b"
        elif any("qwen2.5:7b" in m.lower() for m in installed):
            planner = "qwen2.5:7b"

    coder = CODER_MODEL_DEFAULT
    if not any("qwen2.5-coder" in m.lower() for m in installed):
        if any("qwen2.5" in m.lower() for m in installed):
            coder = "qwen2.5:7b"

    return planner, coder


def get_mcp_tools_schema() -> List[Dict[str, Any]]:
    """Convert MCP tools into an explicit schema."""
    schema = []
    if mcp_integration and hasattr(mcp_integration, "get_all_tool_definitions"):
        for t in mcp_integration.get_all_tool_definitions():
            name = t.get("name", "")
            server = name.split("__")[0] if "__" in name else "native"
            tool = name.split("__", 1)[1] if "__" in name else name
            schema.append({
                "server": server,
                "tool": tool,
                "full_name": name,
                "description": t.get("description", ""),
                "parameters": t.get("inputSchema", {})
            })
    return schema


def call_ollama(model: str, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
    """Execute raw inference against local Ollama runtime."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, timeout=(10, 300))
    if resp.status_code == 200:
        return resp.json().get("message", {}).get("content", "").strip()
    raise RuntimeError(f"Ollama {model} call failed (HTTP {resp.status_code}): {resp.text[:200]}")


def execute_dual_core_harness(prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Main Execution Loop for Dual-Core Harness:
    1. Hermes 3 acts as the Strategic Planner & ReAct Agent.
    2. If code generation, AST parsing, or technical syntax is needed, Hermes delegates to Qwen 2.5-Coder.
    3. If tool calls are generated, they are intercepted, validated, and executed.
    4. Hermes formats the final synthesized response.
    """
    if history is None:
        history = []

    planner_model, coder_model = resolve_models()
    schema = get_mcp_tools_schema()

    # Build tool instructions for the Planner (Hermes)
    tools_prompt = ""
    if schema:
        tools_prompt = f"""
You have access to the following MCP system tools:
{json.dumps(schema, indent=2)}

You can also delegate complex coding, syntax compilation, or script generation to your Co-Pilot Specialist: Qwen 2.5-Coder.

If you choose to execute a tool, output a single JSON block:
```json
{{
    "action": "call_tool",
    "tool": "<tool_name_or_full_name>",
    "args": {{"<arg1>": "<value1>"}}
}}
```

If you need Qwen 2.5-Coder to write, compile, or debug code, output:
```json
{{
    "action": "delegate_code",
    "instruction": "<precise code requirements and constraints>",
    "target_language": "python|c|bash|javascript"
}}
```
"""
    else:
        tools_prompt = "No external MCP tools are currently registered. Perform native reasoning and planning."

    planner_system = f"""You are the Executive Strategic Planner of the D.E.E.P Sovereign AI Cockpit.
Your model identity is {planner_model}. Your partner engine is {coder_model}.
Your role:
- Strategic planning and task decomposition.
- Deciding when to use tools or delegate code synthesis.
- Delivering concise, uninhibited executive guidance.
{tools_prompt}
When ready with the final response, provide your clear, direct answer without extra formatting noise.
"""

    messages = [{"role": "system", "content": planner_system}] + history + [{"role": "user", "content": prompt}]

    # Phase 1: Planner Evaluation (Hermes 3)
    planner_output = call_ollama(planner_model, messages, temperature=0.4)

    # Clean out any thinking scratchpads if present
    cleaned_planner = re.sub(r'<think>.*?(?:</think>|$)', '', planner_output, flags=re.DOTALL).strip()

    execution_trail = []

    # Check for delegation to Qwen 2.5-Coder
    code_match = re.search(r'```json\s*(\{.*?"action":\s*"delegate_code".*?\})\s*```', cleaned_planner, re.DOTALL)
    if code_match:
        try:
            delegation = json.loads(code_match.group(1))
            instruction = delegation.get("instruction", prompt)
            lang = delegation.get("target_language", "python")

            coder_system = f"""You are Qwen 2.5-Coder, the elite Code & AST Engineering Specialist for this Cockpit.
Write clean, performant, production-ready {lang} code adhering strictly to the user's requirements.
Do not provide unnecessary conversational filler—prioritize code correctness, type annotations, and robust error handling.
"""
            coder_messages = [
                {"role": "system", "content": coder_system},
                {"role": "user", "content": f"Task from Hermes Executive:\n{instruction}"}
            ]
            coder_output = call_ollama(coder_model, coder_messages, temperature=0.1)

            execution_trail.append({
                "stage": "code_delegation",
                "engine": coder_model,
                "instruction": instruction,
                "output": coder_output
            })

            # Return hybrid response
            return {
                "planner_model": planner_model,
                "coder_model": coder_model,
                "response": f"{cleaned_planner}\n\n### ⚡ Compiled via {coder_model}:\n{coder_output}",
                "execution_trail": execution_trail,
                "mode": "dual_core_delegation"
            }
        except Exception as e:
            execution_trail.append({"error": f"Code delegation failed: {e}"})

    # Check for Tool Invocation
    tool_match = re.search(r'```json\s*(\{.*?"action":\s*"call_tool".*?\})\s*```', cleaned_planner, re.DOTALL)
    if tool_match and mcp_integration:
        try:
            tool_data = json.loads(tool_match.group(1))
            tool_name = tool_data.get("tool", "")
            args = tool_data.get("args", {})

            # Execute tool through MCP integration
            result = mcp_integration.call_tool(tool_name, args)
            execution_trail.append({
                "stage": "mcp_tool_execution",
                "tool": tool_name,
                "args": args,
                "result": result
            })

            # Synthesis: Give result back to planner for final answer
            synthesis_messages = messages + [
                {"role": "assistant", "content": cleaned_planner},
                {"role": "user", "content": f"[Tool Observation from {tool_name}]:\n{json.dumps(result, indent=2)}\nSynthesize the final executive response."}
            ]
            final_answer = call_ollama(planner_model, synthesis_messages, temperature=0.2)
            final_answer = re.sub(r'<think>.*?(?:</think>|$)', '', final_answer, flags=re.DOTALL).strip()

            return {
                "planner_model": planner_model,
                "coder_model": coder_model,
                "response": final_answer,
                "execution_trail": execution_trail,
                "mode": "dual_core_tool_synthesis"
            }
        except Exception as e:
            execution_trail.append({"error": f"Tool execution error: {e}"})

    # Direct response from planner
    return {
        "planner_model": planner_model,
        "coder_model": coder_model,
        "response": cleaned_planner,
        "execution_trail": execution_trail,
        "mode": "planner_direct"
    }
