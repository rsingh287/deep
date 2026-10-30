"""
Dynamic Tool Forge Intent v2 for D.E.E.P. Sovereign Cockpit
===========================================================
Routes natural language commands to the Self-Synthesizing Tool Forge:
- "synthesize tool <spec>" / "create tool <name> to <spec>"
- "run tool <name> with <args>" / "execute tool <name>"
- "execute chain <spec>" / "run pipeline <spec>"
- "rollback tool <name>"
- "discover tool <query>" / "find tool <query>"
- "list synthesized tools" / "show tools"
"""

import json
import re
from typing import Any, Dict, List, Tuple

from self_synthesizing_tool_forge import get_tool_forge, SemanticToolIndex, ToolVersionManager
from .base_intent import BaseIntent


class DynamicToolIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        p = norm_prompt.strip().lower()
        patterns = [
            r"^(?:please\s+)?(?:synthesize|forge|create|build|generate)\s+tool\s+",
            r"^(?:please\s+)?(?:run|execute)\s+tool\s+",
            r"^(?:please\s+)?(?:run|execute)\s+(?:chain|pipeline)\s+",
            r"^(?:please\s+)?(?:rollback|revert)\s+tool\s+",
            r"^(?:please\s+)?(?:discover|find|search)\s+tool\s+",
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

            table_rows = ["| Tool ID | Name | Version | Verification Status | Tests Passed | Executions |", "| :--- | :--- | :---: | :--- | :---: | :---: |"]
            for t in tools:
                ver = t.get("current_version", 1)
                table_rows.append(f"| `{t['id']}` | **{t['name']}** | v{ver} | {t.get('verification_status', 'UNKNOWN')} | {t.get('test_pass_count', 0)} | {t.get('execution_count', 0)} |")

            msg = "🛠️ **Tool Forge Registry:**\n\n" + "\n".join(table_rows)
            return (msg, "qwen2.5-coder:7b", [{"language": "json", "code": "tool_forge.list_tools()", "output": json.dumps(tools, indent=2)}])

        # 2. Rollback Tool
        rb_match = re.match(r"^(?:please\s+)?(?:rollback|revert)\s+tool\s+([a-zA-Z0-9_-]+)$", p, re.IGNORECASE)
        if rb_match:
            tool_name = rb_match.group(1).strip()
            rb_res = forge.rollback_tool(tool_name)
            if rb_res.get("success"):
                return (
                    f"⏪ **Tool Forge Rollback:** Tool `{tool_name}` successfully rolled back to **v{rb_res.get('restored_version')}** ({rb_res.get('note')}).",
                    "qwen2.5-coder:7b",
                    [{"language": "json", "code": f"tool_forge.rollback_tool('{tool_name}')", "output": json.dumps(rb_res)}]
                )
            else:
                return (
                    f"❌ **Rollback Error:** {rb_res.get('error')}",
                    "qwen2.5-coder:7b",
                    []
                )

        # 3. Discover / Search Tool
        disc_match = re.match(r"^(?:please\s+)?(?:discover|find|search)\s+tool\s+(.+)$", p, re.IGNORECASE)
        if disc_match:
            query = disc_match.group(1).strip()
            matches = forge.discover_tools(query, top_k=3)
            if not matches:
                return (
                    f"🔍 **Tool Forge Discovery:** No existing synthesized tools matched query: *'{query}'*.",
                    "qwen2.5-coder:7b",
                    []
                )
            lines = [f"🔍 **Semantic Tool Discovery for:** *'{query}'*\n"]
            for m in matches:
                t = m["tool"]
                lines.append(f"- **{t['name']}** (`{t['id']}`) — Confidence: **{int(m['score']*100)}%**\n  {t.get('description', '')}")
            return ("\n".join(lines), "qwen2.5-coder:7b", [{"language": "json", "code": f"tool_forge.discover('{query}')", "output": json.dumps(matches)}])

        # 4. Run / Execute Tool
        run_match = re.match(r"^(?:please\s+)?(?:run|execute)\s+tool\s+([a-zA-Z0-9_-]+)(?:\s+with\s+(.+))?$", p, re.IGNORECASE)
        if run_match:
            tool_name = run_match.group(1).strip()
            raw_args = run_match.group(2)
            arguments = {}
            if raw_args:
                try:
                    arguments = json.loads(raw_args)
                except Exception:
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

        # 5. Synthesize Tool
        spec = re.sub(r"^(?:please\s+)?(?:synthesize|forge|create|build|generate)\s+tool\s+", "", p, flags=re.IGNORECASE).strip()
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
                f"❌ **Tool Synthesis Blocked:** {synth_res.get('error', 'Synthesis failed.')}",
                "qwen2.5-coder:7b",
                []
            )

        t_name = synth_res["tool_name"]
        verify_res = forge.verify_tool(t_name, max_healing_attempts=3)

        if verify_res.get("success"):
            heal_msg = " (🩹 Auto-Repaired via Multi-Turn Reflexion)" if verify_res.get("self_healed") else ""
            msg = (
                f"✅ **Tool Synthesized & Verified Successfully!**{heal_msg}\n\n"
                f"- **Tool Name:** `{t_name}` (v{synth_res.get('version', 1)})\n"
                f"- **Description:** {synth_res.get('description')}\n"
                f"- **Status:** `VERIFIED_OPERATIONAL` ({verify_res.get('latency_ms', 0)}ms)\n"
                f"- **AST Security:** Passed Zero-Trust validation.\n\n"
                f"You can now run this tool anytime: `run tool {t_name} with <arguments>`"
            )
            return (
                msg,
                "qwen2.5-coder:7b",
                [{"language": "python", "code": f"# Synthesized {t_name}.py\n# File: {synth_res.get('tool_file')}", "output": "Tests passed."}]
            )
        else:
            return (
                f"⚠️ **Tool Synthesized but Verification Failed:**\n"
                f"Tool `{t_name}` was created, but failed unit test execution:\n```\n{verify_res.get('error', '')[:400]}\n```",
                "qwen2.5-coder:7b",
                []
            )
