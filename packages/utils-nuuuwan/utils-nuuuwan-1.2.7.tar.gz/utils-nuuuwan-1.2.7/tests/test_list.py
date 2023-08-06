from unittest import TestCase

from utils.List import List

TEST_LIST_RAW = ['a', 'b', 'c', 'd']
TEST_LIST = List(TEST_LIST_RAW)


class TestList(TestCase):
    def test_init(self):
        self.assertEqual(TEST_LIST.tolist(), TEST_LIST_RAW)
        x = List()
        self.assertEqual(x.tolist(), [])

    def test_len(self):
        self.assertEqual(len(TEST_LIST), len(TEST_LIST_RAW))

    def test_getitem(self):
        for idx in range(len(TEST_LIST_RAW)):
            self.assertEqual(TEST_LIST[idx], TEST_LIST_RAW[idx])

    def test_setitem(self):
        x = List([1, 2])
        x[0] = 11
        x[1] = 22
        self.assertEqual(x.tolist(), [11, 22])

    def test_eq(self):
        self.assertEqual(TEST_LIST, TEST_LIST_RAW)
        self.assertEqual(TEST_LIST, List(TEST_LIST_RAW))
        self.assertNotEqual(TEST_LIST, "List")

    def test_str(self):
        self.assertEqual(str(TEST_LIST), str(TEST_LIST_RAW))

    def test_repr(self):
        self.assertEqual(repr(TEST_LIST), repr(TEST_LIST_RAW))

    def test_add(self):
        self.assertEqual(List([1, 2]) + List([3, 4]), List([1, 2, 3, 4]))

    def test_flatten(self):
        self.assertEqual(List([[1, 2], [3, 4]]).flatten(), List([1, 2, 3, 4]))
        with self.assertRaises(TypeError):
            List([[1, 2], 3]).flatten()

    def test_unique(self):
        self.assertEqual(List([1, 2, 3, 2]).unique(), List([1, 2, 3]))

    def test_iter(self):
        for item in TEST_LIST:
            self.assertIn(item, TEST_LIST_RAW)
