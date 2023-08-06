import os


class FileOrDirectory:
    def __init__(self, path):
        self.path = path

    @property
    def name(self):
        return self.path.split(os.sep)[-1]

    @property
    def exists(self):
        return os.path.exists(self.path)

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.path == other.path
        return False
