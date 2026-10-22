import os
import json
import requests
import re
import mcp_integration

OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def get_deepseek_tools_schema():
    """Convert MCP tools into a schema string for DeepSeek."""
    schema = []
    # If mcp_integration has loaded tools, format them
    if hasattr(mcp_integration, "MCP_TOOLS_CACHE"):
        for server, tools in mcp_integration.MCP_TOOLS_CACHE.items():
            for t in tools:
                schema.append({
                    "server": server,
                    "tool": t.get("name"),
                    "description": t.get("description")
                })
    return schema

def execute_deepseek_harness(prompt, history=None):
    """
    Main entry point for DeepSeek Harness.
    This intercepts the prompt, evaluates available MCP tools,
    and runs a tool-augmented reasoning loop.
    """
    if history is None:
        history = []
        
    schema = get_deepseek_tools_schema()
    
    tools_prompt = ""
    if schema:
        tools_prompt = f"""
You have access to the following MCP tools:
{json.dumps(schema, indent=2)}

If you decide to use a tool to fulfill the user's request, you MUST output a JSON block exactly like this (and nothing else after your thought process):
```json
{{
    "action": "call_tool",
    "server": "<server_name>",
    "tool": "<tool_name>",
    "args": {{"<arg1>": "<value1>"}}
}}
```
"""
    else:
        tools_prompt = "No MCP tools are currently available. Perform the reasoning natively."

    system_prompt = f"""You are DeepSeek-R1, the core analytical reasoning engine for this AI Cockpit.
Your goal is to reason step-by-step to fulfill the user's request.
{tools_prompt}
If you do NOT want to use a tool, or after you have sufficient information, just respond with your final answer.
"""
    
    payload = {
        "model": "deepseek-r1:8b",
        "messages": [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    
    try:
        resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, timeout=(10, 300))
        if resp.status_code == 200:
            content = resp.json().get("message", {}).get("content", "")
            
            # Extract and remove <think> blocks
            think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
            if think_match:
                # Optionally, you can log or preserve the thought process somewhere else
                pass
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            
            # Simple extractor for the JSON tool call
            match = re.search(r'```json\s*(\{.*?"action":\s*"call_tool".*?\})\s*```', content, re.DOTALL)
            if match:
                try:
                    tool_call = json.loads(match.group(1))
                    server = tool_call.get("server")
                    tool = tool_call.get("tool")
                    args = tool_call.get("args", {})
                    
                    # Execute tool synchronously
                    result = mcp_integration.call_mcp_tool(server, tool, args)
                    
                    # Optional: feed the result back to the model for a final synthesis pass
                    # For now, we return the reasoning + tool output to the UI
                    return f"{content}\n\n**Tool Executed: {server}/{tool}**\nOutput:\n```\n{result}\n```"
                except Exception as e:
                    return f"{content}\n\n**Tool Execution Failed:** {e}"
                    
            return content
        else:
            return f"DeepSeek Engine Error: HTTP {resp.status_code}\n{resp.text}"
    except Exception as e:
        return f"Error connecting to DeepSeek Engine: {e}"
