import random
from unittest import TestCase

from utils import Color

random.seed(0)


class TestColor(TestCase):
    def test_static_helpers(self):
        self.assertEqual(Color._8bit(), 48)
        self.assertEqual(Color._4bit_hex(), '8')
        self.assertEqual(Color._8bit_hex(), '49')
        self.assertEqual(Color._360(), 50)
        self.assertAlmostEqual(Color._float(), 0.7298317482601286)
        self.assertEqual(Color._percent(), 87)

    def test_rgba(self):
        self.assertEqual(Color.rgba(), 'rgba(111,71,144,0.14)')
        self.assertEqual(Color.rgba(12, 34, 56, 0.78), 'rgba(12,34,56,0.78)')

    def test_hsla(self):
        self.assertEqual(Color.hsla(), 'hsla(155,61%,45%,0.58)')
        self.assertEqual(
            Color.hsla(123, 45, 67, 0.89), 'hsla(123,45%,67%,0.89)'
        )

    def test_hex(self):
        self.assertEqual(Color.hex(), '#cd18fc')
