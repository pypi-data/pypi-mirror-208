from pyvista.utilities.fileio import from_meshio

from .parse_inp import read_geof
from .pyvista_mesh import PyvistaMesh


class GeofMesh(PyvistaMesh):
    """Mesh file loaded with pyvista"""

    supported_extensions = ["geof"]

    def _load_data(self, key):
        self.mesh = from_meshio(read_geof(self.file_info.path))
        self.add("mesh", self.mesh)
        return self.mesh
