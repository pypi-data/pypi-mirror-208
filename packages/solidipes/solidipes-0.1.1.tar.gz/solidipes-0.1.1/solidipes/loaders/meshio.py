import meshio

from .. import viewers
from .file import File


class Meshio(File):
    """File loaded with meshio"""

    def __init__(self, path):
        super().__init__(path)
        self.add("mesh")
        self.default_viewer = viewers.PyvistaPlotter

    def _load_data(self, key):
        return meshio.read(self.file_info.path)
