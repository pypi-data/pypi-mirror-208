import streamlit as st
from IPython.display import display

from .. import loaders, viewer_backends
from .viewer import Viewer


class Binary(Viewer):
    """Viewer for (unknown) binary"""

    def __init__(self, data=None):
        self.compatible_data_types = [loaders.Binary, str]
        self.data = []
        super().__init__(data)

    def add(self, data_container):
        """Append text to the viewer"""
        self.check_data_compatibility(data_container)

        if isinstance(data_container, loaders.DataContainer):
            self.data.append(data_container.file_info)
        else:
            raise RuntimeError("can only handle binary types")

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            for d in self.data:
                for k, v in d.data.items():
                    display(k, v)

        elif viewer_backends.current_backend == "streamlit":
            with st.container():
                print(self.data)
                for d in self.data:
                    for k, v in d.data.items():
                        st.markdown(f"- {k} : {v}")
        else:  # python
            for d in self.data.items():
                for k, v in d.data:
                    print(k, k)
