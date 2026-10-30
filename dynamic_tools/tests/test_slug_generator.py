from dynamic_tools.slug_generator import *
import unittest

class TestSlugGenerator(unittest.TestCase):
    def test_slug_generator(self):
        self.assertEqual(slug_generator('Hello World'), 'hello-world')
        self.assertEqual(slug_generator('Python 3.8'), 'python-3-8')
        self.assertEqual(slug_generator('  Leading and trailing spaces  '), 'leading-and-trailing-spaces')
        self.assertEqual(slug_generator('Special_Characters!@#$%^&*()'), 'special-characters')
        self.assertEqual(slug_generator(''), '')

if __name__ == '__main__':
    unittest.main()
