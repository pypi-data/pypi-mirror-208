"""Test."""
import random
import unittest

from utils.Color import Color


class TestColorX(unittest.TestCase):
    """Test."""

    def test_8bit(self):
        random.seed(0)
        self.assertEqual(Color._8bit(), 197)

    def test_360(self):
        random.seed(0)
        self.assertAlmostEqual(Color._360(), 197)

    def test_float(self):
        random.seed(0)
        self.assertAlmostEqual(Color._float(), 0.8444218515250481)

    def test_percent(self):
        random.seed(0)
        self.assertAlmostEqual(Color._percent(), 49)

    def test_rgb(self):
        random.seed(0)
        self.assertEqual(Color.rgba(), 'rgba(197,215,20,0.26)')

    def test_hsla(self):
        random.seed(0)
        self.assertEqual(Color.hsla(), 'hsla(197,97%,53%,0.04)')
