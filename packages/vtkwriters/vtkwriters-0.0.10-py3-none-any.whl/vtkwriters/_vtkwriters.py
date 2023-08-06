# -*- coding: utf-8 -*-

# def mydecode(s, dtype='i'):
#     bs = base64.b64decode(s)
#     print np.fromstring(bs, dtype=dtype)

import sys, os
from functools import partial
import base64
from pathlib import Path
import xml.dom
import numpy as np

vtk_celltype = {
    "point": 1,
    "vertex": 1,
    "pt": 1,
    "line": 3,
    "triangle": 5,
    "tri": 5,
    "pixel": 8,
    "quad": 9,
    "tetrahedron": 10,
    "tet": 10,
    "voxel": 11,
    "hexahedron": 12,
    "hex": 12,
    "wedge": 13,
    "polyhedron": 42,
}


def _extract_single_node(root, name, allow_none=False):
    all_nodes = root.getElementsByTagName(name)
    if len(all_nodes) == 0 and allow_none:
        return
    if len(all_nodes) != 1:
        raise RuntimeError(
            f"We should have a single {name} node (found {len(all_nodes)})!"
        )
    return all_nodes[0]


def create_childnode(parent, name, attributes=None):
    if attributes is None:
        attributes = {}
    elt = parent.ownerDocument.createElement(name)
    for key, val in attributes.items():
        elt.setAttribute(key, val)
    parent.appendChild(elt)
    return elt


def vtk_doc(filetype, version=None):
    impl = xml.dom.getDOMImplementation()
    doc = impl.createDocument(None, "VTKFile", None)
    doc.documentElement.setAttribute("type", filetype)
    doc.documentElement.setAttribute("header_type", "UInt64")
    if version is not None:
        doc.documentElement.setAttribute("version", version)
    return doc


def add_xdataarray_node(parent, nodename, dataname, dtype, ofmt, nbcomp, nbtuples):
    attributes = {}
    if dtype == np.int32:
        dtype = "Int32"
    elif dtype == np.int8:
        dtype = "Int8"
    elif dtype == np.uint8:
        dtype = "Int32"
    elif dtype == np.int64:
        dtype = "Int64"
    elif dtype == np.uint32:
        dtype = "Int32"
    elif dtype == np.uint64:
        dtype = "Int64"
    elif dtype == np.float32:
        dtype = "Float32"
    elif dtype == np.float64:
        dtype = "Float64"
    elif dtype == np.double:
        dtype = "Float64"
    else:
        raise Exception("Unknown data type: " + str(dtype))
    attributes["Name"] = dataname
    attributes["type"] = dtype
    attributes["format"] = ofmt
    if nbcomp is not None:
        attributes["NumberOfComponents"] = "%d" % nbcomp
    if nbtuples is not None:
        attributes["NumberOfTuples"] = "%d" % nbtuples
    return create_childnode(parent, nodename, attributes)


def add_dataarray_node(parent, name, dtype, ofmt="ascii", nbcomp=None, nbtuples=None):
    return add_xdataarray_node(parent, "DataArray", name, dtype, ofmt, nbcomp, nbtuples)


def add_pdataarray_node(parent, name, dtype, ofmt="ascii", nbcomp=None, nbtuples=None):
    return add_xdataarray_node(
        parent, "PDataArray", name, dtype, ofmt, nbcomp, nbtuples
    )


def add_dataarray(
    parent,
    array,
    name,
    ofmt="ascii",
    nbcomp=None,
    nbtuples=None,
    nbitemsbyrow=10,
):
    elt = add_dataarray_node(parent, name, array.dtype, ofmt, nbcomp, nbtuples)
    doc = elt.ownerDocument
    assert len(array.shape) == 1
    if ofmt == "ascii":
        if array.dtype.kind in ["i", "u"]:
            datafmt = "d"
        else:
            datafmt = ".10f"
        fmt = " ".join(["{:%s}" % datafmt] * nbitemsbyrow)
        i = -1
        for i in range(0, array.shape[0] // int(nbitemsbyrow)):
            elt.appendChild(
                doc.createTextNode(
                    fmt.format(*array[i * nbitemsbyrow : (i + 1) * nbitemsbyrow])
                )
            )
        left = array[(i + 1) * nbitemsbyrow :]
        fmt = " ".join(["{:%s}" % datafmt] * len(left))
        elt.appendChild(doc.createTextNode(fmt.format(*left)))
    elif ofmt == "binary":
        elt.appendChild(doc.createTextNode(""))  # this is just to indent node
        nbytes = 8 + array.nbytes
        tmp = np.empty(nbytes, dtype=np.byte)
        tmp = np.require(tmp, requirements=["CONTIGUOUS", "OWNDATA"])
        if sys.version_info.major < 3:
            buffersize = np.empty(1, dtype=np.ulonglong)
            buffersize[0] = array.nbytes
            tmp[:8] = np.getbuffer(buffersize)
            tmp[8:] = np.getbuffer(array)
        else:
            buffersize = memoryview(tmp[:8]).cast("Q")
            buffersize[0] = array.nbytes
            datapart = memoryview(tmp[8:])
            datapart[:] = memoryview(array).cast("b")
        s = base64.b64encode(tmp).decode("ascii")
        elt.appendChild(doc.createTextNode(s))
    else:
        raise Exception("Unknown format !")
    return elt


def add_piece_data(
    piece, location, data=None, attributes=None, ofmt="ascii", isfield=False
):
    data = data or {}
    attributes = attributes or {}
    datanode = create_childnode(piece, location, attributes)
    for name in sorted(data):
        a = data[name]
        nbtuples = None
        if isfield:
            a = np.array([a])
            nbtuples = a.shape[0]
        assert len(a.shape) == 1 or len(a.shape) == 2
        nbcomp = None
        if len(a.shape) == 2:
            nbcomp = a.shape[1]
            a = _ravel_information_block(a)
        add_dataarray(
            datanode, a, ofmt=ofmt, name=name, nbcomp=nbcomp, nbtuples=nbtuples
        )


def _ravel_information_block(block):
    return block.ravel(order="C")


# Paraview data array are in Fortran (column major) mode


def _ravel_structured_data_block(block):
    return block.ravel(order="F")


def vti_doc(
    shape,
    delta=None,
    origin=None,
    extent=None,
    pointdata=None,
    celldata=None,
    ofmt="binary",
):
    if extent is not None:
        assert origin is None and delta is None
        origin = tuple(x[0] for x in extent)
        # conversion to float in case the script is run with python2
        delta = tuple((x[1] - x[0]) / float(nx) for nx, x in zip(shape, extent))
    if delta is None:
        assert extent is None
        delta = (1.0,) * len(shape)
    assert len(shape) == len(delta)
    if origin is None:
        assert extent is None
        origin = (0.0,) * len(shape)
    assert len(shape) == len(origin)
    if len(shape) < 3:
        nbfills = 3 - len(shape)
        shape = shape + (1,) * nbfills
        delta = delta + (1.0,) * nbfills
        origin = origin + (0.0,) * nbfills
    if pointdata is None:
        pointdata = {}
    else:
        pointdata = {
            key: _ravel_structured_data_block(block) for key, block in pointdata.items()
        }
    if celldata is None:
        celldata = {}
    else:
        celldata = {
            key: _ravel_structured_data_block(block) for key, block in celldata.items()
        }
    doc = vtk_doc("ImageData")
    s = " ".join(["%f" for _ in origin])
    extent = " ".join(["0 %d" for _ in shape]) % tuple(shape)
    grid = create_childnode(
        doc.documentElement,
        "ImageData",
        {
            "Origin": s % tuple(origin),
            "Spacing": s % tuple(delta),
            "WholeExtent": extent,
        },
    )
    piece = create_childnode(grid, "Piece", {"Extent": extent})
    add_piece_data(piece, "PointData", pointdata, ofmt=ofmt)
    add_piece_data(piece, "CellData", celldata, ofmt=ofmt)
    return doc


def vtu_vertices(vertices):
    vertices = np.array(vertices, copy=False)
    assert len(vertices.shape) == 2
    dim = vertices.shape[1]
    assert dim <= 3
    if dim < 3:
        tmp = np.zeros((vertices.shape[0], 3), dtype=vertices.dtype)
        tmp[:, :dim] = vertices
        vertices = tmp
    return vertices


def add_all_data(node, pointdata=None, celldata=None, ofmt="binary"):
    add_piece_data(node, "PointData", pointdata, ofmt=ofmt)
    add_piece_data(node, "CellData", celldata, ofmt=ofmt)


def clear_all_data(doc):
    def _clear(piece_node, data_type):
        data_node = _extract_single_node(piece_node, data_type, allow_none=True)
        if data_node:
            piece_node.removeChild(data_node)

    piece_node = _extract_single_node(doc, "Piece")
    _clear(piece_node, "PointData")
    _clear(piece_node, "CellData")


def replace_data(doc, pointdata=None, celldata=None, ofmt="binary"):
    def _replace(piece_node, data_type, data):
        if data:
            data_node = _extract_single_node(piece_node, data_type, allow_none=True)
            if data_node:
                piece_node.removeChild(data_node)
            add_piece_data(piece_node, data_type, data, ofmt=ofmt)

    piece_node = _extract_single_node(doc, "Piece")
    _replace(piece_node, "PointData", pointdata)
    _replace(piece_node, "CellData", celldata)


def add_field_data(node, data, ofmt="binary"):
    if data is not None:
        add_piece_data(node, "FieldData", data, ofmt=ofmt, isfield=True)


def vtu_doc_from_COC(
    vertices,
    offsets,
    connectivity,
    celltypes,
    fielddata=None,
    pointdata=None,
    celldata=None,
    ofmt="binary",
    integer_type=np.int32,
):
    """
    :param integer_type: Type to be used for cell types, connectivity and offsets.
    """
    offsets = offsets.astype(integer_type)
    celltypes = celltypes.astype(integer_type)
    connectivity = connectivity.astype(integer_type)
    doc = vtk_doc("UnstructuredGrid", version="1.0")
    grid = create_childnode(doc.documentElement, "UnstructuredGrid")
    piece = create_childnode(
        grid,
        "Piece",
        {
            "NumberOfPoints": "%d" % vertices.shape[0],
            "NumberOfCells": "%d" % celltypes.shape[0],
        },
    )
    points = create_childnode(piece, "Points")
    add_dataarray(
        points, _ravel_information_block(vertices), "Points", nbcomp=3, ofmt=ofmt
    )
    cells = create_childnode(piece, "Cells")
    add_dataarray(
        cells, _ravel_information_block(connectivity), "connectivity", ofmt=ofmt
    )
    add_dataarray(cells, offsets, "offsets", ofmt=ofmt)
    add_dataarray(cells, celltypes, "types", ofmt=ofmt)
    add_all_data(piece, pointdata=pointdata, celldata=celldata)
    add_field_data(grid, fielddata, ofmt=ofmt)
    return doc


def vtu_doc(
    vertices,
    connectivity,
    celltypes=None,
    fielddata=None,
    pointdata=None,
    celldata=None,
    ofmt="binary",
    integer_type=np.int32,
):
    """
    :param integer_type: Type to be used for cell types, connectivity and offsets.
    """

    @np.vectorize
    def compute_celltype(cellsize):
        return vtk_celltype[
            {
                1: "pt",
                2: "line",
                3: "tri",
                4: "tet",
                6: "wedge",
                8: "hex",
            }[cellsize]
        ]

    vertices = vtu_vertices(vertices)
    if type(celltypes) is str:
        celltypes = vtk_celltype[celltypes]
    try:
        celltypes = int(celltypes)
    except TypeError:
        celltypes = None
    try:
        connectivity = np.array(connectivity, dtype=integer_type, copy=False)
    except ValueError:
        # connectivities may have different length
        cellsizes = np.array([len(cell) for cell in connectivity])
        if celltypes is None:
            celltypes = compute_celltype(cellsizes)
        celltypes = np.array(celltypes, dtype=integer_type, copy=False)
        connectivity = np.hstack(connectivity)
        connectivity = connectivity.astype(integer_type)
    else:
        assert len(connectivity.shape) == 2
        nbcells, cellsize = connectivity.shape
        cellsizes = np.tile(cellsize, nbcells)
        if celltypes is None:
            celltypes = np.tile(compute_celltype(cellsize), nbcells)
        elif type(celltypes) is int:
            assert len(np.unique(cellsizes)) == 1
            celltypes = np.tile(celltypes, nbcells)
    finally:
        cellsizes = cellsizes.astype(integer_type)
        offsets = np.cumsum(cellsizes)
        nbcells = offsets.shape[0]
    assert offsets.shape == celltypes.shape
    return vtu_doc_from_COC(
        vertices,
        offsets,
        connectivity,
        celltypes,
        fielddata,
        pointdata,
        celldata,
        ofmt,
        integer_type=integer_type,
    )


def polyhedra_vtu_doc(
    vertices, cells_faces, pointdata=None, celldata=None, fielddata=None, ofmt="binary"
):
    doc = vtk_doc("UnstructuredGrid", version="1.0")
    grid = create_childnode(doc.documentElement, "UnstructuredGrid")
    nb_cells = len(cells_faces)
    piece = create_childnode(
        grid,
        "Piece",
        {
            "NumberOfPoints": "%d" % vertices.shape[0],
            "NumberOfCells": "%d" % nb_cells,
        },
    )
    points = create_childnode(piece, "Points")
    add_dataarray(
        points, _ravel_information_block(vertices), "Points", nbcomp=3, ofmt=ofmt
    )
    cells = create_childnode(piece, "Cells")
    cells_nodes = [np.unique(np.hstack(faces)) for faces in cells_faces]
    int64array = lambda a: np.asarray(a, dtype=np.int64)

    def as_coc(l):
        return (
            int64array(np.cumsum([len(a) for a in l])),  # offsets
            int64array(np.hstack(l)),  # stacked elemnts
        )

    offsets, connectivity = as_coc(cells_nodes)
    celltypes = np.asarray(np.tile(vtk_celltype["polyhedron"], nb_cells), dtype=np.int8)
    all_faces = []
    for faces in cells_faces:
        tmp = [len(faces)]
        for face in faces:
            tmp.append(len(face))
            tmp.extend(face)
        all_faces.append(tmp)
    faceoffsets, faces = as_coc(all_faces)
    add_dataarray(cells, connectivity, "connectivity", ofmt=ofmt)
    add_dataarray(cells, offsets, "offsets", ofmt=ofmt)
    add_dataarray(cells, celltypes, "types", ofmt=ofmt)
    add_dataarray(cells, faces, "faces", ofmt=ofmt)
    add_dataarray(cells, faceoffsets, "faceoffsets", ofmt=ofmt)
    add_all_data(piece, pointdata=pointdata, celldata=celldata, ofmt=ofmt)
    add_field_data(grid, fielddata, ofmt=ofmt)
    return doc


def parallel_doc(
    doc_type,
    vertices_type,
    pieces,
    pointdata_types=None,
    celldata_types=None,
    ofmt="binary",
):
    doc = vtk_doc(f"P{doc_type}")
    root_element = doc.documentElement
    pugrid = create_childnode(root_element, f"P{doc_type}", {"GhostLevel": "0"})
    ppoints = create_childnode(pugrid, "PPoints")
    add_pdataarray_node(ppoints, "Points", vertices_type, ofmt, nbcomp=3)

    def add_data_node(node_name, data_types):
        if data_types is not None:
            data_node = create_childnode(pugrid, node_name)
            for name in sorted(data_types):
                data_type = data_types[name]
                try:
                    data_type, nbcomp = data_type
                    add_pdataarray_node(data_node, name, data_type, ofmt, nbcomp=nbcomp)
                except TypeError:
                    add_pdataarray_node(data_node, name, data_type, ofmt)

    add_data_node("PPointData", pointdata_types)
    add_data_node("PCellData", celldata_types)
    for piece in pieces:
        create_childnode(pugrid, "Piece", {"Source": piece})
    return doc


def pvtu_doc(*args, **kwargs):
    return parallel_doc("UnstructuredGrid", *args, **kwargs)


def pvtp_doc(*args, **kwargs):
    return parallel_doc("PolyData", *args, **kwargs)


def elevation_map_as_vtp_doc(
    zmap,
    upper_left_center=None,
    upper_left_corner=None,
    shape=None,
    steps=None,
    pointdata=None,
    celldata=None,
    texture=None,
    ofmt="binary",
    return_elements=False,
):
    """ """

    if shape is None:
        assert zmap.ndim == 2
        shape = zmap.shape
    ny, nx = shape
    z = np.reshape(zmap, (ny, nx))
    assert steps is not None
    dx, dy = steps
    assert upper_left_center is None or upper_left_corner is None
    assert not (upper_left_center is None and upper_left_corner is None)
    assert nx > 1 and ny > 1
    assert dx > 0 and dy > 0
    if upper_left_center is not None:
        Ox, Oy = upper_left_center
    else:
        Ox, Oy = upper_left_corner
        Ox += 0.5 * dx
        Oy += 0.5 * dy

    x = np.arange(Ox, Ox + (nx - 0.5) * dx, dx)
    assert x.shape == (nx,)
    y = np.arange(Oy, Oy - (ny - 0.5) * dy, -dy)
    assert y.shape == (ny,)
    xy = np.vstack([np.hstack([x[:, None], np.tile(yi, (nx, 1))]) for yi in y])
    vertices = np.hstack([xy, z.ravel()[:, None]])
    row = np.hstack(
        [
            np.arange(nx - 1)[:, None],
            np.arange(1, nx)[:, None],
            np.arange(1, nx)[:, None] + nx,
            np.arange(nx - 1)[:, None] + nx,
        ]
    ).ravel()
    quads = np.hstack([row + j * nx for j in range(ny - 1)])
    doc = vtk_doc("PolyData", version="1.0")
    grid = create_childnode(doc.documentElement, "PolyData")
    assert vertices.shape[0] == nx * ny
    assert quads.shape[0] == 4 * (nx - 1) * (ny - 1)
    piece = create_childnode(
        grid,
        "Piece",
        {
            "NumberOfPoints": f"{nx*ny:d}",
            "NumberOfVerts": "0",
            "NumberOfLines": "0",
            "NumberOfStrips": "0",
            "NumberOfPolys": f"{(nx-1)*(ny-1):d}",
        },
    )
    points = create_childnode(piece, "Points")
    add_dataarray(
        points, _ravel_information_block(vertices), "Points", nbcomp=3, ofmt=ofmt
    )
    polys = create_childnode(piece, "Polys")
    add_dataarray(polys, _ravel_information_block(quads), "connectivity", ofmt=ofmt)
    add_dataarray(polys, np.arange(4, nx * ny * 4 + 1, 4), "offsets", ofmt=ofmt)
    if pointdata is None:
        pointdata = {}
    if texture is not None:
        if hasattr(texture, "left"):
            Ox, Oy = texture.left, texture.bottom
            Lx = texture.right - Ox
            Ly = texture.top - Oy
        else:
            Ox, Oy = texture.lower_left_corner
            Lx, Ly = texture.extent
        assert Lx > 0 and Ly > 0
        tcoords = np.hstack(
            [
                ((vertices[:, 0] - Ox) / Lx)[:, None],
                ((vertices[:, 1] - Oy) / Ly)[:, None],
            ]
        )
        assert tcoords.shape == (vertices.shape[0], 2)
        pointdata["TextureCoordinates"] = tcoords
        add_piece_data(
            piece,
            "PointData",
            pointdata,
            attributes={"TCoords": "TextureCoordinates"},
            ofmt=ofmt,
        )
    else:
        add_piece_data(piece, "PointData", pointdata, ofmt=ofmt)
    if celldata is None:
        celldata = {}
    add_piece_data(piece, "CellData", celldata, ofmt=ofmt)
    if return_elements:
        return doc, (vertices, quads)
    return doc


def vtp_doc(
    vertices,
    polys,
    pointdata=None,
    celldata=None,
    ofmt="binary",
):
    """ """
    vertices = np.asarray(vertices)
    assert vertices.ndim == 2 and vertices.shape[1] == 3
    doc = vtk_doc("PolyData", version="1.0")
    grid = create_childnode(doc.documentElement, "PolyData")
    piece = create_childnode(
        grid,
        "Piece",
        {
            "NumberOfPoints": f"{vertices.shape[0]:d}",
            "NumberOfVerts": "0",
            "NumberOfLines": "0",
            "NumberOfStrips": "0",
            "NumberOfPolys": f"{len(polys):d}",
        },
    )
    points = create_childnode(piece, "Points")
    add_dataarray(
        points, _ravel_information_block(vertices), "Points", nbcomp=3, ofmt=ofmt
    )
    polygons = create_childnode(piece, "Polys")
    polydata = np.hstack(polys)
    offsets = np.cumsum([len(p) for p in polys], dtype=polydata.dtype)
    add_dataarray(polygons, polydata, "connectivity", ofmt=ofmt)
    add_dataarray(polygons, offsets, "offsets", ofmt=ofmt)
    if pointdata is None:
        pointdata = {}
    add_piece_data(piece, "PointData", pointdata, ofmt=ofmt)
    if celldata is None:
        celldata = {}
    add_piece_data(piece, "CellData", celldata, ofmt=ofmt)
    return doc


def vts_doc(
    vertices,
    pointdata=None,
    celldata=None,
    ofmt="binary",
):
    """ """
    vertices = np.asarray(vertices)
    assert vertices.ndim == vertices.shape[-1] + 1
    doc = vtk_doc("StructuredGrid", version="1.0")
    extent_description = " ".join(
        [f"0 {vertices.shape[i] - 1}" for i in range(vertices.ndim - 1)]
    )
    grid = create_childnode(
        doc.documentElement, "StructuredGrid", {"WholeExtent": extent_description}
    )
    piece = create_childnode(
        grid,
        "Piece",
        {
            "Extent": extent_description,
        },
    )
    points = create_childnode(piece, "Points")
    add_dataarray(
        points,
        _ravel_information_block(vertices),
        "Points",
        nbcomp=vertices.ndim - 1,
        ofmt=ofmt,
    )
    if pointdata is None:
        pointdata = {}
    add_piece_data(piece, "PointData", pointdata, ofmt=ofmt)
    if celldata is None:
        celldata = {}
    add_piece_data(piece, "CellData", celldata, ofmt=ofmt)
    return doc


def vtr_doc(
    coordinates,
    pointdata=None,
    celldata=None,
    ofmt="binary",
):
    """ """
    coordinates = tuple(np.asarray(x, dtype=np.float64) for x in coordinates)
    assert all(x.ndim == 1 for x in coordinates)
    doc = vtk_doc("RectilinearGrid", version="1.0")
    extent_description = " ".join([f"0 {x.size - 1}" for x in coordinates])
    grid = create_childnode(
        doc.documentElement, "RectilinearGrid", {"WholeExtent": extent_description}
    )
    piece = create_childnode(
        grid,
        "Piece",
        {
            "Extent": extent_description,
        },
    )
    coord_node = create_childnode(piece, "Coordinates")
    for x, s in zip(coordinates, ["x", "y", "z"]):
        add_dataarray(
            coord_node,
            _ravel_information_block(x),
            s,
            ofmt=ofmt,
        )
    if pointdata is None:
        pointdata = {}
    add_piece_data(piece, "PointData", pointdata, ofmt=ofmt)
    if celldata is None:
        celldata = {}
    add_piece_data(piece, "CellData", celldata, ofmt=ofmt)
    return doc


def points_as_vtu_doc(vertices, pointdata=None, ofmt="binary"):
    connectivity = np.arange(len(vertices))
    connectivity.shape = (-1, 1)
    return vtu_doc(
        vertices,
        connectivity,
        celltypes="point",
        pointdata=pointdata,
        ofmt=ofmt,
    )


def block_as_vti_doc(
    block,
    location,
    name,
    delta=None,
    origin=None,
    ofmt="binary",
):
    block = np.array(block, copy=False)
    pointdata = celldata = {}
    if location == "point":
        pointdata = {name: _ravel_structured_data_block(block)}
        shape = tuple(n - 1 for n in block.shape)
    elif location == "cell":
        celldata = {name: _ravel_structured_data_block(block)}
        shape = block.shape
    else:
        raise Exception("unknown location" + str(location))
    return vti_doc(
        shape,
        delta=delta,
        origin=origin,
        pointdata=pointdata,
        celldata=celldata,
        ofmt=ofmt,
    )


def blocks_as_vti_doc(
    pointdata=None,
    celldata=None,
    delta=None,
    origin=None,
    ofmt="binary",
):
    if pointdata is None:
        pointdata = {}
    if celldata is None:
        celldata = {}
    pshapes = [v.shape for v in pointdata.values()]
    pshape = None if not pshapes else pshapes[0]
    if not (pshape is None or all([shape == pshape for shape in pshapes])):
        raise Exception("incompatible point data shapes")
    cshapes = [v.shape for v in celldata.values()]
    cshape = None if not cshapes else cshapes[0]
    if not (cshape is None or all([shape == cshape for shape in cshapes])):
        raise Exception("incompatible cell data shapes")
    if pshape is None and cshape is None:
        raise Exception("no data provided")
    if not (pshape is None or cshape is None or cshape == tuple(n - 1 for n in pshape)):
        raise Exception("incompatible pointdata and celldata")
    if cshape is None:
        shape = tuple(n - 1 for n in pshape)
    else:
        shape = cshape
    return vti_doc(
        shape,
        pointdata=pointdata,
        celldata=celldata,
        delta=delta,
        origin=origin,
        ofmt=ofmt,
    )


def pvd_doc(snapshots):
    """snapshots is assumed to be a collection of tuples with the format
    (time, filepath)"""
    doc = vtk_doc("Collection")
    collection = create_childnode(doc.documentElement, "Collection")
    for t, filepath in sorted(snapshots):
        create_childnode(
            collection,
            "DataSet",
            {"timestep": "%g" % t, "file": str(filepath)},
        )
    return doc


def vtm_doc(elements, fielddata=None, ofmt="ascii"):
    """Creates a composite dataset from paraview files.
    :param elements: is a sequence of filenames or tuple with (element name, filename)
    if not given basenames are used to name blocks,
    it can also be a dictionnary to define subblocks"""

    def refactor(elements):
        result = []
        for element in elements:
            if type(element) is tuple:
                name, filepath = element
                filepath = Path(filepath)
            else:
                filepath = Path(element)
                name = filepath.with_suffix("").name
            assert filepath.exists(), f"{filepath} does not exist"
            result.append((name, filepath))
        return result

    def add_datasets(block, elements):
        for k, (name, filepath) in enumerate(elements):
            create_childnode(
                block,
                "DataSet",
                {"index": f"{k}", "name": name, "file": str(filepath)},
            )

    doc = vtk_doc("vtkMultiBlockDataSet", version="1.0")  # version is mandatory here
    multiblock = create_childnode(doc.documentElement, "vtkMultiBlockDataSet")
    try:
        for k, (block_name, subblocks) in enumerate(elements.items()):
            block = create_childnode(
                multiblock,
                "Block",
                {"index": f"{k}", "name": block_name},
            )
            add_datasets(block, refactor(subblocks))
    except AttributeError:
        add_datasets(multiblock, refactor(elements))
    add_field_data(multiblock, fielddata, ofmt=ofmt)
    return doc


def write_xml(doc, out, indent=" " * 2, newl="\n", extension=""):
    def output(filelike):
        doc.writexml(filelike, addindent=indent, newl=newl)

    if isinstance(out, str):
        filename = out
        if not filename.endswith(extension):
            filename = out + extension
        with open(filename, "w") as f:
            output(f)
        return filename
    else:
        output(out)
        return out


write_vti = partial(write_xml, extension=".vti")
write_vts = partial(write_xml, extension=".vts")
write_vtr = partial(write_xml, extension=".vtr")
write_vtu = partial(write_xml, extension=".vtu")
write_pvtu = partial(write_xml, extension=".pvtu")
write_pvd = partial(write_xml, extension=".pvd")
write_vtm = partial(write_xml, extension=".vtm")
write_vtp = partial(write_xml, extension=".vtp")
write_pvtp = partial(write_xml, extension=".pvtp")


def _write_data_snapshots(
    doc_from_data,
    times,
    datas,
    name,
    filepath=".",
    propname=None,
    proppath=".",
    extension="",
    delta=None,
    origin=None,
    location="cell",
    ofmt="binary",
    indent=" " * 2,
    newl="\n",
):
    if propname is None:
        propname = name
    filedir = os.path.join(filepath, proppath)
    if os.path.exists(filedir):
        assert os.path.isdir(filedir)
    else:
        os.makedirs(filedir)
    datapath = os.path.join(filedir, propname)
    datafiles = []
    # size of counter field
    fmt = "%%0%dd" % (int(np.log10(len(datas)) + 1))
    for i, data in enumerate(datas):
        datafiles.append(
            write_xml(
                doc_from_data(data, propname),
                datapath + (fmt % i),
                indent=indent,
                newl=newl,
                extension=extension,
            )
        )
    filepath = os.path.join(filepath, name)
    datafiles = [os.path.relpath(path, os.path.dirname(filepath)) for path in datafiles]
    return write_pvd(
        pvd_doc(list(zip(times, datafiles))),
        filepath,
        indent=indent,
        newl=newl,
    )


def write_block_snapshots(
    times,
    blocks,
    name,
    filepath=".",
    propname=None,
    proppath=".",
    delta=None,
    origin=None,
    location="cell",
    ofmt="binary",
    indent=" " * 2,
    newl="\n",
):
    def doc_from_data(data, name):
        return block_as_vti_doc(
            data,
            location,
            name,
            delta=delta,
            origin=origin,
            ofmt=ofmt,
        )

    return _write_data_snapshots(
        doc_from_data,
        times,
        blocks,
        name,
        filepath=filepath,
        propname=propname,
        proppath=proppath,
        extension=".vti",
        indent=" " * 2,
        newl="\n",
    )


def write_unstructured_snapshots(
    times,
    name,
    vertices,
    connectivity,
    datas,
    location,
    filepath=".",
    propname=None,
    proppath=".",
    celltypes=None,
    ofmt="binary",
    indent=" " * 2,
    newl="\n",
):
    def doc_from_data(data, name):
        pointdata = None
        celldata = None
        datadict = {name: data}
        if location == "point":
            pointdata = datadict
        if location == "cell":
            celldata = datadict
        return vtu_doc(
            vertices,
            connectivity,
            celltypes=celltypes,
            pointdata=pointdata,
            celldata=celldata,
            ofmt=ofmt,
        )

    return _write_data_snapshots(
        doc_from_data,
        times,
        datas,
        name,
        filepath=filepath,
        propname=propname,
        proppath=proppath,
        extension=".vtu",
        indent=" " * 2,
        newl="\n",
    )


def points_as_vtu(vertices):
    tmp = np.reshape(vertices, (-1, 3))
    return vtu_doc(
        tmp,
        np.reshape(np.arange(tmp.shape[0]), (-1, 1)),
    )


def polyline_as_vtu(vertices):
    tmp = np.reshape(vertices, (-1, 3))
    assert tmp.shape[0] > 1
    return vtu_doc(
        tmp,
        np.transpose(np.vstack([range(tmp.shape[0] - 1), range(1, tmp.shape[0])])),
    )
