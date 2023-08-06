import os
import unittest

from utils import WWW, CSVFile, File, JSONFile, TSVFile

DIR_TESTS = 'tests'


URL_BASE = '/'.join(
    [
        'https://raw.githubusercontent.com',
        'nuuuwan/utils',
        'main/tests',
    ]
)

URL_HTML = 'https://nuuuwan.github.io/utils/index.html'


def get_test_file(ext: str) -> str:
    return os.path.join(DIR_TESTS, f'data.{ext}')


def strip_html(html):
    return html.replace('\t', '').replace('\n', '').replace(' ', '')


def get_test_url(ext: str) -> str:
    if ext == 'html':
        return URL_HTML
    return f'{URL_BASE}/data.{ext}'


def cleanup_local_files():
    pass


class TestWWW(unittest.TestCase):
    def test_download_html(self):
        cleanup_local_files()
        for _ in range(2):
            self.assertEqual(
                strip_html(File(get_test_file('html')).read()),
                strip_html(WWW(get_test_url('html')).read()),
            )

    def test_download_binary(self):
        cleanup_local_files()
        self.assertEqual(
            File(get_test_file('png')).readBinary(),
            WWW(get_test_url('png')).read(),
        )

    def test_read(self):
        cleanup_local_files()
        self.assertEqual(
            File(get_test_file('txt')).read(),
            WWW(get_test_url('txt')).read(),
        )

    def test_exists(self):
        cleanup_local_files()
        url = get_test_url('png')
        self.assertTrue(WWW(url).exists)
        self.assertFalse(WWW(url + '.1234').exists)

    def test_children(self):
        cleanup_local_files()
        url = 'https://www.python.org/'
        children = WWW(url).children
        self.assertGreater(len(children), 0)
        print(children[0].url)
        self.assertIn(children[0].url, '#')

    # ----------------------------
    # To Deprecate
    # ----------------------------

    def test_read_json(self):
        cleanup_local_files()
        self.assertEqual(
            JSONFile(get_test_file('json')).read(),
            WWW(get_test_url('json')).readJSON(),
        )

    def test_read_tsv(self):
        cleanup_local_files()
        self.assertEqual(
            TSVFile(get_test_file('tsv')).read(),
            WWW(get_test_url('tsv')).readTSV(),
        )

    def test_read_csv(self):
        cleanup_local_files()
        self.assertEqual(
            CSVFile(get_test_file('csv')).read(),
            WWW(get_test_url('csv')).readCSV(),
        )

    def test_read_binary(self):
        cleanup_local_files()
        self.assertEqual(
            File(get_test_file('png')).readBinary(),
            WWW(get_test_url('png')).readBinary(),
        )

        with self.assertRaises(Exception):
            WWW(get_test_url('png') + '.1234').readBinary()

    def test_read_selenium(self):
        cleanup_local_files()
        content = WWW(get_test_url('html')).readSelenium()
        self.assertIn(
            'This is a test',
            content,
        )
