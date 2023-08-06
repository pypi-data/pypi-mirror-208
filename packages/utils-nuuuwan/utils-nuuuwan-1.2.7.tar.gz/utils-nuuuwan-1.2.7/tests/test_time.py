import time
from unittest import TestCase

from utils import (TIMEZONE_OFFSET, Time, TimeDelta, TimeFormat, TimeUnit,
                   get_date_id, get_time_id)


class TestTime(TestCase):
    def test_init(self):
        ut = 1234567890
        t = Time(ut)
        self.assertEqual(t.ut, ut)

    def test_now(self):
        t = Time.now()
        ut = time.time()
        self.assertGreater(t.ut, ut - 10)
        self.assertGreater(ut + 10, t.ut)

        with self.assertRaises(TypeError):
            t + 1

    def test_sub(self):
        t0 = Time(1234567800)
        t1 = Time(1234567890)
        dut10 = TimeDelta(90)

        self.assertEqual(t1 - t0, dut10)
        self.assertEqual(t1 - dut10, t0)

        with self.assertRaises(TypeError):
            t0 - 1

    def test_add(self):
        t0 = Time(1234567800)
        dt = TimeDelta(100)
        t1 = Time(1234567900)
        self.assertEqual(t0 + dt, t1)

    def test_delta_humanize(self):
        for dut, expected_humanized in [
            [0, '0 seconds'],
            [1, '1 second'],
            [60, '1 minute'],
            [120, '2 minutes'],
            [3_600, '1 hour'],
            [86_400, '1 day'],
        ]:
            self.assertEqual(TimeDelta(dut).humanize(), expected_humanized)

    def test_format_stringify(self):
        t = Time(1234567890)
        for format_str, expected_time_str, ut2 in [
            ['%Y-%m-%d', '2009-02-14', 1234549800],
            ['%Y-%m-%d %H:%M', '2009-02-14 05:01', 1234567860],
            ['%Y-%m-%d %H:%M:%S', '2009-02-14 05:01:30', 1234567890],
        ]:
            tf = TimeFormat(format_str, TIMEZONE_OFFSET.LK)
            self.assertEqual(
                expected_time_str,
                tf.stringify(t),
            )

            t2 = Time(ut2)
            self.assertEqual(
                t2,
                tf.parse(expected_time_str),
            )

    def test_time_id(self):
        time_id = get_time_id()
        self.assertEqual(len(time_id), 15)

    def test_date_id(self):
        date_id = get_date_id()
        self.assertEqual(len(date_id), 8)

    def test_time_unit_truediv(self):
        self.assertEqual(TimeUnit(1) / 2, TimeUnit(0.5))
        self.assertEqual(TimeUnit(1) / TimeUnit(0.5), 2.0)

        with self.assertRaises(TypeError):
            2 / TimeUnit(2)

    def test_time_unit_mul(self):
        self.assertEqual(TimeUnit(1) * 2, TimeUnit(2))

    def test_time_unit_eq(self):
        self.assertEqual(TimeUnit(1) * 2, TimeUnit(2))
        self.assertNotEqual(TimeUnit(1) * 2, TimeUnit(3))
        self.assertNotEqual(TimeUnit(1) * 2, 2)
