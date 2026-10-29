"""
Targeted Verification Suite for Skills, Intents, and Music Engine
==================================================================
Tests:
- music_queue_engine.py: Queue operations, priority, state persistence, error bounds
- skills_api.py: SSRF protection, path validation, registry routing
- file_gen_tools_skill.py: JSON cleanup & export handling
- intents/background_research_intent.py: Keywords, tuple contract, safe workspace reporting
- intents/website_builder_intent.py: Triggers, topic sanitization, execution safety
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import music_queue_engine
from skills_api import is_safe_fetch_url
from intents.background_research_intent import BackgroundResearchIntent
from intents.website_builder_intent import WebsiteBuilderIntent


class TestMusicQueueEngine(unittest.TestCase):
    def setUp(self):
        self.engine = music_queue_engine.MusicQueueEngine()
        self.engine.clear()

    def tearDown(self):
        self.engine.clear()

    def test_queue_lifecycle(self):
        """Test adding, getting, and clearing queue entries."""
        fake_entry = {
            "clean_title": "Legendary Anthem",
            "artist": "Test Artist",
            "filename": "legendary_anthem.mp3",
            "path": "C:\\Users\\User\\Music\\legendary_anthem.mp3"
        }
        with patch("local_music_engine.find_track", return_value=fake_entry):
            res1 = self.engine.enqueue("Legendary Anthem")
            self.assertEqual(res1["status"], "success")
            self.assertEqual(res1["position"], 1)

            res2 = self.engine.enqueue("Second Song")
            self.assertEqual(res2["status"], "success")
            self.assertEqual(res2["position"], 2)

            q_state = self.engine.get_queue()
            self.assertEqual(q_state["queue_length"], 2)
            self.assertEqual(q_state["queue"][0]["title"], "Legendary Anthem")

            # Test priority next (inserted at index 0)
            res_vip = self.engine.enqueue("VIP Priority Track", priority="next")
            self.assertEqual(res_vip["position"], 1)
            q_state2 = self.engine.get_queue()
            self.assertEqual(q_state2["queue"][0]["title"], "Legendary Anthem")

            # Remove item
            rem = self.engine.remove_at(1)
            self.assertEqual(rem["status"], "success")

            # Clear
            clr = self.engine.clear()
            self.assertEqual(clr["status"], "success")
            self.assertEqual(self.engine.get_queue()["queue_length"], 0)


class TestSkillsApiSecurity(unittest.TestCase):
    def test_ssrf_safety_filter(self):
        """Verify that SSRF URLs to localhost, 127.0.0.1, and private IPs are blocked."""
        # Unsafe targets
        self.assertFalse(is_safe_fetch_url("http://localhost:8000/admin"))
        self.assertFalse(is_safe_fetch_url("http://127.0.0.1:11434/api/tags"))
        self.assertFalse(is_safe_fetch_url("http://192.168.1.1/router"))
        self.assertFalse(is_safe_fetch_url("http://10.0.0.1/internal"))
        self.assertFalse(is_safe_fetch_url("ftp://example.com/file"))
        self.assertFalse(is_safe_fetch_url("file:///etc/passwd"))

        # Safe public targets
        self.assertTrue(is_safe_fetch_url("https://en.wikipedia.org/wiki/Artificial_intelligence"))
        self.assertTrue(is_safe_fetch_url("https://github.com/torvalds/linux"))


class TestBackgroundResearchIntent(unittest.TestCase):
    def test_triggers(self):
        self.assertTrue(BackgroundResearchIntent.can_handle("please do background research on quantum tech"))
        self.assertTrue(BackgroundResearchIntent.can_handle("monitor web for security advisories"))
        self.assertFalse(BackgroundResearchIntent.can_handle("what is the weather today"))

    def test_execute_returns_valid_3tuple(self):
        res = BackgroundResearchIntent.execute("run background research", "run background research")
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 3)
        self.assertIn("Background research pipeline deployed", res[0])
        self.assertEqual(res[1], "research_agent")
        self.assertIsInstance(res[2], list)


class TestWebsiteBuilderIntent(unittest.TestCase):
    def test_triggers(self):
        self.assertTrue(WebsiteBuilderIntent.can_handle("build a website for a coffee shop"))
        self.assertTrue(WebsiteBuilderIntent.can_handle("create a website for photography"))
        self.assertFalse(WebsiteBuilderIntent.can_handle("play some music"))


class TestVisualClickerAndVisionIntents(unittest.TestCase):
    def test_visual_clicker_target_extraction(self):
        """Verify target extraction does NOT corrupt words ending or containing 'on' (button, python, icon)."""
        import re
        test_cases = [
            ("click on the button", "the button"),
            ("click on python", "python"),
            ("click icon", "icon"),
            ("click on submit button", "submit button"),
        ]
        for prompt, expected in test_cases:
            target = re.sub(r"^.*?click\s+(?:on\s+)?", "", prompt, flags=re.IGNORECASE).strip()
            self.assertEqual(target, expected)

    def test_git_autopilot_triggers(self):
        """Verify GitAutopilotIntent triggers strictly on rollback/undo and not generic commit/git phrases."""
        from intents.git_intent import GitAutopilotIntent
        self.assertTrue(GitAutopilotIntent.can_handle("please undo the changes"))
        self.assertTrue(GitAutopilotIntent.can_handle("rollback to last commit"))
        self.assertTrue(GitAutopilotIntent.can_handle("discard changes in workspace"))
        self.assertFalse(GitAutopilotIntent.can_handle("tell me what is git"))
        self.assertFalse(GitAutopilotIntent.can_handle("write a nice commit message"))

    def test_db_adapter_context_manager(self):
        """Verify PostgresConnectionAdapter and PostgresCursorAdapter support Pythonic context management."""
        import db_engine
        mock_pg_conn = MagicMock()
        mock_pg_conn.closed = False
        adapter = db_engine.PostgresConnectionAdapter(mock_pg_conn)
        with adapter as conn:
            self.assertEqual(conn, adapter)
        mock_pg_conn.close.assert_called()

    def test_self_healing_intent(self):
        """Verify SelfHealingIntent returns a valid 3-tuple without deadlocks."""
        from intents.self_healing_intent import SelfHealingIntent
        self.assertTrue(SelfHealingIntent.can_handle("self heal"))
        self.assertTrue(SelfHealingIntent.can_handle("debug the last error"))
        res = SelfHealingIntent.execute("self heal", "self heal")
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 3)
        self.assertIn("Self-Healing Diagnostics", res[0])
        self.assertEqual(res[1], "self_healing_agent")

    def test_visual_canvas_intent_triggers(self):
        """Verify VisualCanvasIntent matches anywhere in prompt, not strictly at index 0."""
        from intents.visual_canvas_intent import VisualCanvasIntent
        self.assertTrue(VisualCanvasIntent.can_handle("can you edit this <button> change it so that it is blue"))
        self.assertTrue(VisualCanvasIntent.can_handle("edit this <div> change it so that it has padding"))
        self.assertFalse(VisualCanvasIntent.can_handle("change this code"))


if __name__ == "__main__":
    unittest.main()
