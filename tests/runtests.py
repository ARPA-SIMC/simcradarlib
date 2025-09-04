import unittest


# This is a unittest example. It can be used as a template for concrete tests and it prevents unittest.test to exit with
# status 5 (no test run).
class TestExample(unittest.TestCase):
    def test_example(self):
        self.assertEqual(1, 1, "1 = 1")


if __name__ == '__main__':
    unittest.main()
