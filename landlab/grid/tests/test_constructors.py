import numpy as np
import pytest
from numpy.testing import assert_array_equal
from six import StringIO

from landlab import CLOSED_BOUNDARY, HexModelGrid, RasterModelGrid, NetworkModelGrid, VoronoiDelaunayGrid, RadialModelGrid, ModelGrid

from landlab.grid.raster import from_dict as raster_from_dict
from landlab.grid.hex import from_dict as hex_from_dict


def test_raster_old_from_dict_deprecated():
    params = {"NUM_COLS": 10, "NUM_ROWS": 5, "GRID_SPACING": 4}
    with pytest.deprecated_call():
        mg = raster_from_dict(params)
    assert mg.shape == (5, 10)
    assert mg.dx == 4
    assert mg.dy == 4


def test_hex_old_from_dict_deprecated():
    params = {"NUM_COLS": 10, "NUM_ROWS": 5, "GRID_SPACING": 4}
    with pytest.deprecated_call():
        mg = hex_from_dict(params)
    assert mg.number_of_nodes == 54


def test_raster_from_file():
    file_strn = ("shape:\n"
                 "    - 10\n"
                 "    - 20\n"
                 "xy_spacing:\n"
                 "    - 25\n"
                 "    - 45\n"
                 "bc:\n"
                 "    right: 'closed'\n"
                 "    top: 'closed'\n"
                 "    left: 'closed'\n"
                 "    bottom: 'closed'\n"
                 "xy_of_lower_left:\n"
                 "    - 35\n"
                 "    - 55\n"
                 "axis_name:\n"
                 "    - 'spam'\n"
                 "    - 'eggs'\n"
                 "axis_units:\n"
                 "    - 'smoot'\n"
                 "    - 'parsec'")
    with StringIO(file_strn) as file_like:
        mg = RasterModelGrid.from_file(file_like)

    # assert things.
    assert mg.shape == (10, 20)
    assert mg.dx == 25
    assert mg.dy == 45
    assert (mg.x_of_node.min(), mg.y_of_node.min()) == (35, 55)
    assert np.all(mg.status_at_node[mg.boundary_nodes] == CLOSED_BOUNDARY)
    assert mg.axis_units == ("smoot", "parsec")
    assert mg.axis_name == ("spam", "eggs")


def test_raster_from_dict():
    params = {
        "shape": (10, 20),
        "xy_spacing": (25, 45),
        "bc": {
            "right": "closed",
            "top": "closed",
            "left": "closed",
            "bottom": "closed",
        },
        "xy_of_lower_left": (35, 55),
        "axis_name": ("spam", "eggs"),
        "axis_units": ("smoot", "parsec"),
    }

    mg = RasterModelGrid.from_dict(params)

    # assert things.
    assert mg.shape == (10, 20)
    assert mg.dx == 25
    assert mg.dy == 45
    assert (mg.x_of_node.min(), mg.y_of_node.min()) == (35, 55)
    assert np.all(mg.status_at_node[mg.boundary_nodes] == CLOSED_BOUNDARY)
    assert mg.axis_units == ("smoot", "parsec")
    assert mg.axis_name == ("spam", "eggs")


def test_hex_from_dict():
    params = {
        "base_num_rows": 5,
        "base_num_cols": 4,
        "dx": 2.,
        "xy_of_lower_left": (35, 55),
        "axis_name": ("spam", "eggs"),
        "axis_units": ("smoot", "parsec"),
    }

    mg = HexModelGrid.from_dict(params)

    # assert things.
    true_x_node = np.array([37.,  39.,  41.,  43.,
                            36.,  38.,  40.,  42.,  44.,
                            35.,  37.,  39.,  41.,  43.,  45.,
                            36.,  38.,  40.,  42.,  44.,
                            37.,  39.,  41.,  43.])
    assert_array_equal(true_x_node, mg.x_of_node)
    assert (mg.x_of_node.min(), mg.y_of_node.min()) == (35, 55)
    assert mg.axis_units == ("smoot", "parsec")
    assert mg.axis_name == ("spam", "eggs")


def test_radial_from_dict():
    params = {
        "num_shells": 5,
        "dr": 2.,
        "xy_of_center": (35, 55),
        "axis_name": ("spam", "eggs"),
        "axis_units": ("smoot", "parsec"),
    }

    mg = RadialModelGrid.from_dict(params)

    # assert things.
    assert mg.number_of_nodes == 95
    assert mg.xy_of_center == (35, 55)
    assert [35, 55] in mg.xy_of_node
    assert mg.axis_units == ("smoot", "parsec")
    assert mg.axis_name == ("spam", "eggs")


def test_network_from_dict():
        pass# params = {}
    # >>> y_of_node = (0, 1, 2, 2)
    # >>> x_of_node = (0, 0, -1, 1)
    # >>> nodes_at_link = ((1, 0), (2, 1), (3, 1))
    # >>> grid = NetworkModelGrid((y_of_node, x_of_node), nodes_at_link)
    # >>> grid.x_of_node
    # array([ 0.,  0., -1.,  1.])
    # >>> grid.y_of_node
    # array([ 0.,  1.,  2.,  2.])
    # >>> grid.nodes_at_link
    # array([[0, 1],
    #        [2, 1],
    #        [1, 3]])


def test_voronoi_from_dict():
    pass
