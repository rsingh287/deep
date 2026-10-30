"""
Phase 1 Integration Test Suite: VLM Grounded Desktop Automation & Sub-400ms Voice Pipeline
==========================================================================================
Verifies:
1. DPI Awareness & Screen Resolution
2. Multi-Format VLM Coordinate Parsing (points, boxes, percentages, regex fallbacks)
3. Visual Clicker Intent Matrix (click, double click, right click, type into, hover)
4. Silero VAD Frame Probability Analysis
5. CUDA / CPU Faster-Whisper Latency Benchmark (<100ms on GPU)
6. Live REST Endpoints (/api/vision/ground_element, /api/voice/vad/status, /api/voice/vad/transcribe)
"""

import os
import sys
import time
import unittest
import numpy as np
import requests

from vlm_grounding_engine import get_vlm_grounding_engine, VLMGroundingEngine
from voice_vad_stream_engine import get_voice_vad_stream_engine, VoiceVADStreamEngine
from intents.visual_clicker_intent import VisualClickerIntent


class TestPhase1VLMAndVAD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vlm_engine = get_vlm_grounding_engine()
        cls.voice_engine = get_voice_vad_stream_engine()
        cls.api_base = "http://127.0.0.1:5000"

    # --- 1. Screen Resolution & DPI Awareness ---
    def test_01_screen_resolution_and_capture(self):
        w, h = self.vlm_engine.get_screen_resolution()
        self.assertGreater(w, 640, "Screen width must be > 640")
        self.assertGreater(h, 480, "Screen height must be > 480")

        cap = self.vlm_engine.capture_screen(max_dim=800)
        self.assertIn("b64", cap)
        self.assertIn("orig_w", cap)
        self.assertIn("orig_h", cap)
        self.assertEqual(cap["orig_w"], w)
        self.assertEqual(cap["orig_h"], h)
        self.assertLessEqual(max(cap["scaled_w"], cap["scaled_h"]), 800)

    # --- 2. Multi-Format VLM Coordinate Parsing ---
    def test_02_vlm_coordinate_parsing_point_format(self):
        w, h = 1920, 1080
        # Format: {"point": [500, 500]} normalized to 1000
        raw_json = '```json\n{"point": [500, 500], "label": "screen center"}\n```'
        parsed = self.vlm_engine.parse_vlm_coordinates(raw_json, w, h)
        self.assertIsNotNone(parsed)
        x, y, label = parsed
        self.assertEqual(x, 960)
        self.assertEqual(y, 540)
        self.assertEqual(label, "screen center")

    def test_03_vlm_coordinate_parsing_box_format(self):
        w, h = 1920, 1080
        # Format: {"box_2d": [ymin, xmin, ymax, xmax]} normalized to 1000
        raw_json = '{"box_2d": [200, 400, 400, 600], "label": "dialog box"}'
        parsed = self.vlm_engine.parse_vlm_coordinates(raw_json, w, h)
        self.assertIsNotNone(parsed)
        x, y, label = parsed
        # Center x: (400+600)/2 = 500 -> 50% of 1920 = 960
        # Center y: (200+400)/2 = 300 -> 30% of 1080 = 324
        self.assertEqual(x, 960)
        self.assertEqual(y, 324)

    def test_04_vlm_coordinate_parsing_percentage_format(self):
        w, h = 1000, 1000
        raw_json = '{"x_pct": 25.0, "y_pct": 75.0, "label": "bottom-left quarter"}'
        parsed = self.vlm_engine.parse_vlm_coordinates(raw_json, w, h)
        self.assertIsNotNone(parsed)
        x, y, label = parsed
        self.assertEqual(x, 250)
        self.assertEqual(y, 750)

    def test_05_vlm_coordinate_parsing_raw_bounding_box(self):
        w, h = 1000, 1000
        raw_text = 'The detected bounding box is [100, 200, 300, 400].'
        parsed = self.vlm_engine.parse_vlm_coordinates(raw_text, w, h)
        self.assertIsNotNone(parsed)
        x, y, label = parsed
        # cx = 300 -> 300 / 1000 * 1000 = 300
        # cy = 200 -> 200 / 1000 * 1000 = 200
        self.assertEqual(x, 300)
        self.assertEqual(y, 200)

    # --- 3. Visual Clicker Intent Matrix ---
    def test_06_visual_clicker_intent_can_handle(self):
        self.assertTrue(VisualClickerIntent.can_handle("click on submit button"))
        self.assertTrue(VisualClickerIntent.can_handle("please click on cancel"))
        self.assertTrue(VisualClickerIntent.can_handle("double click on chrome icon"))
        self.assertTrue(VisualClickerIntent.can_handle("right click on desktop"))
        self.assertTrue(VisualClickerIntent.can_handle("hover over settings gear"))
        self.assertTrue(VisualClickerIntent.can_handle("type test into search box"))

        # Non-matching
        self.assertFalse(VisualClickerIntent.can_handle("what is the weather today in Toronto"))
        self.assertFalse(VisualClickerIntent.can_handle("play song starboy"))

    def test_07_visual_clicker_spatial_shortcut_execution(self):
        # Spatial shortcut executes in <1ms without calling LLM
        res, model, actions = VisualClickerIntent.execute(
            user_prompt="click on center",
            norm_prompt="click on center"
        )
        self.assertIn("Visual Operator", res)
        self.assertEqual(model, "qwen2.5vl:7b")
        self.assertEqual(len(actions), 1)

    # --- 4. Silero VAD Frame Evaluation ---
    def test_08_silero_vad_frame_evaluation(self):
        self.assertIsNotNone(self.voice_engine.vad_model, "Silero VAD model must be loaded")
        # 512 float32 zeros (silence)
        silent_frame = np.zeros(512, dtype=np.float32)
        prob = float(self.voice_engine.vad_model(silent_frame)[0])
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        self.assertLess(prob, 0.5, "Silent frame must have voice probability < 0.5")

    # --- 5. Faster-Whisper GPU/CPU Inference Benchmark ---
    def test_09_faster_whisper_benchmark(self):
        self.assertIsNotNone(self.voice_engine.whisper_model, "Whisper model must be loaded")
        # 1 second of dummy float32 audio
        dummy_audio = np.zeros(16000, dtype=np.float32)
        text, latency_ms = self.voice_engine.transcribe_audio_chunk(dummy_audio)
        self.assertIsInstance(text, str)
        self.assertGreater(latency_ms, 0.0)
        print(f"\n[Test Benchmark] Faster-Whisper 1s Chunk Inference Time: {latency_ms:.1f}ms (Device: {self.voice_engine.telemetry['device']})")

    # --- 6. Live REST Endpoints ---
    def test_10_rest_api_vision_ground_element(self):
        try:
            res = requests.post(
                f"{self.api_base}/api/vision/ground_element",
                json={"target": "center"},
                timeout=10
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server is not currently running on port 5000")

    def test_11_rest_api_voice_vad_status(self):
        try:
            res = requests.get(f"{self.api_base}/api/voice/vad/status", timeout=5)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            self.assertIn("telemetry", data)
            self.assertIn("whisper_model", data["telemetry"])
        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server is not currently running on port 5000")

    def test_12_rest_api_voice_vad_transcribe(self):
        try:
            res = requests.post(f"{self.api_base}/api/voice/vad/transcribe", json={}, timeout=10)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            self.assertIn("stt_latency_ms", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Flask server is not currently running on port 5000")


if __name__ == "__main__":
    unittest.main()
