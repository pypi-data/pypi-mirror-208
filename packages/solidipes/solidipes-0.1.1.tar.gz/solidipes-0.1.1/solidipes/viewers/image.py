import streamlit as st
from IPython.display import display

from .. import loaders, viewer_backends
from .viewer import Viewer


class Image(Viewer):
    """Viewer for images"""

    def __init__(self, data=None):
        self.compatible_data_types = [loaders.Image]
        #: Image to display
        self.image = None
        super().__init__(data)

    def add(self, data_container):
        """Replace the viewer's image"""
        self.check_data_compatibility(data_container)
        self.image = data_container.image

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            display(self.image)

        elif viewer_backends.current_backend == "streamlit":
            with st.container():
                st.image(self.image)
        else:  # python
            self.image.show()
