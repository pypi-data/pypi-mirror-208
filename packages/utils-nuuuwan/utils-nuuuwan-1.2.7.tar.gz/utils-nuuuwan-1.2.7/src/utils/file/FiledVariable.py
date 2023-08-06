import tempfile

from utils import hashx
from utils.file.JSONFile import JSONFile

FILE_VARIABLE_CACHE = {}


class FiledVariable:
    def __init__(self, key: str, func_get):
        self.key = key
        self.func_get = func_get

    @property
    def cache_key(self):
        return hashx.md5(self.key)

    @property
    def file_path(self):
        return tempfile.NamedTemporaryFile(
            prefix="cache.", suffix=".json"
        ).name

    @property
    def file(self):
        return JSONFile(self.file_path)

    def clear_file(self):
        self.file.delete()

    def clear_cache(self):
        global FILE_VARIABLE_CACHE
        FILE_VARIABLE_CACHE = {}

    @property
    def value(self):
        global FILE_VARIABLE_CACHE
        if self.cache_key in FILE_VARIABLE_CACHE:
            return FILE_VARIABLE_CACHE[self.cache_key]

        if self.file.exists:
            return self.file.read()

        value = self.func_get()
        self.file.write(value)
        FILE_VARIABLE_CACHE[self.cache_key] = value
        return value
