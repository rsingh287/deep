import unittest
from dynamic_tools.v4_test_fx_client import run

class TestV4TestFxClient(unittest.TestCase):
    def test_invalid_input(self):
        res = run("not_a_dict")
        self.assertFalse(res.get("success", False))

    def test_valid_call_structure(self):
        res = run({})
        self.assertIn("url", res)

if __name__ == "__main__":
    unittest.main()
