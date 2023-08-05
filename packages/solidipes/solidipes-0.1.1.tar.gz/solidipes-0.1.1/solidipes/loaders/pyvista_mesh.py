from functools import wraps

import pyvista as pv

from .. import viewers
from .file import File

DEFAULT_DATA_ID = "_"  #: data name given to implicitly added arrays
POINT_DATA_SUFFIX = " (point data)"
CELL_DATA_SUFFIX = " (cell data)"


def get_point_data_from_id_or_array(func):
    """Decorator to give either data_id or array to method accepting data_id"""

    @wraps(func)
    def wrapper(self, data_id_or_array, *args, **kwargs):
        if isinstance(data_id_or_array, str):
            data_id = data_id_or_array
            if data_id not in self.point_data_names:
                raise ValueError(f'No point data entry with the name "{data_id}" exists.')

        else:
            data_id = DEFAULT_DATA_ID
            self.add_point_data(data_id_or_array, data_id)

        return func(self, data_id, *args, **kwargs)

    return wrapper


def get_cell_data_from_id_or_array(func):
    """Decorator to give either data_id or array to method accepting data_id"""

    @wraps(func)
    def wrapper(self, data_id_or_array, *args, **kwargs):
        if isinstance(data_id_or_array, str):
            data_id = data_id_or_array
            if data_id not in self.cell_data_names:
                raise ValueError(f'No cell data entry with the name "{data_id}" exists.')

        else:
            data_id = DEFAULT_DATA_ID
            self.add_cell_data(data_id_or_array, data_id)

        return func(self, data_id, *args, **kwargs)

    return wrapper


class PyvistaMesh(File):
    """Mesh file loaded with pyvista"""

    supported_extensions = ["msh", "stl", "vtu", "pvtu"]

    def __init__(self, path):
        super().__init__(path)
        #: Fully loaded pyvista mesh
        self.pyvista_mesh = None
        self.add("mesh")

        self.default_viewer = viewers.PyvistaPlotter

    def copy_pyvista_data_to_collection(self):
        """Add pyvista data to data collection"""
        self.add("mesh", self.pyvista_mesh)

        for name in self.point_data_names:
            self.add(name + POINT_DATA_SUFFIX, self.get_point_data(name))

        for name in self.cell_data_names:
            self.add(name + CELL_DATA_SUFFIX, self.get_cell_data(name))

    @property
    def data_info(self):
        """Trigger loading of Pyvista mesh and return info"""
        self.load_all()
        return super().data_info

    def _load_data(self, key):
        self.pyvista_mesh = pv.read(self.file_info.path)
        self.copy_pyvista_data_to_collection()
        return self.pyvista_mesh

    def load_all(self):
        """Cannot rely on default implementation of load_all because data
        dictionary changes size"""
        self.get("mesh")

    @property
    def point_data_names(self):
        return self.pyvista_mesh.point_data.keys()

    @property
    def cell_data_names(self):
        return self.pyvista_mesh.cell_data.keys()

    def get_point_data(self, name):
        return self.pyvista_mesh.point_data.get_array(name)

    def add_point_data(self, array, name):
        self.pyvista_mesh.point_data.set_array(array, name)
        self.add(name + POINT_DATA_SUFFIX, array)

    def remove_point_data(self, name):
        self.pyvista_mesh.point_data.remove(name)
        self.remove(name + POINT_DATA_SUFFIX)

    def get_cell_data(self, name):
        return self.pyvista_mesh.cell_data.get_array(name)

    def add_cell_data(self, array, name):
        self.pyvista_mesh.cell_data.set_array(array, name)
        self.add(name + CELL_DATA_SUFFIX, array)

    def remove_cell_data(self, name):
        self.pyvista_mesh.cell_data.remove(name)
        self.remove(name + CELL_DATA_SUFFIX)

    @get_point_data_from_id_or_array
    def get_warped(self, data_id, factor=1.0):
        """
        Returns another PyvistaMesh with the mesh points displaced by the
        given data.

        Args:
            data (string): Name of point data. If data is 1D, the mesh is
                warped along its normals. Otherwise, the data must have the
                same number dimensionality as the mesh.
            factor (float): Factor to multiply the displacements by. Defaults
                to 1.0.
        """
        new_mesh = self.copy()
        dim = self.get_point_data(data_id).ndim  # 1 if scalar, 2 if vector
        if dim == 1:
            new_pyvista_mesh = new_mesh.pyvista_mesh.warp_by_scalar(data_id, factor=factor)

        else:
            new_pyvista_mesh = new_mesh.pyvista_mesh.warp_by_vector(data_id, factor=factor)

        new_mesh.pyvista_mesh = new_pyvista_mesh
        new_mesh.copy_pyvista_data_to_collection()

        return new_mesh

    @get_point_data_from_id_or_array
    def set_point_values(self, data_id):
        """
        Sets the point values for plotting to the given data.

        Args:
            data (string): Name of point data.
        """
        self.pyvista_mesh.set_active_scalars(data_id, "point")

    @get_cell_data_from_id_or_array
    def set_cell_values(self, data_id):
        """
        Sets the cell values for plotting to the given data.

        Args:
            data (string): Name of cell data.
        """
        self.pyvista_mesh.set_active_scalars(data_id, "cell")
