import os

from ..utils import get_mimes
from .data_container import DataContainer
from .mime_types import get_extension, get_mime_type, get_possible_extensions, is_valid_extension


class File(DataContainer):
    """Abstract container class for file metadata

    A File can be read from disk and may contain multiple DataContainer
    entries.
    """

    #: List of supported mime types. Override in subclasses.
    supported_mime_types = []
    #: List of additionally supported file extensions. Override in subclasses.
    supported_extensions = []

    def __init__(self, path):
        super().__init__()
        self.name = os.path.basename(path)

        # Metadata
        stats = os.stat(path)
        mime_type, charset = get_mime_type(path)
        self.add(
            "file_info",
            DataContainer(
                {
                    "size": stats.st_size,
                    "created_time": stats.st_ctime,
                    "modified_time": stats.st_mtime,
                    "permissions": stats.st_mode,
                    "owner": stats.st_uid,
                    "group": stats.st_gid,
                    "path": path,
                    "type": mime_type,
                    "charset": charset,
                    "extension": get_extension(path),
                }
            ),
        )

    def valid_loading(self):
        return super().valid_loading() and self.valid_extension()

    def valid_extension(self):
        if self.file_info.path in get_mimes():
            return True

        res = is_valid_extension(self.file_info.path, self.file_info.type)
        if not res:
            self.errors.append(
                f"Mime type '{self.file_info.type}' not matching extension '{os.path.splitext(self.file_info.path)[1]}'"
            )
        return res

    @classmethod
    def check_file_support(cls, path):
        """Check mime type, then extension of file"""

        mime_type, _ = get_mime_type(path)

        for supported_mime_type in cls.supported_mime_types:
            if mime_type.startswith(supported_mime_type):
                return True

        extension = get_extension(path)

        if extension in cls.supported_extensions:
            return True

        extensions = get_possible_extensions(mime_type)
        for e in extensions:
            if e in cls.supported_extensions:
                return True

        return False
