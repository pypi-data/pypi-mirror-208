import os

from utils.file.File import File
from utils.file.FileOrDirectory import FileOrDirectory


class Directory(FileOrDirectory):
    @staticmethod
    def isIgnore(path: str):
        for k in ['__pycache__', '.git']:
            if k in path:
                return True
        return False

    def mkdir(self):
        os.mkdir(self.path)

    @property
    def children(self):
        _children = []
        for name in os.listdir(self.path):
            path = os.path.join(self.path, name)
            if Directory.isIgnore(path):
                continue

            if os.path.isdir(path):
                _children.append(Directory(path))
            else:
                _children.append(File(path))
        return sorted(_children, key=lambda x: x.name)
