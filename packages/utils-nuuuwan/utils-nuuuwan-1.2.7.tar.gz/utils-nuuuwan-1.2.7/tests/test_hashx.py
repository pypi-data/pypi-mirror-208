"""Tests for hashx"""

import unittest

from utils import hashx


class TestHashx(unittest.TestCase):
    """Tests."""

    def test_md5(self):
        """Test."""
        self.assertEqual(
            'fc3ff98e8c6a0d3087d515c0473f8677',
            hashx.md5('hello world!'),
        )


if __name__ == '__main__':
    unittest.main()
