from unittest import TestCase

from utils.List import List


class TestIter(TestCase):
    def test_count_list1(self):
        x = List(
            [
                'Nuwan Senaratna',
                'Nuwan Silva',
                'Nuwan de Silva',
                'Albert Einstein',
                'Albert Perera',
                'Barbie Perera',
            ]
        )

        def func_key(x):
            return x.split(' ')[0]

        self.assertEqual(
            x.count(func_key),
            {'Nuwan': 3, 'Albert': 2, 'Barbie': 1},
        )

    def test_count_list2(self):
        x = List([1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4])
        self.assertEqual(x.count(), {1: 2, 2: 3, 3: 4, 4: 3})

    def test_count_list3(self):
        int_list = [(i + 1) for i in range(0, 10000)]
        x = List(int_list)

        def func_key(i):
            return i % 3

        self.assertEqual(x.count(func_key), {0: 3333, 1: 3334, 2: 3333})
