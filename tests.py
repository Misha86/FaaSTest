"""Module with tests for FaaS."""
import unittest


class TestFaaS(unittest.TestCase):
    """Tests for FaaS."""

    def test_for_test(self):
        """Test for test."""
        self.assertEqual(2 + 2, 4)


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run()
