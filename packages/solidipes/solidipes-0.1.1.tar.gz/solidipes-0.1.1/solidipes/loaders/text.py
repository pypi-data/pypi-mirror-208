from .. import viewers
from .file import File


class Text(File):
    """Text file, potentially formatted with markdown"""

    supported_mime_types = ["text/plain"]
    supported_file_extensions = ["txt"]

    def __init__(self, path):
        super().__init__(path)
        self.add("text")
        self.default_viewer = viewers.Text

    def _load_data(self, key):
        """Read full text file"""
        text = ""
        with open(self.file_info.path, "r") as f:
            text = f.read()
        return text


class Markdown(Text):
    """Markdown file"""

    supported_mime_types = ["text/markdown"]
    supported_file_extensions = ["md"]

    def __init__(self, path):
        super().__init__(path)
        self.add("text")
        self.default_viewer = viewers.MarkdownViewer
