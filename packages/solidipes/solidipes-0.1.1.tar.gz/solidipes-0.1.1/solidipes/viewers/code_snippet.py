import os

import streamlit as st
from IPython.display import display

from .. import loaders, viewer_backends
from .text import Text


def guess_language(path):
    ext = os.path.splitext(path)[1]
    if ext == ".py":
        return "python"
    if ext in [".c", ".cc", ".cpp", ".cxx", ".h", ".hpp"]:
        return "cpp"
    if ext == ".m":
        return "matlab"
    return "python"


class Code(Text):
    def __init__(self, data=None):
        if data is not None:
            self.path = data.file_info.path
        super().__init__(data)
        self.compatible_data_types = [loaders.CodeSnippet, str]

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            display(self.text)

        elif viewer_backends.current_backend == "streamlit":
            st.code(self.text, language=guess_language(self.path))

        else:  # pure python
            print(self.text)
