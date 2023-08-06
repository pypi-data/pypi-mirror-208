import os
from unittest import TestCase

from utils import PDFFile

TEST_PDF_FILE = PDFFile(os.path.join('tests', 'example.pdf'))


class TestPDFFile(TestCase):
    def test_n_pages(self):
        self.assertEqual(TEST_PDF_FILE.n_pages, 16)
