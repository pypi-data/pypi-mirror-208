from PIL import Image as PILImage

from .. import viewers
from .file import File


class Image(File):
    """Image loaded with PIL"""

    supported_mime_types = ["image/"]

    def __init__(self, path):
        super().__init__(path)

        self.add("image")
        self.default_viewer = viewers.Image

    def _load_data(self, key):
        """Load image data with PIL"""
        if self.file_info.type == "image/svg+xml":
            import tempfile

            from reportlab.graphics import renderPM
            from svglib.svglib import svg2rlg

            with tempfile.NamedTemporaryFile() as tmp:
                drawing = svg2rlg(self.file_info.path)
                renderPM.drawToFile(drawing, tmp.name, fmt="PNG")
                return PILImage.open(tmp.name)
        return PILImage.open(self.file_info.path)
