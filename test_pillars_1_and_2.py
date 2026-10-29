"""
===================================================================
D.E.E.P SOVEREIGN AI: TEST SUITE FOR PILLARS 1 & 2
===================================================================
Pillar 1: Vision Mutex & Zero-Copy Shared Memory Frame Ingestion
Pillar 2: Dream Memory Consolidation (Qdrant -> PostgreSQL Durable Graph)
"""

import os
import sys
import time
import json
import unittest
import numpy as np

# Ensure utf-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import db_engine
import qdrant_session_cache
from shared_memory_frame_buffer import (
    SharedMemoryFrameWriter,
    SharedMemoryFrameReader,
    acquire_vision_frame,
    DEFAULT_BUFFER_NAME,
    force_cleanup_shared_memory
)
from enhanced_knowledge_graph import enhanced_kg
import memory_engine
import sleep_phase_dream_engine


class TestPillars1And2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sleep_phase_dream_engine.init_db()
        force_cleanup_shared_memory(DEFAULT_BUFFER_NAME)

    @classmethod
    def tearDownClass(cls):
        force_cleanup_shared_memory(DEFAULT_BUFFER_NAME)

    # =================================================================
    # PILLAR 1: VISION MUTEX & ZERO-COPY SHARED MEMORY INGESTION
    # =================================================================

    def test_01_shared_memory_frame_buffer_write_and_acquire(self):
        """Pillar 1: Verify writing to shared memory and zero-conflict acquisition."""
        test_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
        # Add distinctive test marker
        test_frame[100:150, 100:150, :] = 255

        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        writer.write_frame(test_frame)

        # Acquire frame via zero-copy shared memory
        acquired = acquire_vision_frame(camera_index=0, name=DEFAULT_BUFFER_NAME, fallback_to_hardware=False)
        self.assertIsNotNone(acquired, "Frame should be acquired from shared memory buffer")
        self.assertEqual(acquired.shape, (480, 640, 3))
        self.assertEqual(acquired.dtype, np.uint8)
        self.assertEqual(acquired[120, 120, 0], 255, "Test marker should match pixel content exactly")
        writer.close()

    def test_02_vision_engine_uses_acquire_frame(self):
        """Pillar 1: Verify vision_engine.capture_webcam_hardware_vision reads from shared buffer."""
        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
        sample_img[:, :] = (50, 100, 150)
        writer.write_frame(sample_img)

        from vision_engine import capture_webcam_hardware_vision
        res = capture_webcam_hardware_vision()
        self.assertTrue(res.get("success"), f"Hardware vision should succeed: {res.get('error')}")
        self.assertEqual(res.get("resolution"), "640x480")
        writer.close()

    def test_03_live_camera_vision_uses_acquire_frame(self):
        """Pillar 1: Verify live_camera_vision captures via shared memory."""
        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
        writer.write_frame(sample_img)

        from live_camera_vision import LiveCameraVisionEngine
        cam = LiveCameraVisionEngine(camera_index=0)
        res = cam.capture_live_frame_analysis()
        self.assertTrue(res.get("success"), f"Live camera vision should succeed: {res.get('error')}")
        self.assertIn("image_b64", res)
        writer.close()

    def test_04_sign_language_engine_uses_acquire_frame(self):
        """Pillar 1: Verify sign_language_engine captures via shared memory."""
        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
        writer.write_frame(sample_img)

        from sign_language_engine import SignLanguageVisionEngine
        sl = SignLanguageVisionEngine(camera_index=0)
        res = sl.recognize_sign_gesture()
        self.assertTrue(res.get("success"), f"Sign language engine should succeed: {res.get('error')}")
        self.assertIn("gesture", res)
        writer.close()

    def test_05_facial_expression_engine_uses_acquire_frame(self):
        """Pillar 1: Verify facial_expression_engine captures via shared memory."""
        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
        writer.write_frame(sample_img)

        from facial_expression_engine import FacialExpressionEngine
        fe = FacialExpressionEngine(camera_index=0)
        res = fe.analyze_facial_expression()
        self.assertTrue(res.get("success"), f"Facial expression analysis should succeed: {res.get('error')}")
        self.assertIn("image_b64", res)
        writer.close()

    def test_06_mediapipe_kinematics_uses_acquire_frame(self):
        """Pillar 1: Verify mediapipe kinematics captures via shared memory when frame_or_path is None."""
        writer = SharedMemoryFrameWriter(name=DEFAULT_BUFFER_NAME)
        sample_img = np.zeros((480, 640, 3), dtype=np.uint8)
        writer.write_frame(sample_img)

        from mediapipe_hand_face_kinematics import MediaPipeHandFaceKinematicsEngine
        mpk = MediaPipeHandFaceKinematicsEngine()
        res = mpk.process_frame(frame_or_path=None)
        self.assertIn("hand_tracking", res)
        self.assertIn("face_kinematics", res)
        writer.close()

    # =================================================================
    # PILLAR 2: DREAM MEMORY CONSOLIDATION (QDRANT -> POSTGRESQL DURABLE GRAPH)
    # =================================================================

    def test_07_no_sqlite_in_sleep_phase_dream_engine(self):
        """Pillar 2: Verify sleep_phase_dream_engine is completely purged of SQLite."""
        with open("sleep_phase_dream_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("sqlite3", content, "sleep_phase_dream_engine must not import sqlite3")
        self.assertNotIn("dream_memory.db", content, "sleep_phase_dream_engine must not reference dream_memory.db")

    def test_08_qdrant_cache_scroll_recent_turns(self):
        """Pillar 2: Verify Qdrant hot session cache stores and scrolls turns."""
        q = qdrant_session_cache.get_qdrant_cache()
        test_session = f"session_test_{int(time.time())}"
        q.cache_session_turn(test_session, "user", "What is the clock frequency of the PIC18F85K22?")
        q.cache_session_turn(test_session, "assistant", "The PIC18F85K22 runs on a 4.9152 MHz external crystal.")

        turns = q.get_recent_session_turns(session_id=test_session, limit=10)
        self.assertGreaterEqual(len(turns), 2, "Must retrieve at least 2 turns")
        roles = [t["role"] for t in turns]
        self.assertIn("user", roles)
        self.assertIn("assistant", roles)

    def test_09_dream_consolidation_qdrant_to_postgres_graph(self):
        """Pillar 2: Verify dream consolidation distills Qdrant session turns to PostgreSQL graph."""
        q = qdrant_session_cache.get_qdrant_cache()
        test_session = f"dream_session_audit_{int(time.time())}"

        q.cache_session_turn(
            session_id=test_session,
            role="user",
            text="How is the MCP9701 temperature sensor connected to the PIC18F85K22?"
        )
        q.cache_session_turn(
            session_id=test_session,
            role="assistant",
            text="The MCP9701 linear active thermistor is wired to AN0 on the PIC18F85K22 with 19.5 mV/C slope and 400 mV offset at 0C. Line 1 of the 16x2 LCD is broken so render solely on Line 2 (0xC0)."
        )

        # Execute dream consolidation
        telemetry = sleep_phase_dream_engine.distill_and_consolidate(
            session_id=test_session,
            max_turns=10,
            export_finetune=True
        )

        self.assertTrue(telemetry.get("success"), f"Consolidation must succeed: {telemetry}")
        self.assertEqual(telemetry.get("source"), "qdrant")
        self.assertGreaterEqual(telemetry.get("consolidated_turns"), 2)
        self.assertGreaterEqual(telemetry.get("entities_created"), 1)
        self.assertGreaterEqual(telemetry.get("observations_added"), 1)
        self.assertGreaterEqual(telemetry.get("finetune_exported"), 1)

        # Verify Qdrant cache was flushed for this session
        remaining_turns = q.get_recent_session_turns(session_id=test_session)
        self.assertEqual(len(remaining_turns), 0, "Qdrant volatile cache for session should be empty after consolidation")

        # Verify PostgreSQL kg_entities has the entities
        conn = db_engine.get_db_connection()
        conn.row_factory = True
        c = conn.cursor()
        c.execute("SELECT name FROM kg_entities WHERE name IN ('PIC18F85K22', 'MCP9701')")
        entities = [r["name"] for r in c.fetchall()]
        self.assertIn("PIC18F85K22", entities)
        self.assertIn("MCP9701", entities)

        # Verify PostgreSQL dream_consolidation_log audit record
        c.execute("SELECT session_id, turn_count, entities_count FROM dream_consolidation_log WHERE session_id = %s", (test_session,))
        audit = c.fetchone()
        self.assertIsNotNone(audit, "Audit record must be logged in dream_consolidation_log")
        self.assertEqual(audit["session_id"], test_session)
        self.assertGreaterEqual(audit["turn_count"], 2)
        conn.close()

    def test_10_dream_secret_scrubbing_in_finetune(self):
        """Pillar 2: Verify secrets and API keys are scrubbed before export to dataset_fine_tune.jsonl."""
        q = qdrant_session_cache.get_qdrant_cache()
        test_session = f"dream_secret_{int(time.time())}"
        fake_secret = "secret_apikey_999888777666"

        q.cache_session_turn(
            session_id=test_session,
            role="user",
            text=f"Store my api_key = {fake_secret} securely for the database."
        )
        q.cache_session_turn(
            session_id=test_session,
            role="assistant",
            text=f"Understood. The api_key = {fake_secret} has been encrypted in PostgreSQL."
        )

        res = sleep_phase_dream_engine.distill_and_consolidate(
            session_id=test_session,
            max_turns=10,
            export_finetune=True
        )
        self.assertTrue(res.get("success"))

        # Verify secret was scrubbed in fine-tune file
        with open("dataset_fine_tune.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_entry_str = lines[-1]
        self.assertNotIn(fake_secret, last_entry_str, "Raw secret must NEVER leak into fine-tuning dataset")
        self.assertIn("[REDACTED_SECRET]", last_entry_str, "Scrubbed token should be substituted with redaction marker")

    def test_11_backward_compatible_dream_cycle_call(self):
        """Pillar 2: Verify legacy dream_cycle() entrypoint works cleanly."""
        res = sleep_phase_dream_engine.dream_cycle(max_turns=5, export_finetune=False)
        self.assertTrue(res.get("success"))
        self.assertIn("consolidated_turns", res)
        self.assertIn("duration_seconds", res)


if __name__ == "__main__":
    unittest.main()
