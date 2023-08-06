import os

from utils.file.FileOrDirectory import FileOrDirectory

DIALECT = 'excel'
DELIMITER_CSV = ','
DELIMITER_TSV = '\t'
DELIM_LINE = '\n'
ENCODING = 'utf-8'


class File(FileOrDirectory):
    def delete(self):
        if self.exists:
            os.remove(self.path)

    @property
    def ext(self):
        return self.name.split('.')[-1]

    def read(self):
        with open(self.path, 'r', encoding=ENCODING) as fin:
            content = fin.read()
            fin.close()
        return content

    def readBinary(self):
        with open(self.path, 'rb') as fin:
            content = fin.read()
            fin.close()
        return content

    def write(self, content):
        with open(self.path, 'w', encoding=ENCODING) as fout:
            fout.write(content)
            fout.close()

    def writeBinary(self, content):
        with open(self.path, 'wb') as fout:
            fout.write(content)
            fout.close()

    def read_lines(self):
        content = File.read(self)
        return content.split(DELIM_LINE)

    def write_lines(self, lines):
        content = DELIM_LINE.join(lines)
        File.write(self, content)
