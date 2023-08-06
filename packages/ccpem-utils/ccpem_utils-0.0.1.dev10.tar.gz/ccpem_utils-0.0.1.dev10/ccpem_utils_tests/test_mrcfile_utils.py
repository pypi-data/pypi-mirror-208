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
import tempfile
import math
import shutil
from ccpem_utils_tests import test_data
from ccpem_utils.map.mrcfile_utils import crop_mrc_map, bin_mrc_map, pad_mrc_map
import mrcfile
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle


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
        # print(self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_map_crop(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        crop_mrc_map(
            map_input, new_dim=(71, 73, 58), map_output="emd_3488_cropped1.mrc"
        )
        # check1
        with mrcfile.open("emd_3488_cropped1.mrc", mode="r") as mrc:
            wrapped_mapobj1 = MapObjHandle(mrc)
            assert wrapped_mapobj1.data.shape == (58, 73, 71)

    def test_map_pad(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        pad_mrc_map(map_input, ext_dim=(10, 10, 10), map_output="emd_3488_padded.mrc")
        # check1
        with mrcfile.open("emd_3488_padded.mrc", mode="r") as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
            assert wrapped_mapobj.data.shape == (110, 110, 110)

    def test_downsample(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        bin_mrc_map(map_input, new_dim=50, map_output="emd_3488_downsampled_dim.mrc")
        # check
        with mrcfile.open("emd_3488_downsampled_dim.mrc", mode="r") as mrc:
            downsampled_mapobj = MapObjHandle(mrc)
            assert downsampled_mapobj.data.shape == (50, 50, 50)
            assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
            assert math.isclose(
                downsampled_mapobj.apix[0],
                2.1,
                rel_tol=0.00001,
            )
        bin_mrc_map(
            map_input,
            new_spacing=(2.1, 2.1, 2.1),
            map_output="emd_3488_downsampled.mrc",
        )
        # check
        with mrcfile.open("emd_3488_downsampled.mrc", mode="r") as mrc:
            downsampled_mapobj = MapObjHandle(mrc)
            assert downsampled_mapobj.data.shape == (50, 50, 50)
            assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
            assert math.isclose(
                downsampled_mapobj.apix[0],
                2.1,
                rel_tol=0.00001,
            )
