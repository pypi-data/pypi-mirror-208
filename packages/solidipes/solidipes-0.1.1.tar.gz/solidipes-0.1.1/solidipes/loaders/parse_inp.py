import meshio
import numpy as np
import pyparsing as pp

################################################################
abaqus_to_meshio_permutation = {
    "C3D10": {0: 0, 1: 1, 2: 2, 3: 9, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8},
    "C3D10_4": {0: 0, 1: 1, 2: 2, 3: 9, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8},
    "C3D10R": {0: 0, 1: 1, 2: 2, 3: 9, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8},
}
################################################################
abaqus_to_meshio_type = {
    # trusses
    "T2D2": "line",
    "T2D2H": "line",
    "T2D3": "line3",
    "T2D3H": "line3",
    "T3D2": "line",
    "T3D2H": "line",
    "T3D3": "line3",
    "T3D3H": "line3",
    # beams
    "B21": "line",
    "B21H": "line",
    "B22": "line3",
    "B22H": "line3",
    "B31": "line",
    "B31H": "line",
    "B32": "line3",
    "B32H": "line3",
    "B33": "line3",
    "B33H": "line3",
    # surfaces
    "CPS4": "quad",
    "CPS4R": "quad",
    "S4": "quad",
    "S4R": "quad",
    "S4RS": "quad",
    "S4RSW": "quad",
    "S4R5": "quad",
    "S8R": "quad8",
    "S8R5": "quad8",
    "S9R5": "quad9",
    # "QUAD": "quad",
    # "QUAD4": "quad",
    # "QUAD5": "quad5",
    # "QUAD8": "quad8",
    # "QUAD9": "quad9",
    #
    "CPS3": "triangle",
    "STRI3": "triangle",
    "S3": "triangle",
    "S3R": "triangle",
    "S3RS": "triangle",
    "R3D3": "triangle",
    # "TRI7": "triangle7",
    # 'TRISHELL': 'triangle',
    # 'TRISHELL3': 'triangle',
    # 'TRISHELL7': 'triangle',
    #
    "STRI65": "triangle6",
    # 'TRISHELL6': 'triangle6',
    # volumes
    "C3D8": "hexahedron",
    "C3D8H": "hexahedron",
    "C3D8I": "hexahedron",
    "C3D8IH": "hexahedron",
    "C3D8R": "hexahedron",
    "C3D8RH": "hexahedron",
    # "HEX9": "hexahedron9",
    "C3D20": "hexahedron20",
    "C3D20H": "hexahedron20",
    "C3D20R": "hexahedron20",
    "C3D20RH": "hexahedron20",
    # "HEX27": "hexahedron27",
    #
    "C3D4": "tetra",
    "C3D4H": "tetra4",
    # "TETRA8": "tetra8",
    "C3D10": "tetra10",
    "C3D10_4": "tetra10",
    "C3D10R": "tetra10",
    "C3D10H": "tetra10",
    "C3D10I": "tetra10",
    "C3D10M": "tetra10",
    "C3D10MH": "tetra10",
    # "TETRA14": "tetra14",
    #
    # "PYRAMID": "pyramid",
    "C3D6": "wedge",
    "C3D15": "wedge15",
    #
    # 4-node bilinear displacement and pore pressure
    "CAX4P": "quad",
    # 6-node quadratic
    "CPE6": "triangle6",
}

################################################################


class ParseINP:
    _valid_characters = "\n " + pp.printables
    _valid_characters = _valid_characters.replace("*", "")
    ppText = pp.Word(_valid_characters)

    def parseBlock(self, token, level=None, content=None, tokens=None):
        # print(f"detected: {token} ({level}) {type(content)} {len(content)}")
        pass

    def _parseBlock(self, tokens):
        return self.parseBlock(
            tokens[1],
            level=len(tokens[0]),
            content=tokens[2].strip(),
            tokens=tokens,
        )

    def paragraph(self, n):
        if n == 0:
            return self.ppText
        _block_start = pp.Literal("*" * n) + pp.Word(pp.alphas)
        _block_content = pp.Combine(pp.ZeroOrMore(self.ppText | self.paragraph(n - 1)))
        _block = _block_start + _block_content
        _block.leaveWhitespace()
        _block.addParseAction(lambda toks: self._parseBlock(toks))

        return _block

    def inp_file(self):
        _p = self.paragraph(4) | self.paragraph(3) | self.paragraph(2) | self.paragraph(1)
        _file = pp.Combine(pp.OneOrMore(_p).leaveWhitespace())
        _file.addParseAction(lambda toks: self.final_parse(toks))
        return _file

    def final_parse(self, toks):
        pass

    def parse(self, filename):
        to_parse = open(filename).read()
        self.inp_file().parseString(to_parse)


################################################################


class ParseGEOF(ParseINP):
    def parseBlock(self, token, level=None, content=None, tokens=None):
        if token == "node":
            # print(f'{"*"*level}detected {token}')
            content = content.split("\n")
            n_nodes, dim = content[0].split()
            n_nodes = int(n_nodes)
            dim = int(dim)
            values = [_l.split() for _l in content[1:]]
            nodes = np.array(values, dtype=float)
            assert nodes.shape[0] == n_nodes
            assert nodes.shape[1] == dim + 1
            print(f"Loaded {n_nodes} nodes")
            self.nodes = nodes
            return "nodes:ok\n"
        if token == "element":
            # print(f'{"*"*level}detected {token}')
            content = content.split("\n")
            n_elements = int(content[0])
            values = [_l.split() for _l in content[1:]]
            values = np.array(values)
            el_type = np.array(values[:, 1], dtype=str)
            connectivity = np.array(values[:, 2:], dtype=int) - 1
            # print(connectivity)
            self.cells = {}
            for e, _type in enumerate(el_type):
                aba_type = _type.upper()
                _type = abaqus_to_meshio_type[aba_type]
                if _type not in self.cells:
                    self.cells[_type] = []

                perm = abaqus_to_meshio_permutation[aba_type]
                self.cells[_type].append(connectivity[e, :])

            for _type, conn in self.cells.items():
                permuted = np.zeros_like(conn)

                for i, ii in perm.items():
                    permuted[:, i] = connectivity[:, ii]
                self.cells[_type] = permuted
            # print(self.cells)
            print(f"Loaded {n_elements} elements")
            assert n_elements == connectivity.shape[0]
            return "elements:ok\n"
        if token == "geometry":
            # print(f'{"*"*level}detected {token}')
            # print(content)
            return content
        if token == "return":
            return content
        # print(f'{"*"*level}ignored {token}')
        return f'{"*"*level}ignored {token}'

    def final_parse(self, toks):
        points = self.nodes[:, 1:]
        cells = [(_type, c) for _type, c in self.cells.items()]
        self.mesh = meshio.Mesh(points, cells)
        return "mesh ok\n"


################################################################


def read_geof(filename):
    parser = ParseGEOF()
    parser.parse(filename)
    # print(parser.mesh)
    # parser.mesh.write("foo.vtu", file_format='vtu')
    # parser.mesh.write("foo.vtk", file_format='vtk')
    # parser.mesh.write("foo.msh", file_format='gmsh')
    return parser.mesh
