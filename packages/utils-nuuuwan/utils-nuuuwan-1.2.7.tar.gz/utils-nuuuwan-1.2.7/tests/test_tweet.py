from unittest import TestCase

from utils import Tweet


class TestTweet(TestCase):
    def test_init(self):
        self.assertIsNotNone(Tweet('test'))
