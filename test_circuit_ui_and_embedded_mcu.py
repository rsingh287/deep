"""
==============================================================================
Unit Test Suite: Circuit Breaker Matrix & Embedded MCU Toolchain Integration
==============================================================================
Validates:
1. Circuit Breaker fault injection & recovery endpoints (trip & reset).
2. Embedded MCU Toolchain discovery (xc8-cc, ipecmd, MPLABX projects).
3. Pre-flash hardware directive static audit on PIC18F85K22 firmware.
4. Microchip xc8-cc compiler execution with DFP pack producing valid HEX.
5. PICkit 3 USB mutex locking mechanics.
"""

import unittest
import json
import os
import app
import embedded_mcu_engine
from hystrix_circuit_breaker import global_circuit_registry, CircuitState


class TestCircuitUIAndEmbeddedMCU(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.app.test_client()

    def test_01_circuit_breaker_telemetry_endpoint(self):
        res = self.client.get('/api/system/circuit_breakers')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIsInstance(data['resilience_matrix'], list)
        breaker_names = [b['name'] for b in data['resilience_matrix']]
        self.assertIn('ollama_inference', breaker_names)
        self.assertIn('iot_smart_home', breaker_names)
        self.assertIn('vision_hardware', breaker_names)

    def test_02_circuit_breaker_trip_and_reset_endpoints(self):
        # 1. Trip to OPEN
        res_trip = self.client.post('/api/system/circuit_breakers/trip', json={'name': 'iot_smart_home'})
        self.assertEqual(res_trip.status_code, 200)
        data_trip = json.loads(res_trip.data.decode('utf-8'))
        self.assertTrue(data_trip['success'])
        self.assertEqual(data_trip['breaker']['state'], 'OPEN')

        # Verify breaker state in registry
        breaker = global_circuit_registry.get('iot_smart_home')
        self.assertIsNotNone(breaker)
        self.assertEqual(breaker.state, CircuitState.OPEN)

        # 2. Reset back to CLOSED
        res_reset = self.client.post('/api/system/circuit_breakers/reset', json={'name': 'iot_smart_home'})
        self.assertEqual(res_reset.status_code, 200)
        data_reset = json.loads(res_reset.data.decode('utf-8'))
        self.assertTrue(data_reset['success'])
        self.assertEqual(data_reset['breaker']['state'], 'CLOSED')
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_03_mcu_toolchain_status(self):
        res = self.client.get('/api/hardware/mcu/status')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['xc8_available'])
        self.assertTrue(data['ipecmd_available'])
        self.assertGreater(data['projects_count'], 0)

    def test_04_mcu_pre_flash_audit(self):
        res = self.client.post('/api/hardware/mcu/audit', json={'project': 'digital_lock.X'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['passed'])
        self.assertEqual(data['findings'], [])

    def test_05_mcu_compiler_execution(self):
        res = self.client.post('/api/hardware/mcu/compile', json={'project': 'digital_lock.X'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['hex_path'])
        self.assertTrue(os.path.isfile(data['hex_path']))
        self.assertGreater(data['hex_size_bytes'], 0)

    def test_06_pickit3_mutex_locking(self):
        # Acquire lock and verify double-acquire fails safely
        acquired = embedded_mcu_engine.PICKIT3_USB_MUTEX.acquire(blocking=False)
        self.assertTrue(acquired)
        try:
            # Second acquire should fail immediately without deadlock
            second_try = embedded_mcu_engine.PICKIT3_USB_MUTEX.acquire(blocking=False)
            self.assertFalse(second_try)
        finally:
            embedded_mcu_engine.PICKIT3_USB_MUTEX.release()


if __name__ == '__main__':
    unittest.main()
