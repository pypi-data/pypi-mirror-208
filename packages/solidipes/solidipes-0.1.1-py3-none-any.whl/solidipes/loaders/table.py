import pandas as pd

from .. import viewers
from .data_container import wrap_errors
from .file import File


class Table(File):
    """Table file loaded with Pandas"""

    supported_mime_types = ["text/csv", "application/vnd.ms-excel"]
    supported_extensions = ["csv", "xlsx"]

    def __init__(self, path):
        super().__init__(path)

        # find loader matching file extension
        if self.file_info.type == "text/csv":
            self.pandas_loader = pd.read_csv
        elif self.file_info.type == "application/vnd.ms-excel" or self.file_info.extension in ["xlsx"]:
            self.pandas_loader = pd.read_excel
        else:
            raise RuntimeError(f"File type not supported: {path} {self.file_info.type}")

        self.add("header")
        self.add("table")
        self.default_viewer = viewers.Table

    def validate_header(self, header):
        for h in header:
            try:
                h = float(h)
                self.errors.append(f"Incorrect header: {header}")
                break
            except Exception:
                pass
            if h.startswith("Unnamed"):
                self.errors.append(f"Incorrect header: {header}")
                break

    @wrap_errors
    def _load_data(self, key):
        """Load header or full table with Pandas"""

        if key == "header":
            data = self.pandas_loader(self.file_info.path, nrows=0)
            header = list(data.columns)
            self.validate_header(header)
            return ", ".join(header)

        if key == "table":
            return self.pandas_loader(self.file_info.path)
            self.validate_header(data.columns)
