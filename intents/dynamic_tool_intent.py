"""
Dynamic Tool Forge Intent for D.E.E.P. Sovereign Cockpit
========================================================
Routes natural language commands to the Self-Synthesizing Tool Forge:
- "synthesize tool <spec>" / "create tool <name> to <spec>"
- "run tool <name> with <args>" / "execute tool <name>"
- "list synthesized tools" / "show tools"
"""

import json
import re
from typing import Any, Dict, List, Tuple
from .base_intent import BaseIntent
from self_synthesizing_tool_forge import get_tool_forge


class DynamicToolIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        p = norm_prompt.strip().lower()
        patterns = [
            r"^(?:please\s+)?(?:synthesize|forge|create|build|generate)\s+tool\s+",
            r"^(?:please\s+)?(?:run|execute)\s+tool\s+",
            r"^(?:please\s+)?(?:list|show|get)\s+(?:synthesized\s+)?tools$",
        ]
        return any(bool(re.match(pat, p)) for pat in patterns)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        forge = get_tool_forge()
        p = norm_prompt.strip()
        low = p.lower()

        # 1. List synthesized tools
        if re.search(r"(?:list|show|get)\s+(?:synthesized\s+)?tools", low):
            tools = forge.list_synthesized_tools()
            if not tools:
                return (
                    "🛠️ **Tool Forge Registry:** No dynamic tools currently synthesized. You can create one anytime with `synthesize tool <description>`.",
                    "qwen2.5-coder:7b",
                    []
                )

            table_rows = ["| Tool ID | Name | Verification Status | Tests Passed | Executions |", "| :--- | :--- | :--- | :---: | :---: |"]
            for t in tools:
                table_rows.append(f"| `{t['id']}` | **{t['name']}** | {t.get('verification_status', 'UNKNOWN')} | {t.get('test_pass_count', 0)} | {t.get('execution_count', 0)} |")

            msg = "🛠️ **Tool Forge Registry:**\n\n" + "\n".join(table_rows)
            return (msg, "qwen2.5-coder:7b", [{"language": "json", "code": "tool_forge.list_tools()", "output": json.dumps(tools, indent=2)}])

        # 2. Run / Execute Tool
        run_match = re.match(r"^(?:please\s+)?(?:run|execute)\s+tool\s+([a-zA-Z0-9_-]+)(?:\s+with\s+(.+))?$", p, re.IGNORECASE)
        if run_match:
            tool_name = run_match.group(1).strip()
            raw_args = run_match.group(2)
            arguments = {}
            if raw_args:
                try:
                    arguments = json.loads(raw_args)
                except Exception:
                    # Parse key=val pairs with automatic type casting
                    pairs = re.findall(r"([a-zA-Z0-9_]+)=([^\s]+)", raw_args)
                    for k, v in pairs:
                        val = v.strip().strip("'\"")
                        if val.lower() == "true":
                            arguments[k] = True
                        elif val.lower() == "false":
                            arguments[k] = False
                        else:
                            try:
                                arguments[k] = float(val) if "." in val else int(val)
                            except ValueError:
                                arguments[k] = val

            res = forge.execute_tool(tool_name, arguments)
            if res.get("success"):
                out_str = str(res.get("result"))
                return (
                    f"⚡ **Tool Forge Execution:** Successfully ran `{tool_name}` in {res.get('execution_time_ms', 0)}ms.\n\n**Output:**\n```json\n{out_str}\n```",
                    "qwen2.5-coder:7b",
                    [{"language": "python", "code": f"tool_forge.execute_tool({repr(tool_name)}, {arguments})", "output": str(res)}]
                )
            else:
                return (
                    f"❌ **Tool Forge Execution Error:** {res.get('error', 'Execution failed.')}",
                    "qwen2.5-coder:7b",
                    [{"language": "python", "code": f"tool_forge.execute_tool({repr(tool_name)}, {arguments})", "output": str(res)}]
                )

        # 3. Synthesize Tool
        spec = re.sub(r"^(?:please\s+)?(?:synthesize|forge|create|build|generate)\s+tool\s+", "", p, flags=re.IGNORECASE).strip()
        # Extract suggested name if provided: "to_uppercase to convert text to upper"
        name_m = re.match(r"^([a-zA-Z0-9_]+)\s+(?:to\s+|that\s+|for\s+)?(.+)$", spec)
        tool_name = None
        if name_m and len(name_m.group(1)) <= 30 and not name_m.group(1).startswith("a"):
            tool_name = name_m.group(1)
            prompt_spec = name_m.group(2)
        else:
            prompt_spec = spec

        synth_res = forge.synthesize_tool(prompt=prompt_spec, tool_name=tool_name)
        if not synth_res.get("success"):
            return (
                f"❌ **Tool Forge Synthesis Failed:** {synth_res.get('error', 'Unknown error')}",
                "qwen2.5-coder:7b",
                []
            )

        t_name = synth_res["tool_name"]
        # Verify immediately
        verify_res = forge.verify_tool(t_name)

        if verify_res.get("success"):
            return (
                f"✅ **Tool Synthesized & Verified:** `{t_name}` is live and registered in Master Skills!\n\n"
                f"- **Description:** {synth_res.get('description')}\n"
                "- **AST Security:** Passed Zero-Trust Guardrails\n"
                f"- **Sandbox Tests:** All unit tests PASSED ({verify_res.get('latency_ms', 0)}ms)\n"
                f"- **Invocation:** Run anytime with `run tool {t_name} with <arguments>`",
                "qwen2.5-coder:7b",
                [{"language": "python", "code": f"tool_forge.verify_tool({repr(t_name)})", "output": str(verify_res)}]
            )
        else:
            return (
                f"⚠️ **Tool Synthesized with Test Warning:** `{t_name}` was generated but unit tests did not pass.\n"
                f"Error: {verify_res.get('error', 'Verification failed')[:200]}",
                "qwen2.5-coder:7b",
                []
            )
