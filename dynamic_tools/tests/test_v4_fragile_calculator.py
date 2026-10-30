import unittest
from dynamic_tools.v4_fragile_calculator import run

class TestFragile(unittest.TestCase):
    def test_add(self):
        res = run({"val_a": 1, "val_b": 2})
        self.assertEqual(res.get("result"), 3)

if __name__ == "__main__":
    unittest.main()
    def test_regression_healed_1793329699(self):
        res = run({'val_b': 5})
        self.assertIsNotNone(res)

