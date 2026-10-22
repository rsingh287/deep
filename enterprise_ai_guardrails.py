"""
Enterprise AI Guardrails & Arbitration System Module
Includes LLM Output Arbitration, Hallucination Detection, and Text-to-SQL Security Guardrails.
"""

import re


class EnterpriseAIGuardrails:
    def __init__(self):
        self.blocked_sql_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "TRUNCATE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
        ]
        self.restricted_tables = [
            "users",
            "user_credentials",
            "passwords",
            "security_keys",
            "secret_tokens",
        ]
        self.arbitration_history = []

    def validate_text_to_sql(self, sql_query: str) -> dict:
        """
        Validates Text-to-SQL queries using AST-style rules:
        - Blocks destructive DDL/DML keywords (DROP, DELETE, UPDATE, etc.)
        - Restricts access to sensitive system/credential tables
        - Enforces mandatory LIMIT clause (default 100)
        - Detects SQL injection attempts
        """
        query_upper = sql_query.upper().strip()

        # 1. Reject multi-statement queries
        if ";" in query_upper[:-1]:
            return {
                "valid": False,
                "reason": "SECURITY_VIOLATION: Multiple SQL statements are forbidden.",
                "sanitized_query": None,
            }

        # 2. Reject destructive statements
        for keyword in self.blocked_sql_keywords:
            if re.search(rf"\b{keyword}\b", query_upper):
                return {
                    "valid": False,
                    "reason": f"SECURITY_VIOLATION: Prohibited statement type '{keyword}'. Only SELECT queries are permitted.",
                    "sanitized_query": None,
                }

        # 3. Check for restricted tables
        for table in self.restricted_tables:
            if re.search(rf"\b{table}\b", query_upper, re.IGNORECASE):
                return {
                    "valid": False,
                    "reason": f"SECURITY_VIOLATION: Access to restricted table '{table}' is forbidden.",
                    "sanitized_query": None,
                }

        # 4. Must start with SELECT or WITH
        if not (query_upper.startswith("SELECT") or query_upper.startswith("WITH")):
            return {
                "valid": False,
                "reason": "SECURITY_VIOLATION: Query must begin with SELECT or WITH clause.",
                "sanitized_query": None,
            }

        # 5. Enforce mandatory LIMIT 100 if missing
        sanitized = sql_query.strip().rstrip(";")
        if "LIMIT" not in query_upper:
            sanitized += " LIMIT 100"

        return {
            "valid": True,
            "reason": "Query passed all security AST guardrails.",
            "sanitized_query": sanitized,
        }

    def arbitrate_output(
        self, prompt: str, generated_text: str, consensus_threshold: float = 0.8
    ) -> dict:
        """
        Multi-agent output arbitration system:
        - Evaluates output for structural hallucination, incomplete code blocks, or unsafe commands.
        - Calculates an arbitration confidence score.
        """
        issues = []
        score = 1.0

        # Check for unclosed code fences
        fence_count = generated_text.count("```")
        if fence_count % 2 != 0:
            issues.append("Unterminated markdown code block detected")
            score -= 0.25

        # Check for placeholder hallucinations
        placeholders = [
            "<INSERT_KEY_HERE>",
            "TODO: IMPLEMENT",
            "[YOUR_API_KEY]",
            "example.com",
        ]
        for ph in placeholders:
            if ph in generated_text:
                issues.append(f"Unresolved placeholder detected: {ph}")
                score -= 0.2

        # Check for destructive shell commands
        dangerous_cmds = ["rm -rf", "format c:", "del /f /s /q", "dd if="]
        for cmd in dangerous_cmds:
            if cmd in generated_text.lower():
                issues.append(f"CRITICAL: Unsafe shell command detected: {cmd}")
                score -= 0.6

        passed = (score >= consensus_threshold) and ("CRITICAL" not in "".join(issues))

        record = {
            "prompt_sample": prompt[:60] + "..." if len(prompt) > 60 else prompt,
            "passed": passed,
            "confidence_score": round(max(0.0, score), 2),
            "issues_detected": issues,
        }

        self.arbitration_history.append(record)
        if len(self.arbitration_history) > 100:
            self.arbitration_history.pop(0)

        return record

    def get_guardrails_summary(self) -> dict:
        """Returns summary metrics for arbitration and SQL guardrails."""
        total = len(self.arbitration_history)
        passed_count = sum(1 for r in self.arbitration_history if r["passed"])
        return {
            "total_arbitrated_responses": total,
            "passed_responses": passed_count,
            "pass_rate_percent": (
                round((passed_count / total * 100), 1) if total > 0 else 100.0
            ),
            "blocked_sql_keywords": self.blocked_sql_keywords,
            "restricted_tables": self.restricted_tables,
        }


# Singleton instance
enterprise_guardrails = EnterpriseAIGuardrails()
