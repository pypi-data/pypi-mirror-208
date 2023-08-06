import time
from unittest import TestCase

from utils import FiledVariable

MAX_N = 1_000_000
VALUE = (MAX_N) * (MAX_N - 1) // 2


def func_get():
    s = 0
    for i in range(MAX_N):
        s += i
    return s


class TestFiledVariable(TestCase):
    def test_cache_key(self):
        fv = FiledVariable('test_key', None)
        self.assertEqual(fv.cache_key, '8c32d1183251df9828f929b935ae0419')

    def test_cache_get(self):
        fvar = FiledVariable('test_key', func_get)
        fvar.clear_file()
        fvar.clear_cache()
        self.assertEqual(fvar.key, 'test_key')
        self.assertEqual(fvar.value, VALUE)

        t0 = time.time()
        self.assertEqual(fvar.value, VALUE)
        dt = time.time() - t0
        self.assertLess(dt, 0.001)

    def test_file_get(self):
        fvar = FiledVariable('test_key', func_get)
        fvar.clear_cache()
        self.assertEqual(fvar.value, VALUE)
