"""
Test Suite for Netflix Hystrix Circuit Breakers and Facebook Infer-Style Static AST Scanner
=============================================================================================
Verifies:
1. hystrix_circuit_breaker.py:
   - State transitions: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
   - Instant short-circuiting without blocking UI threads
   - Graceful fallback execution
   - Bulkhead concurrency semaphore limiting
   - Registry telemetry matrix
2. code_scanner_engine.py:
   - Infer-style AST visitor detects resource handle leaks
   - Silent exception swallowing detection
   - SQL injection risk detection on string interpolation
   - Embedded MCU C firmware rules (clock frequency, LCD pinout, config fuses)
"""

import ast
import time
import unittest
from unittest.mock import MagicMock

from hystrix_circuit_breaker import (
    HystrixCircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
    CircuitBreakerRegistry,
)
from code_scanner_engine import InferASTVisitor, scan_embedded_c_file


class TestHystrixCircuitBreaker(unittest.TestCase):
    def test_closed_state_success(self):
        """Normal calls succeed and keep state CLOSED."""
        breaker = HystrixCircuitBreaker(name="test_service", failure_threshold=2)
        mock_fn = MagicMock(return_value="OK")

        res = breaker.call(mock_fn, "arg1")
        self.assertEqual(res, "OK")
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.successful_requests, 1)
        self.assertEqual(breaker.failed_requests, 0)

    def test_trip_to_open_and_fallback(self):
        """Consecutive failures trip circuit to OPEN, invoking fallback immediately."""
        fallback_fn = MagicMock(return_value="FALLBACK_ACTIVE")
        breaker = HystrixCircuitBreaker(
            name="test_trip",
            failure_threshold=2,
            recovery_timeout=0.2,
            default_fallback=fallback_fn,
        )

        def failing_fn():
            raise ConnectionError("Service unreachable")

        # 1st failure: remains CLOSED, returns graceful fallback
        res1 = breaker.call(failing_fn)
        self.assertEqual(res1, "FALLBACK_ACTIVE")
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker._consecutive_failures, 1)

        # 2nd failure: trips to OPEN and executes fallback
        res2 = breaker.call(failing_fn)
        self.assertEqual(res2, "FALLBACK_ACTIVE")
        self.assertEqual(breaker.state, CircuitState.OPEN)

        # 3rd attempt: short-circuits instantly without calling failing_fn
        probe_fn = MagicMock()
        res_fast = breaker.call(probe_fn)
        self.assertEqual(res_fast, "FALLBACK_ACTIVE")
        probe_fn.assert_not_called()
        self.assertGreater(breaker.short_circuited_requests, 0)

    def test_half_open_recovery(self):
        """After recovery timeout, canary probe succeeds and resets state to CLOSED."""
        breaker = HystrixCircuitBreaker(
            name="test_recovery",
            failure_threshold=1,
            recovery_timeout=0.1,  # Short 100ms timeout for test
        )

        def failing_fn():
            raise RuntimeError("Down")

        with self.assertRaises(RuntimeError):
            breaker.call(failing_fn)
        self.assertEqual(breaker._state, CircuitState.OPEN)

        # Wait for recovery timeout
        time.sleep(0.15)
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)

        # Canary probe succeeds
        canary = MagicMock(return_value="RECOVERED")
        res = breaker.call(canary)
        self.assertEqual(res, "RECOVERED")
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker._consecutive_failures, 0)

    def test_bulkhead_concurrency_limit(self):
        """Bulkhead rejects executions beyond max_concurrent limit."""
        breaker = HystrixCircuitBreaker(
            name="test_bulkhead",
            bulkhead_max_concurrent=1,
            default_fallback=lambda *a, **k: "OVERLOADED_FALLBACK"
        )
        # Saturated semaphore
        breaker.bulkhead_semaphore.acquire(blocking=False)
        res = breaker.call(lambda: "OK")
        self.assertEqual(res, "OVERLOADED_FALLBACK")
        breaker.bulkhead_semaphore.release()

    def test_registry_telemetry(self):
        """Registry manages breakers and returns telemetry matrix."""
        registry = CircuitBreakerRegistry()
        b1 = registry.get_or_create("service_alpha", failure_threshold=3)
        b2 = registry.get_or_create("service_beta", failure_threshold=5)

        matrix = registry.get_telemetry_matrix()
        self.assertEqual(len(matrix), 2)
        names = [item["name"] for item in matrix]
        self.assertIn("service_alpha", names)
        self.assertIn("service_beta", names)


class TestInferASTScanner(unittest.TestCase):
    def test_resource_leak_detection(self):
        """Detects unmanaged get_db_connection() outside context managers."""
        code = """
def process():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    # Missing conn.close() in finally block
"""
        tree = ast.parse(code)
        visitor = InferASTVisitor("sample.py", "sample.py")
        visitor.visit(tree)
        self.assertTrue(any("Resource Handle Check" in f for f in visitor.findings))

    def test_silent_exception_swallow_detection(self):
        """Detects bare 'except: pass' without logging or feedback."""
        code = """
def risky():
    try:
        do_something()
    except Exception:
        pass
"""
        tree = ast.parse(code)
        visitor = InferASTVisitor("logic.py", "logic.py")
        visitor.visit(tree)
        self.assertTrue(any("Silent Swallow" in f for f in visitor.findings))

    def test_sql_injection_detection(self):
        """Detects string-interpolated f-strings in database cursor execute."""
        code = """
def query_user(user_input):
    cursor.execute(f"SELECT * FROM accounts WHERE name = '{user_input}'")
"""
        tree = ast.parse(code)
        visitor = InferASTVisitor("db.py", "db.py")
        visitor.visit(tree)
        self.assertTrue(any("SQL Injection Risk" in f for f in visitor.findings))

    def test_embedded_c_scanner_checks(self):
        """Verifies embedded analyzer flags mismatched crystal and wrong port definitions."""
        import tempfile
        c_code = """
#define _XTAL_FREQ 8000000UL
#pragma config FOSC = HS1
#define LCD_DATA_LAT LATD
"""
        with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as tmp:
            tmp.write(c_code)
            tmp_path = tmp.name

        findings = scan_embedded_c_file(tmp_path, "test_firmware.c")
        self.assertTrue(any("Clock Frequency Alert" in f for f in findings))
        self.assertTrue(any("Config Fuse Warning" in f for f in findings))
        self.assertTrue(any("Embedded Hardware Rule" in f for f in findings))


if __name__ == "__main__":
    unittest.main()
