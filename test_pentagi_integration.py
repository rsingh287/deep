"""
Integration Test Suite for PentAGI & D.E.E.P
Tests zero-trust scope enforcement, intent dispatching,
Docker lifecycle abstraction, and executive voice feedback.
"""

import unittest
import sys
import os

# Add local_ai_gui to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pentagi_bridge_engine
from intents.pentest_intent import PentestIntent
from intents.registry import execute_intent


class TestPentAGIIntegration(unittest.TestCase):

    def test_zero_trust_target_whitelist(self):
        """Verifies that only authorized local/internal targets pass zero-trust validation."""
        # Allowed targets
        allowed = [
            "localhost",
            "127.0.0.1",
            "localhost:5000",
            "http://127.0.0.1:8080",
            "192.168.1.100:3000",
            "10.0.0.5",
            "host.docker.internal"
        ]
        for target in allowed:
            is_valid, msg = pentagi_bridge_engine.validate_target_scope(target)
            self.assertTrue(is_valid, f"Expected {target} to be allowed, but got: {msg}")

        # Blocked external targets
        blocked = [
            "google.com",
            "8.8.8.8",
            "https://evil-target.org",
            "142.250.190.46",
            "api.stripe.com"
        ]
        for target in blocked:
            is_valid, msg = pentagi_bridge_engine.validate_target_scope(target)
            self.assertFalse(is_valid, f"Expected {target} to be blocked, but was allowed: {msg}")
            self.assertIn("SECURITY BLOCK", msg)

    def test_pentest_intent_can_handle(self):
        """Verifies natural language triggers for PentestIntent."""
        valid_prompts = [
            "pentagi",
            "run pentagi scan",
            "start pentagi",
            "stop pentagi",
            "pentagi status",
            "run a penetration test on localhost:5000",
            "red team assessment against 127.0.0.1",
            "audit network security"
        ]
        for p in valid_prompts:
            self.assertTrue(PentestIntent.can_handle(p.lower()), f"Failed to match trigger: {p}")

        non_matching = [
            "play some music",
            "what is the weather today",
            "open chrome browser"
        ]
        for p in non_matching:
            self.assertFalse(PentestIntent.can_handle(p.lower()), f"Incorrectly matched: {p}")

    def test_preflight_recon_local(self):
        """Tests that local socket reconnaissance works cleanly."""
        res = pentagi_bridge_engine.run_preflight_recon("127.0.0.1:5000")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("host"), "127.0.0.1")
        self.assertEqual(res.get("port"), "5000")
        self.assertIsInstance(res.get("findings"), list)

    def test_execute_intent_integration(self):
        """Tests end-to-end execution through D.E.E.P's modular intent registry."""
        # 1. Status query
        result = execute_intent("check pentagi status", "check pentagi status")
        self.assertIsNotNone(result)
        report, agent, code_blocks = result
        self.assertEqual(agent, "pentagi_orchestrator")
        self.assertIn("PentAGI System Health Monitor", report)

        # 2. Blocked external target
        result_blocked = execute_intent(
            "run pentest against google.com",
            "run pentest against google.com"
        )
        self.assertIsNotNone(result_blocked)
        report_blocked, agent_blocked, _ = result_blocked
        self.assertEqual(agent_blocked, "pentagi_security_guardrail")
        self.assertIn("Zero-Trust Security Gate: BLOCKED", report_blocked)

        # 3. Authorized local target
        result_local = execute_intent(
            "run pentest on 127.0.0.1:5000",
            "run pentest on 127.0.0.1:5000"
        )
        self.assertIsNotNone(result_local)
        report_local, agent_local, _ = result_local
        self.assertEqual(agent_local, "pentagi_orchestrator")
        self.assertIn("PentAGI Autonomous Security Assessment", report_local)

    def test_executive_voice_brevity(self):
        """Verifies voice brevity conforms to D.E.E.P's <= 15 words and no raw Markdown."""
        voice_text = pentagi_bridge_engine.format_executive_voice("ready", "localhost")
        words = voice_text.split()
        self.assertLessEqual(len(words), 15, f"Voice feedback exceeded 15 words: {voice_text}")
        self.assertNotIn("*", voice_text)
        self.assertNotIn("http", voice_text)
        self.assertNotIn("#", voice_text)


if __name__ == "__main__":
    unittest.main()
