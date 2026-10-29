from .base_intent import BaseIntent
import os
import json

class CodeScannerIntent(BaseIntent):
    SCAN_TRIGGERS = [
        "scan my code", "find dead code", "find bugs",
        "go through all coding and find bugs", "code audit", "scan code",
        "check bugs", "check problems", "bugs and problems",
        "check bugs and problems", "find problems", "check for bugs",
        "check code", "check codebase", "bug check",
    ]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return any(t in norm_prompt for t in cls.SCAN_TRIGGERS)

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            import code_scanner_engine

            scan_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            results_json = code_scanner_engine.run_code_scan(scan_dir)
            results = json.loads(results_json)

            report = "🔍 **D.E.E.P Sovereign Codebase Inspection Report:**\n\n"

            if results.get("infer_ast_analysis"):
                report += f"🔬 **Infer-Style AST Analysis ({len(results['infer_ast_analysis'])} findings):**\n"
                for item in results["infer_ast_analysis"][:5]:
                    report += f"- `{item}`\n"
                if len(results["infer_ast_analysis"]) > 5:
                    report += f"- *...and {len(results['infer_ast_analysis'])-5} more.*\n"
                report += "\n"

            if results.get("embedded_firmware_analysis"):
                report += f"⚡ **Embedded MCU Firmware Analysis ({len(results['embedded_firmware_analysis'])} findings):**\n"
                for item in results["embedded_firmware_analysis"][:5]:
                    report += f"- `{item}`\n"
                report += "\n"

            if results.get("bugs"):
                report += f"**Flake8 & Logic Issues ({len(results['bugs'])}):**\n"
                for bug in results["bugs"][:8]:
                    report += f"- `{bug}`\n"
                if len(results["bugs"]) > 8:
                    report += f"- *...and {len(results['bugs'])-8} more.*\n"
            else:
                report += "**Bugs & Logic Issues:** None detected!\n"

            report += "\n"

            if results.get("dead_code"):
                report += f"**Dead Code Found ({len(results['dead_code'])}):**\n"
                for dc in results["dead_code"][:5]:
                    report += f"- `{dc}`\n"
                if len(results["dead_code"]) > 5:
                    report += f"- *...and {len(results['dead_code'])-5} more.*\n"
            else:
                report += "**Dead Code:** None detected!\n"

            if results.get("errors"):
                report += "\n**Scan Errors:**\n"
                for err in results["errors"]:
                    report += f"- {err}\n"

            return (
                report,
                "code_scanner_engine",
                [
                    {
                        "language": "python",
                        "code": "code_scanner_engine.run_code_scan()",
                        "output": "Code scanned successfully.",
                    }
                ],
            )
        except Exception as e:
            return (f"❌ **Code Scanner Error:** {e}", "code_scanner_engine", [])
