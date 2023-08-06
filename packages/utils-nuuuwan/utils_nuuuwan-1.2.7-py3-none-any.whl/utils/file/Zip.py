import os
import zipfile


class Zip:
    def __init__(self, path):
        self.path = path

    @property
    def zip_path(self):
        return self.path + '.zip'

    @property
    def arc_name(self):
        return os.path.basename(os.path.normpath(self.path))

    @property
    def dir_zip(self):
        return os.path.dirname(os.path.normpath(self.path))

    def zip(self, skip_delete=False):
        assert os.path.exists(self.path)
        with zipfile.ZipFile(
            self.zip_path,
            mode='w',
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            zip_file.write(self.path, arcname=self.arc_name)
            assert os.path.exists(self.zip_path)

        if not skip_delete:
            os.remove(self.path)
            assert not os.path.exists(self.path)

    def unzip(self, skip_delete=False):
        assert os.path.exists(self.zip_path)
        with zipfile.ZipFile(self.zip_path) as zip_file:
            zip_file.extractall(self.dir_zip)
            assert os.path.exists(self.path)

        if not skip_delete:
            os.remove(self.zip_path)
            assert not os.path.exists(self.zip_path)
