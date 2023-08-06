import os
from functools import cached_property

import camelot
import PyPDF2

from utils.file.Directory import Directory
from utils.file.File import File


class PDFFile(File):
    @cached_property
    def n_pages(self):
        file = open(self.path, 'rb')
        reader = PyPDF2.PdfFileReader(file)
        return reader.numPages

    @property
    def dir_tables(self):
        return Directory(self.path + '.tables')

    def load_table_files(self):
        return self.dir_tables.children

    def store_table_files(self):
        os.makedirs(self.dir_tables.path)
        tables = camelot.read_pdf(self.path, pages='all')
        table_files = []
        for i, table in enumerate(tables):
            table_path = os.path.join(self.dir_tables.path, f'{i}.tsv')
            table.to_csv(table_path, sep='\t')
            table_files.append(File(table_path))
        return table_files

    @property
    def table_files(self):
        if self.dir_tables.exists:
            return self.load_table_files()
        return self.store_table_files()
