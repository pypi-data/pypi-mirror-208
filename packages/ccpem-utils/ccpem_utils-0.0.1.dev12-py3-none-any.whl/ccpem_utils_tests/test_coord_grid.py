#
#     Copyright (C) 2021 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.
#

import unittest
import os
import shutil
import tempfile
import numpy as np
from ccpem_utils_tests import test_data
from ccpem_utils.model.coord_grid import (
    set_map_grid,
    set_cubic_map_grid,
    mapGridPositions,
)
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.scripts import shift_map_model_origin_zero
from ccpem_utils.map.mrc_map_utils import crop_map_grid
import mrcfile
import subprocess


class MapParseTests(unittest.TestCase):
    def setUp(self):
        """
        Setup test data and output directories.
        """
        self.test_data = os.path.dirname(test_data.__file__)
        self.test_dir = tempfile.mkdtemp(prefix="map_parse")
        # Change to test directory
        self._orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self._orig_dir)
        print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_model_grid(self):
        # read
        model_input = os.path.join(self.test_data, "5me2.pdb")
        origin, dim = set_map_grid(model_input, apix=(1.0, 1.0, 1.0))
        with mrcfile.new("5me2.mrc") as mrc:
            mrc.header.origin.x = origin[0]
            mrc.header.origin.y = origin[1]
            mrc.header.origin.z = origin[2]
            # dimensions
            mrc.header.cella.x = dim[0]
            mrc.header.cella.y = dim[1]
            mrc.header.cella.z = dim[2]
            # voxel_size
            mrc.voxel_size = (1.0, 1.0, 1.0)
            mrc.set_data(np.zeros((dim[2], dim[1], dim[0]), dtype="float32"))
        assert dim == (108, 110, 96)
        origin, dim = set_cubic_map_grid(model_input, apix=(1.0, 1.0, 1.0))
        assert dim == (110, 110, 110)

    def test_run_subprocess_shift_map_model_zero(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # crop
        crop_map_grid(wrapped_mapobj, new_dim=(71, 73, 58))
        # write
        with mrcfile.new("emd_3488_cropped.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)
            list_grid_points = mapGridPositions(
                wrapped_mapobj, atom_coord=(61.197, 39.327, 61.266), res_map=3.2
            )[:]
        assert len(list_grid_points) == 22
        ox, oy, oz = wrapped_mapobj.origin
        wrapped_mapobj.close()
        model_input = os.path.join(self.test_data, "5me2.pdb")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(shift_map_model_origin_zero.__file__)
                + " -m "
                + "emd_3488_cropped.mrc"
                + " -p "
                + model_input,
            ],
            shell=True,
        )
        shifted_map = (
            os.path.splitext(os.path.basename("emd_3488_cropped.mrc"))[0]
            + "_shifted.mrc"
        )
        with mrcfile.open(shifted_map, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
            list_grid_points_shifted = mapGridPositions(
                wrapped_mapobj,
                atom_coord=(61.197 - ox, 39.327 - oy, 61.266 - oz),
                res_map=3.2,
            )
        shifted_model = (
            os.path.splitext(os.path.basename(model_input))[0]
            + "_shifted"
            + os.path.splitext(model_input)[1]
        )
        assert os.path.isfile(shifted_map)
        assert os.path.isfile(shifted_model)
        assert np.array_equal(list_grid_points, list_grid_points_shifted)
