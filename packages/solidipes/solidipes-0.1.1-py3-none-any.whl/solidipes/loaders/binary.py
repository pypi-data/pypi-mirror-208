from datasize import DataSize

from .. import viewers
from .file import File


class Binary(File):
    """File of unsupported type"""

    def __init__(self, path):
        super().__init__(path)
        self.add("metadata")
        self.default_viewer = viewers.Binary

    def _load_data(self, key):
        """Put metadata in a Text data object"""
        text = ""

        if self.file_info.type is not None:
            text += f"File type: {self.file_info.type}\n"

        text += f"File size: {DataSize(self.file_info.size):.2a}"
        return text
