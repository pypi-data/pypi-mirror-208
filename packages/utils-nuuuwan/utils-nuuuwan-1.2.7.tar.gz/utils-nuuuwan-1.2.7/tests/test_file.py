import os
import tempfile
import unittest
from urllib.parse import urljoin

from utils import CSVFile, File, JSONFile, TSVFile, XSVFile
from utils.www import WWW

TEST_DATA_LIST = [
    {'name': 'Alpha', 'age': '1'},
    {'name': 'Bravo', 'age': '2'},
]

TEST_DATA_ITEM_LIST = [
    True,
    1234,
    1234.5678,
    '1234',
    [1, 2, 3, 'test'],
    {'test': 123},
    TEST_DATA_LIST,
]


class TestFile(unittest.TestCase):
    def test_eq(self):
        file1 = File(
            tempfile.NamedTemporaryFile(prefix="test1.", suffix=".txt").name
        )
        file2 = File(
            tempfile.NamedTemporaryFile(prefix="test2.", suffix=".txt").name
        )
        self.assertEqual(file1, file1)
        self.assertNotEqual(file1, file2)
        self.assertNotEqual(file1, 'file2')

    def test_read_and_write(self):
        """Test."""
        content = 'Hello' * 100
        file = File(
            tempfile.NamedTemporaryFile(
                prefix="utils.test_file.", suffix=".txt"
            ).name
        )
        file.write(content)
        content2 = file.read()
        self.assertEqual(content, content2)
        self.assertEqual(file.ext, 'txt')

        lines = [f'Hello {i}' for i in range(0, 100)]
        file.write_lines(lines)
        lines2 = file.read_lines()
        self.assertEqual(lines, lines2)

    def test_json_read_and_write(self):
        for data in TEST_DATA_ITEM_LIST:
            json_file = JSONFile(
                tempfile.NamedTemporaryFile(
                    prefix="utils.test_file.", suffix=".json"
                ).name
            )
            json_file.write(data)
            data2 = json_file.read()
            self.assertEqual(data, data2)

    def test_xsv_delimiter(self):
        xsv_file = XSVFile('')
        with self.assertRaises(NotImplementedError) as _:
            xsv_file.delimiter

    def test_xsv_read_helper(self):
        delimiter = ' '
        xsv_lines = ['a b c', '1 2 3']
        data_list = XSVFile._readHelper(delimiter, xsv_lines)
        expected_data_list = [{'a': '1', 'b': '2', 'c': '3'}]
        self.assertEqual(expected_data_list, data_list)

    def test_csv_delimiter(self):
        csv_file = CSVFile('')
        self.assertEqual(csv_file.delimiter, ',')

    def test_csv_read_and_write(self):
        csv_file = CSVFile(
            tempfile.NamedTemporaryFile(
                prefix="utils_test_file.", suffix=".csv"
            ).name
        )
        csv_file.write(TEST_DATA_LIST)
        data_list = csv_file.read()
        self.assertEqual(TEST_DATA_LIST, data_list)

    def test_tsv_read_and_write(self):
        tsv_file = TSVFile(
            tempfile.NamedTemporaryFile(
                prefix="utils_test_file.", suffix=".tsv"
            ).name
        )
        tsv_file.write(TEST_DATA_LIST)
        data_list = tsv_file.read()
        self.assertEqual(TEST_DATA_LIST, data_list)

    def test_tsv_read_and_write_custom(self):
        URL_SUMMARY = urljoin(
            'https://raw.githubusercontent.com',
            'nuuuwan/news_lk3_data/main/reports/summary.tsv',
        )
        tmp_file = WWW(URL_SUMMARY).download()
        d_list = TSVFile(tmp_file).read()
        tsv_file = TSVFile(
            tempfile.NamedTemporaryFile(
                prefix="utils_test_file.", suffix=".tsv"
            ).name
        )
        tsv_file.write(d_list)
        data_list2 = tsv_file.read()
        self.assertEqual(d_list, data_list2)

    def write_test_json_file(self):
        json_file_name = tempfile.NamedTemporaryFile(
            prefix="utils.test_zip_read_and_write.", suffix=".json"
        ).name
        data = [i for i in range(0, 1_000)]
        json_file = JSONFile(json_file_name)
        json_file.write(data)
        json_file_size = os.path.getsize(json_file_name)
        expected_json_file_size = 6_892
        self.assertEqual(expected_json_file_size, json_file_size)
        return json_file_name, json_file, data


if __name__ == '__main__':
    unittest.main()
