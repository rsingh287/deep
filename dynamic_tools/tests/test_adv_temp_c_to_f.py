import unittest
from dynamic_tools.adv_temp_c_to_f import run

class TestTemp(unittest.TestCase):
    def test_boil(self):
        res = run({"celsius": 100})
        self.assertEqual(res.get("fahrenheit"), 212.0)

    def test_freeze(self):
        res = run({"celsius": 0})
        self.assertEqual(res.get("fahrenheit"), 32.0)

if __name__ == "__main__":
    unittest.main()
