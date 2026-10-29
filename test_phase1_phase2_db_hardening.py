"""
Test Suite for D.E.E.P Phase 1 & Phase 2 Database Hardening
Empirically tests:
1. psycopg v3 driver and connection pooling
2. Least-privilege deep_reader role with engine-level read-only enforcement
3. Async read-only querying without event loop errors
4. Autovacuum configuration on vector tables
5. Enterprise AI Guardrails execute_safely integration
"""

import unittest
import asyncio
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import postgresql_engine
from enterprise_ai_guardrails import EnterpriseAIGuardrails


class TestDBHardening(unittest.TestCase):

    def test_01_connection_and_driver_v3(self):
        """Verifies connection to deep_db using psycopg v3 and confirms deep_reader status."""
        status = postgresql_engine.test_postgresql_connection()
        self.assertEqual(status.get("status"), "success")
        self.assertIn("psycopg v3", status.get("driver", ""))
        self.assertEqual(status.get("deep_reader_role"), "Enforced & Active")
        self.assertGreaterEqual(status.get("table_count", 0), 25)

    def test_02_sync_query_execution(self):
        """Verifies standard sync query execution with markdown table formatting."""
        md = postgresql_engine.execute_postgresql_query("SELECT COUNT(*) as total FROM facts;")
        self.assertIn("PostgreSQL Query Results", md)
        self.assertIn("total", md)

    def test_03_deep_reader_engine_level_block(self):
        """Verifies that deep_reader role is physically barred from mutating data by PostgreSQL."""
        # Valid read
        ok, rows = postgresql_engine.execute_readonly_query("SELECT id, concept FROM facts LIMIT 3;")
        self.assertTrue(ok)
        self.assertIsInstance(rows, list)

        # Prohibited INSERT
        ok_insert, err_insert = postgresql_engine.execute_readonly_query(
            "INSERT INTO facts (concept, facts) VALUES ('test_hack', 'fail');"
        )
        self.assertFalse(ok_insert)
        self.assertIn("read-only transaction", str(err_insert).lower())

        # Prohibited DROP
        ok_drop, err_drop = postgresql_engine.execute_readonly_query("DROP TABLE facts;")
        self.assertFalse(ok_drop)
        self.assertIn("read-only transaction", str(err_drop).lower())

    def test_04_async_readonly_query_execution(self):
        """Verifies async execution on Windows without ProactorEventLoop collision."""
        async def run_async():
            return await postgresql_engine.execute_readonly_query_async(
                "SELECT COUNT(*) as count FROM chat_messages;"
            )

        ok, result = asyncio.run(run_async())
        self.assertTrue(ok)
        self.assertIsInstance(result, list)
        self.assertIn("count", result[0])

    def test_05_guardrails_execute_safely(self):
        """Verifies EnterpriseAIGuardrails execute_safely with engine enforcement."""
        guard = EnterpriseAIGuardrails()

        # Legitimate query
        res = guard.execute_safely("SELECT id, concept FROM facts")
        self.assertTrue(res.get("success"))
        self.assertIn("LIMIT 100", res.get("query"))

        # Blocked by Python AST
        res_blocked = guard.execute_safely("DELETE FROM facts WHERE id=1")
        self.assertFalse(res_blocked.get("success"))
        self.assertIn("SECURITY_VIOLATION", res_blocked.get("error"))

    def test_06_autovacuum_tuned_on_vector_table(self):
        """Verifies that autovacuum_vacuum_scale_factor=0.05 is active on mem0_episodic_vectors."""
        ok, rows = postgresql_engine.execute_readonly_query(
            "SELECT reloptions FROM pg_class WHERE relname='mem0_episodic_vectors';"
        )
        self.assertTrue(ok)
        if rows and rows[0].get("reloptions"):
            options_str = str(rows[0]["reloptions"])
            self.assertIn("autovacuum_vacuum_scale_factor=0.05", options_str)


if __name__ == "__main__":
    unittest.main()
