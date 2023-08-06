"""Test."""
import unittest

from utils.String import String

SNAKE_AND_CAMEL_EXAMPLES = [
    ['this_is_a_test', 'ThisIsATest'],
    ['123', '123'],
    ['123_testing123', '123Testing123'],
]


class TestDT(unittest.TestCase):
    def test_float(self):
        for [input, expected_output] in [
            ['0', 0],
            ['123', 123],
            ['123abc', None],
            ['123.456', 123.456],
        ]:
            self.assertEqual(
                String(input).float,
                expected_output,
            )

    def test_int(self):
        for [input, expected_output] in [
            ['0', 0],
            ['123', 123],
            ['123abc', None],
            ['123.456', 123],
        ]:
            self.assertEqual(
                String(input).int,
                expected_output,
            )

    def test_snake(self):
        for [input, expected_output] in [
            ['This is a test', 'this_is_a_test'],
            ['123', '123'],
            ['123 Testing 123', '123_testing_123'],
        ]:
            self.assertEqual(
                String(input).snake,
                expected_output,
            )

    def test_kebab(self):
        for [input, expected_output] in [
            ['This is a test', 'this-is-a-test'],
            ['123', '123'],
            ['123 Testing 123', '123-testing-123'],
        ]:
            self.assertEqual(
                String(input).kebab,
                expected_output,
            )

    def test_camel(self):
        for [input, expected_output] in [
            ['This is a test', 'ThisIsATest'],
            ['123', '123'],
            ['123 Testing 123', '123Testing123'],
        ]:
            self.assertEqual(
                String(input).camel,
                expected_output,
            )

    def test_str_and_repr(self):
        for input in [
            'This is a test',
            '123',
            '123 Testing 123',
        ]:
            self.assertEqual(
                str(String(input)),
                input,
            )
            self.assertEqual(
                repr(String(input)),
                input,
            )
