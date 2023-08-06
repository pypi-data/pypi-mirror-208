import os
from unittest import TestCase

from utils import Directory, File


class TestDirectory(TestCase):
    def test_init(self):
        dir_tests = Directory(os.path.join('src', 'utils'))
        self.assertEqual(dir_tests.path, os.path.join('src', 'utils'))
        self.assertEqual(dir_tests.name, 'utils')
        self.assertEqual(
            dir_tests.children[0],
            File(os.path.join('src', 'utils', 'Browser.py')),
        )

        self.assertEqual(dir_tests, Directory(os.path.join('src', 'utils')))
