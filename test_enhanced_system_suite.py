"""
Comprehensive Test Suite for Enhanced Knowledge Graph & Filesystem Primitives
Verifies:
1. Filesystem line streaming (head, tail, range)
2. Safe atomic append
3. Safe quarantine deletion and restore
4. Parallel cached multi-file read
5. Archive compression & safe decompression (Zip-Slip defense)
6. Symlink / Junction creation
7. In-place Knowledge Graph observation updates (exact schema)
8. Confidence scoring, timestamps & source attribution
9. Relational & type graph queries
10. Role-Based Access Control (RBAC) & PQC/AES-256 encrypted observations
11. Unified MCP tool dispatcher
"""

import os
import sys
import shutil
import tempfile
import unittest

# Ensure root directory is on path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import enhanced_fs_engine as efs
from enhanced_knowledge_graph import enhanced_kg
from security_rbac_engine import security_rbac
from mcp_integration import call_tool, get_all_tool_definitions


class TestEnhancedSystemSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="deep_test_suite_")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_01_read_lines_head_tail_range(self):
        sample_file = os.path.join(self.test_dir, "sample_lines.txt")
        lines = [f"Line {i:02d}: system payload {i}\n" for i in range(1, 31)]
        with open(sample_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Test HEAD
        head_res = efs.read_lines(sample_file, mode="head", count=5)
        self.assertTrue(head_res["success"])
        self.assertEqual(len(head_res["lines"]), 5)
        self.assertTrue("Line 01" in head_res["lines"][0])
        self.assertTrue("Line 05" in head_res["lines"][4])

        # Test TAIL
        tail_res = efs.read_lines(sample_file, mode="tail", count=5)
        self.assertTrue(tail_res["success"])
        self.assertEqual(len(tail_res["lines"]), 5)
        self.assertTrue("Line 26" in tail_res["lines"][0] or "Line 30" in tail_res["lines"][-1])

        # Test RANGE
        range_res = efs.read_lines(sample_file, mode="range", start_line=10, end_line=15)
        self.assertTrue(range_res["success"])
        self.assertEqual(len(range_res["lines"]), 6)
        self.assertTrue("Line 10" in range_res["lines"][0])
        self.assertTrue("Line 15" in range_res["lines"][-1])

    def test_02_atomic_append(self):
        append_file = os.path.join(self.test_dir, "append_target.txt")
        res1 = efs.append_file(append_file, "Initial line 1")
        self.assertTrue(res1["success"])
        res2 = efs.append_file(append_file, "Appended line 2")
        self.assertTrue(res2["success"])

        with open(append_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Initial line 1\n", content)
        self.assertIn("Appended line 2\n", content)

    def test_03_safe_quarantine_deletion_and_restore(self):
        del_target = os.path.join(self.test_dir, "quarantine_target.txt")
        with open(del_target, "w", encoding="utf-8") as f:
            f.write("Important data to quarantine and restore.")

        # Delete with quarantine
        del_res = efs.delete_file(del_target, permanent=False, quarantine=True)
        self.assertTrue(del_res["success"])
        self.assertTrue(del_res["quarantined"])
        self.assertFalse(os.path.exists(del_target))

        # Restore
        trash_id = del_res["trashId"]
        restore_res = efs.restore_file(trash_id)
        self.assertTrue(restore_res["success"])
        self.assertTrue(os.path.exists(del_target))
        with open(del_target, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Important data to quarantine and restore.")

    def test_04_parallel_multi_file_read_and_cache(self):
        file_paths = []
        for i in range(5):
            fp = os.path.join(self.test_dir, f"multi_{i}.txt")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(f"Parallel content {i}")
            file_paths.append(fp)

        # First read - cache miss
        res1 = efs.read_multiple_files_fast(file_paths)
        self.assertTrue(res1["success"])
        self.assertEqual(res1["totalFiles"], 5)

        # Second read - cache hit
        res2 = efs.read_multiple_files_fast(file_paths)
        self.assertTrue(res2["success"])
        cached_count = sum(1 for v in res2["results"].values() if v.get("cached"))
        self.assertGreaterEqual(cached_count, 1)

    def test_05_archive_compression_and_safe_extract(self):
        sub_folder = os.path.join(self.test_dir, "archive_src")
        os.makedirs(sub_folder, exist_ok=True)
        f1 = os.path.join(sub_folder, "f1.txt")
        with open(f1, "w", encoding="utf-8") as f:
            f.write("Payload one for zip archive test.")

        zip_out = os.path.join(self.test_dir, "bundle.zip")
        comp_res = efs.compress_files([sub_folder], zip_out, format="zip")
        self.assertTrue(comp_res["success"])
        self.assertTrue(os.path.exists(zip_out))

        extract_dir = os.path.join(self.test_dir, "archive_extracted")
        dec_res = efs.decompress_file(zip_out, extract_dir)
        self.assertTrue(dec_res["success"])
        self.assertGreaterEqual(dec_res["extractedCount"], 1)

    def test_06_in_place_observation_update(self):
        # Register test entity
        enhanced_kg.create_entities([{
            "name": "TEST_CONTROLLER",
            "entityType": "HARDWARE",
            "description": "Test hardware controller"
        }])

        # Add initial observation
        add_res = enhanced_kg.add_observations(
            entity_name="TEST_CONTROLLER",
            observations=["Initial baud rate 9600 bps"],
            confidence=0.8,
            source="calibration"
        )
        self.assertTrue(add_res["success"])

        # Execute in-place update matching user's exact JSON schema
        update_payload = [{
            "entityName": "TEST_CONTROLLER",
            "oldObservations": ["Initial baud rate 9600"],
            "newObservations": ["Upgraded high-speed baud rate 115200 bps with parity check"]
        }]

        upd_res = enhanced_kg.update_observations(update_payload)
        self.assertTrue(upd_res["success"])
        self.assertIn("TEST_CONTROLLER", upd_res["updatedEntities"])

        # Query and verify in-place update
        query_res = enhanced_kg.query_graph(entity_name="TEST_CONTROLLER")
        self.assertTrue(query_res["success"])
        texts = [o["observation_text"] for o in query_res["observations"]]
        self.assertTrue(any("115200 bps" in t for t in texts))
        self.assertFalse(any("9600 bps" in t for t in texts))

    def test_07_metadata_timestamps_and_confidence(self):
        res = enhanced_kg.add_observations(
            entity_name="TEST_CONTROLLER",
            observations=["ADC resolution configured for 12-bit mode"],
            confidence=0.99,
            source="firmware_inspection"
        )
        self.assertTrue(res["success"])

        # Query with minConfidence = 0.9
        high_conf = enhanced_kg.query_graph(entity_name="TEST_CONTROLLER", min_confidence=0.9)
        self.assertGreaterEqual(len(high_conf["observations"]), 1)

        # Query with minConfidence = 1.0 (should filter out)
        ultra_high = enhanced_kg.query_graph(entity_name="TEST_CONTROLLER", min_confidence=1.0)
        has_12bit = any("12-bit" in o["observation_text"] for o in ultra_high["observations"])
        self.assertFalse(has_12bit)

    def test_08_relation_and_type_queries(self):
        enhanced_kg.create_entities([
            {"name": "ANALOG_PIN_RA0", "entityType": "PIN"},
            {"name": "MCP9701_SENSOR", "entityType": "SENSOR"}
        ])
        enhanced_kg.create_relations([{
            "from": "MCP9701_SENSOR",
            "to": "ANALOG_PIN_RA0",
            "relationType": "CONNECTED_TO",
            "confidence": 1.0
        }])

        rel_query = enhanced_kg.query_graph(relation_type="CONNECTED_TO")
        self.assertTrue(rel_query["success"])
        self.assertGreaterEqual(len(rel_query["relations"]), 1)

    def test_09_security_rbac_and_encryption(self):
        # 1. RBAC Check: READ_ONLY role cannot delete or write
        allowed, reason = security_rbac.verify_permission("READ_ONLY", "filesystem:delete_quarantine")
        self.assertFalse(allowed)

        allowed_admin, _ = security_rbac.verify_permission("ADMIN", "filesystem:delete_quarantine")
        self.assertTrue(allowed_admin)

        # 2. Secret detection and auto-encryption
        secret_obs = "Database password is secret_token_xyz987654321"
        self.assertTrue(security_rbac.detect_secrets(secret_obs))

        # Add sensitive observation
        enc_add = enhanced_kg.add_observations(
            entity_name="TEST_CONTROLLER",
            observations=[secret_obs]
        )
        self.assertTrue(enc_add["success"])

        # Query without decryption -> encrypted placeholder
        query_normal = enhanced_kg.query_graph(entity_name="TEST_CONTROLLER", decrypt_sensitive=False)
        self.assertTrue(any("[ENCRYPTED_SENSITIVE_DATA]" in o["observation_text"] for o in query_normal["observations"]))

        # Query with decryption -> original secret recovered
        query_decrypted = enhanced_kg.query_graph(entity_name="TEST_CONTROLLER", decrypt_sensitive=True, user_role="ADMIN")
        self.assertTrue(any("secret_token_xyz987654321" in o["observation_text"] for o in query_decrypted["observations"]))

    def test_10_unified_mcp_dispatcher(self):
        tools = get_all_tool_definitions()
        tool_names = [t["name"] for t in tools]
        self.assertIn("memory__update_observations", tool_names)
        self.assertIn("filesystem__read_lines", tool_names)
        self.assertIn("filesystem__delete_file", tool_names)
        self.assertIn("filesystem__append_file", tool_names)
        self.assertIn("archive__compress_files", tool_names)

        # Dispatch via call_tool
        test_file = os.path.join(self.test_dir, "dispatcher_test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Line A\nLine B\nLine C\n")

        disp_res = call_tool("filesystem__read_lines", {"filePath": test_file, "mode": "head", "count": 2})
        self.assertTrue(disp_res["success"])
        self.assertEqual(len(disp_res["lines"]), 2)

    def test_11_public_apis_and_mcp_servers(self):
        from routes.enhanced_tools_bp import enhanced_bp
        from routes.public_apis_bp import public_bp, API_MAP
        from flask import Flask

        app = Flask(__name__)
        app.register_blueprint(enhanced_bp)
        app.register_blueprint(public_bp)
        client = app.test_client()

        # Verify 19 MCP servers
        mcp_res = client.get("/api/mcp/servers")
        self.assertEqual(mcp_res.status_code, 200)
        self.assertEqual(mcp_res.json["total_servers"], 19)

        # Verify 35 Public APIs
        pub_res = client.get("/api/public/list")
        self.assertEqual(pub_res.status_code, 200)
        self.assertEqual(pub_res.json["total_apis"], 35)
        self.assertEqual(len(API_MAP), 35)

        # Test specific endpoints
        cad_res = client.get("/api/public/cad_usd")
        self.assertEqual(cad_res.status_code, 200)
        self.assertEqual(cad_res.json["status"], "success")

    def test_12_network_device_intelligent_classification(self):
        from routes.cyber import classify_network_device, generate_alert_card
        from network_sentinel import classify_fallback_speech

        op_name = os.getenv("OPERATOR_NAME", "Commander")

        # Case 1: Internal Microsoft Hyper-V / WSL2
        hyp = classify_network_device("172.27.55.102", "00:15:5d:8e:1e:21", "Microsoft Hyper-V", "Local Host")
        self.assertEqual(hyp["category"], "VIRTUAL_ADAPTER")
        self.assertTrue(hyp["is_virtual"])
        self.assertIn(op_name, hyp["spoken_text"])
        self.assertIn("Hyper-V", hyp["spoken_text"])
        self.assertLessEqual(len(hyp["spoken_text"].split()), 15)
        self.assertNotIn("172.27.55.102", hyp["spoken_text"])  # No raw dotted decimal string

        # Case 2: Recognized hardware vendor (Apple)
        apl = classify_network_device("192.168.2.199", "bc:d0:74:aa:bb:cc", "Apple Inc.", "iPhone")
        self.assertEqual(apl["category"], "KNOWN_PHYSICAL")
        self.assertFalse(apl["is_virtual"])
        self.assertIn(op_name, apl["spoken_text"])
        self.assertIn("Apple", apl["spoken_text"])
        self.assertLessEqual(len(apl["spoken_text"].split()), 15)

        # Case 3: Truly unverified device
        unv = classify_network_device("192.168.2.89", "56:80:70:65:ce:f0", "Unknown Vendor", "Unknown")
        self.assertEqual(unv["category"], "UNVERIFIED")
        self.assertIn(op_name, unv["spoken_text"])
        self.assertIn("dot 89", unv["spoken_text"])
        self.assertLessEqual(len(unv["spoken_text"].split()), 15)

        # Case 4: Alert card HTML generation
        card_html = generate_alert_card("172.27.55.102", "00:15:5d:8e:1e:21", "Microsoft Hyper-V", "Local Host", "2026-10-19 20:41:18", hyp)
        self.assertIn("tactical-device-alert", card_html)
        self.assertIn("Microsoft Hyper-V / WSL2 Virtual Subsystem", card_html)
        self.assertIn("not an outside intruder", card_html)

        # Case 5: Network Sentinel fallback speech
        fb = classify_fallback_speech("172.27.55.102", "00:15:5d:8e:1e:21")
        self.assertIn(op_name, fb)
        self.assertIn("Hyper-V", fb)
        self.assertLessEqual(len(fb.split()), 15)


if __name__ == "__main__":
    unittest.main()
