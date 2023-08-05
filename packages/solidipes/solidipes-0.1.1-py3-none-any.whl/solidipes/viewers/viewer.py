from abc import ABC, abstractmethod

import streamlit as st
from IPython.display import display

from .. import viewer_backends

################################################################


def wrap_errors(func):
    def foo(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if viewer_backends.current_backend == "jupyter notebook":
                display(e)
            elif viewer_backends.current_backend == "streamlit":
                st.text(e)
            else:  # python
                print(e)

    return foo


################################################################


class Viewer(ABC):
    """Abstract class for viewers

    If istanciated with data, it will directly display it.

    Args:
        data: data to display
        add_kwargs: kwargs to pass to the add method. Note: cannot be passed
            as a positional argement because of get_data_from_container
            decorator.
        show_kwargs: kwargs to pass to the show method
        **kwargs: kwargs to pass to the init method
    """

    def __init__(self, data_container=None, add_kwargs={}, show_kwargs={}, **kwargs):
        #: List of data types that are compatible with the viewer
        self.compatible_data_types = []

        if data_container is None:
            return

        self.data_container = data_container
        self.add(data_container, **add_kwargs)
        self.show(**show_kwargs)

    def check_data_compatibility(self, data):
        """Check if data is compatible with the viewer"""
        if len(self.compatible_data_types) == 0:
            return True

        if type(data) not in self.compatible_data_types:
            raise TypeError(f"Data type {type(data)} is not compatible with {self.__class__.__name__}")

        return True

    @abstractmethod
    def add(self, data, **kwargs):
        """Add data to the viewer"""
        self.check_data_compatibility(data)

    @abstractmethod
    def show(self, **kwargs):
        """Show the viewer"""
        pass

    def save(self, path, **kwargs):
        """Save the view to a file"""
        raise Exception("This Viewer cannot save content to file.")
