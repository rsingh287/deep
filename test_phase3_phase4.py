"""
===================================================================
D.E.E.P TEST SUITE: PHASE 3 (TIERED MEMORY) & PHASE 4 (IPC SHM)
===================================================================
Empirical verification suite for:
1. Tier 1 Qdrant Hot Session Cache (gRPC 6334 vector caching, search, clear)
2. Tier 2 PostgreSQL Durable Knowledge Graph (entities, observations, relations)
3. Least-privilege deep_reader validation on PostgreSQL durable graph
4. Tiered memory integration in memory_engine (hot Qdrant + durable PostgreSQL)
5. Zero-copy Shared Memory Frame Buffer (ping-pong double-buffering, IPC, cleanup)
"""

import os
import sys
import time
import unittest
import numpy as np

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import qdrant_session_cache
from enhanced_knowledge_graph import enhanced_kg
import memory_engine
import shared_memory_frame_buffer as shm_buf
import enterprise_ai_guardrails as eg
import postgresql_engine


class TestPhase3Phase4Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure fresh state for test session
        cls.test_session_id = f"test_session_{int(time.time())}"
        cls.q_cache = qdrant_session_cache.get_qdrant_cache()

    # =================================================================
    # PHASE 3: TIER 1 (QDRANT HOT SESSION CACHE VIA gRPC 6334)
    # =================================================================

    def test_01_qdrant_hot_cache_configuration(self):
        """Verifies Qdrant gRPC 6334 target, collection configuration, and tier status."""
        status = self.q_cache.get_tier_status()
        self.assertEqual(status["tier"], 1)
        self.assertEqual(status["grpc_port"], 6334)
        self.assertEqual(status["collection"], "hot_session_cache")
        self.assertEqual(status["vector_dimension"], 768)
        self.assertIn(status["backend"], ["gRPC", "In-Memory Fallback"])

    def test_02_qdrant_session_caching_and_vector_search(self):
        """Tests caching conversation turns into Tier 1 hot memory and vector recall."""
        # 1. Cache user and assistant turns
        turn1_id = self.q_cache.cache_session_turn(
            session_id=self.test_session_id,
            role="user",
            text="How do I configure the PIC18F85K22 analog to digital converter on AN0?"
        )
        self.assertTrue(bool(turn1_id))

        turn2_id = self.q_cache.cache_session_turn(
            session_id=self.test_session_id,
            role="assistant",
            text="Set TRISAbits.TRISA0 = 1, configure ANCON0 for analog input, and set ADCON1 for 5V VDD reference."
        )
        self.assertTrue(bool(turn2_id))

        # 2. Vector search across session
        hits = self.q_cache.search_session_cache(
            query="ANCON0 analog configuration",
            session_id=self.test_session_id,
            limit=2
        )
        self.assertGreaterEqual(len(hits), 1)
        self.assertTrue(any("TRISAbits" in h["text"] for h in hits))

    def test_03_qdrant_session_clear(self):
        """Tests scoped clearance of hot session cache."""
        temp_sess = f"temp_sess_{int(time.time())}"
        self.q_cache.cache_session_turn(temp_sess, "user", "Temporary query")
        cleared = self.q_cache.clear_session_cache(session_id=temp_sess)
        self.assertTrue(cleared)
        hits = self.q_cache.search_session_cache("Temporary query", session_id=temp_sess)
        self.assertEqual(len(hits), 0)

    # =================================================================
    # PHASE 3: TIER 2 (POSTGRESQL DURABLE GRAPH & RELATIONAL LEDGER)
    # =================================================================

    def test_04_postgresql_durable_graph_storage(self):
        """Verifies entities, observations, and relations are stored durably in PostgreSQL deep_db."""
        self.assertTrue(enhanced_kg.use_postgres)

        ent_name = f"TEST_TIER2_MCU_{int(time.time())}"
        c_res = enhanced_kg.create_entities([{
            "name": ent_name,
            "entityType": "MICROCONTROLLER",
            "description": "Durable hardware entity in PostgreSQL deep_db"
        }])
        self.assertTrue(c_res["success"])
        self.assertIn(ent_name, c_res["createdEntities"])

        # Add durable observation
        obs_res = enhanced_kg.add_observations(
            entity_name=ent_name,
            observations=["Durable observation: Operating voltage 3.3V to 5.5V"],
            confidence=0.98,
            source="hardware_datasheet"
        )
        self.assertTrue(obs_res["success"])

        # Query durable graph
        q_res = enhanced_kg.query_graph(entity_name=ent_name)
        self.assertTrue(q_res["success"])
        self.assertEqual(len(q_res["entities"]), 1)
        self.assertGreaterEqual(len(q_res["observations"]), 1)
        self.assertIn("3.3V to 5.5V", q_res["observations"][0]["observation_text"])

    def test_05_deep_reader_least_privilege_on_durable_graph(self):
        """Verifies least-privilege deep_reader role can query durable graph tables in deep_db."""
        guard = eg.EnterpriseAIGuardrails()
        res = guard.execute_safely("SELECT name, entity_type FROM kg_entities LIMIT 5")
        self.assertTrue(res["success"])
        self.assertIsInstance(res["rows"], list)

    # =================================================================
    # PHASE 3: TIERED MEMORY INTEGRATION (HOT CACHE + DURABLE GRAPH)
    # =================================================================

    def test_06_tiered_memory_store_and_recall_integration(self):
        """Tests unified memory_engine routing: stores to PG + Qdrant and recalls with tier markers."""
        concept = f"PIC18F_BAUD_{int(time.time())}"
        fact = "UART1 operates at 115200 baud with BRGH=1 and BRG16=1"

        store_res = memory_engine.store_fact(concept, fact)
        self.assertEqual(store_res["status"], "success")
        self.assertIn("Tiered Memory", store_res["message"])

        # Recall facts
        recalled = memory_engine.recall_facts(concept, limit=3)
        self.assertGreaterEqual(len(recalled), 1)
        self.assertEqual(recalled[0]["concept"], concept)
        self.assertIn("115200 baud", recalled[0]["facts"])
        self.assertIn("Tier", recalled[0]["tier"])

    def test_07_chromadb_eradication_verification(self):
        """Verifies ChromaDB is not imported or utilized in memory_engine (zero VRAM thrashing)."""
        self.assertFalse(hasattr(memory_engine, "chromadb"))
        self.assertFalse(hasattr(memory_engine, "get_chroma_collection"))

    # =================================================================
    # PHASE 4: IPC OPTIMIZATION (SAFE, LEAK-PROOF SHARED MEMORY)
    # =================================================================

    def test_08_shared_memory_frame_buffer_ping_pong(self):
        """Tests double-buffered shared RAM frame exchange without tearing."""
        buf_name = f"deep_test_ping_pong_{int(time.time())}"
        w, h = 640, 480

        with shm_buf.SharedMemoryFrameWriter(name=buf_name, max_width=w, max_height=h) as writer:
            with shm_buf.SharedMemoryFrameReader(name=buf_name, max_width=w, max_height=h) as reader:
                # Frame 1: solid red
                frame1 = np.zeros((h, w, 3), dtype=np.uint8)
                frame1[:, :] = (0, 0, 255)
                self.assertTrue(writer.write_frame(frame1))

                read1, meta1 = reader.read_frame(copy=True)
                self.assertIsNotNone(read1)
                self.assertEqual(meta1["sequence"], 1)
                self.assertEqual(meta1["width"], w)
                self.assertEqual(meta1["height"], h)
                self.assertEqual(read1[0, 0, 2], 255)  # Red channel
                self.assertEqual(meta1["slot"], 1)  # Slot 1 active

                # Frame 2: solid green (must alternate to slot 0)
                frame2 = np.zeros((h, w, 3), dtype=np.uint8)
                frame2[:, :] = (0, 255, 0)
                self.assertTrue(writer.write_frame(frame2))

                read2, meta2 = reader.read_frame(copy=True)
                self.assertIsNotNone(read2)
                self.assertEqual(meta2["sequence"], 2)
                self.assertEqual(read2[0, 0, 1], 255)  # Green channel
                self.assertEqual(meta2["slot"], 0)  # Slot 0 active

    def test_09_shared_memory_zero_copy_view(self):
        """Tests sub-millisecond zero-copy direct memory view (copy=False)."""
        buf_name = f"deep_test_zerocopy_{int(time.time())}"
        w, h = 320, 240

        with shm_buf.SharedMemoryFrameWriter(name=buf_name, max_width=w, max_height=h) as writer:
            with shm_buf.SharedMemoryFrameReader(name=buf_name, max_width=w, max_height=h) as reader:
                test_pattern = np.arange(h * w * 3, dtype=np.uint8).reshape((h, w, 3))
                writer.write_frame(test_pattern)

                # Read zero-copy view
                view, meta = reader.read_frame(copy=False)
                self.assertIsNotNone(view)
                self.assertEqual(view.shape, (h, w, 3))
                self.assertTrue(np.array_equal(view, test_pattern))
                self.assertLess(meta["latency_ms"], 50.0)

    def test_10_shared_memory_leak_proof_cleanup(self):
        """Verifies clean handle closure and unlinking on Windows."""
        buf_name = f"deep_test_cleanup_{int(time.time())}"
        writer = shm_buf.SharedMemoryFrameWriter(name=buf_name, max_width=160, max_height=120)
        writer.write_frame(np.zeros((120, 160, 3), dtype=np.uint8))
        self.assertFalse(writer.is_closed)

        # Close and unlink
        writer.close()
        writer.unlink()
        self.assertTrue(writer.is_closed)

        # Confirm buffer is removed
        reader = shm_buf.SharedMemoryFrameReader(name=buf_name, max_width=160, max_height=120)
        frame, meta = reader.read_frame()
        self.assertIsNone(frame)
        self.assertIn("error", meta)
        reader.close()


if __name__ == "__main__":
    unittest.main()
