import matplotlib.pyplot as plt
import streamlit as st
from IPython.display import display

from .. import loaders, viewer_backends
from .viewer import Viewer, wrap_errors


class Table(Viewer):
    """Viewer for tables"""

    def __init__(self, data_container=None):
        self.compatible_data_types = [loaders.Table]
        #: Table to display
        self.data_container = None
        super().__init__(data_container)

    def add(self, data_container):
        """Replace the viewer's table"""
        self.check_data_compatibility(data_container)

        if isinstance(data_container, loaders.DataContainer):
            self.data_container = data_container

    def show_plot(self):
        if self.data_container is None:
            raise Exception("No data to show")

        table = self.data_container.table
        cols = table.columns

        c1, c2 = st.columns(2)
        marker = None
        line = "-"

        with c1:
            tab_col_select, tab_advanced = st.tabs(["Column selection", "Advanced"])
            with tab_col_select:
                xaxis = st.radio(
                    "X-axis",
                    options=cols,
                    horizontal=True,
                    key="xaxis_" + self.data_container.file_info.path,
                )
                yaxis = st.multiselect(
                    "Y-axis",
                    options=cols,
                    default=[c for c in cols if c != xaxis],
                    key="yaxis_" + self.data_container.file_info.path,
                )

            with tab_advanced:
                marker = st.text_input(
                    "Point marker",
                    value="o",
                    key="marker_" + self.data_container.file_info.path,
                )
                line = st.text_input(
                    "Line style",
                    value="-",
                    key="line_" + self.data_container.file_info.path,
                )

        with c2:
            if marker == "":
                marker = None
            if line == "":
                line = "-"

            fig = plt.figure(figsize=(7, 5))
            axe = fig.add_subplot(111)
            for y in yaxis:
                axe.plot(
                    table[xaxis],
                    table[y],
                    label=y,
                    marker=marker,
                    linestyle=line,
                )
            axe.set_xlabel(xaxis)
            axe.legend(loc="best")
            st.pyplot(fig)

    @wrap_errors
    def show(self):
        if self.data_container is None:
            raise Exception("No data to show")

        if viewer_backends.current_backend == "jupyter notebook":
            display(self.data_container.table)

        elif viewer_backends.current_backend == "streamlit":
            tab_figure, tab_raw = st.tabs(["Figure", "Raw Data"])
            with tab_figure:
                self.show_plot()
            with tab_raw:
                st.dataframe(self.data_container.table)

        else:  # python
            print(self.data_container.table)
