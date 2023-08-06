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
import subprocess
from ccpem_utils.scripts import get_map_parameters
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.map.mrc_map_utils import (
    crop_map_grid,
    pad_map_grid,
    interpolate_to_grid,
    downsample_apix,
    lowpass_filter,
)
import numpy as np
import mrcfile
from ccpem_utils.other.calc import get_ccc


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
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_map_crop(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # copy
        wrapped_mapobj_copy = wrapped_mapobj.copy()
        # process1
        crop_map_grid(wrapped_mapobj, new_dim=(71, 73, 58))
        # write1
        with mrcfile.new("emd_3488_cropped1.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)
        wrapped_mapobj.close()
        # check1
        with mrcfile.open("emd_3488_cropped1.mrc", mode="r") as mrc:
            wrapped_mapobj1 = MapObjHandle(mrc)
            assert wrapped_mapobj1.data.shape == (58, 73, 71)
        # process2
        wrapped_mapobj2 = crop_map_grid(
            wrapped_mapobj_copy, contour=0.125, ext=3, inplace=False
        )
        # write
        with mrcfile.new("emd_3488_cropped2.mrc", overwrite=True) as mrc:
            wrapped_mapobj2.update_newmap_data_header(mrc)
        # check
        with mrcfile.open("emd_3488_cropped2.mrc", mode="r") as mrc:
            wrapped_mapobj2 = MapObjHandle(mrc)
            assert wrapped_mapobj2.data.shape == (58, 73, 71)
        assert (
            get_ccc(
                wrapped_mapobj1.data,
                wrapped_mapobj2.data,
            )
            == 1.0
        )
        # process3
        wrapped_mapobj3 = crop_map_grid(
            wrapped_mapobj_copy, contour=0.125, ext=3, cubic=True, inplace=False
        )
        assert wrapped_mapobj3.data.shape == (73, 73, 73)
        maskmap = wrapped_mapobj_copy.copy()
        maskmap.data = wrapped_mapobj_copy.data >= 0.125
        # mask input
        crop_map_grid(wrapped_mapobj_copy, mask_map=maskmap, ext=3, cubic=True)
        wrapped_mapobj3.data = wrapped_mapobj3.data * (wrapped_mapobj3.data >= 0.125)
        assert (
            get_ccc(
                wrapped_mapobj3.data,
                wrapped_mapobj_copy.data,
            )
            == 1
        )

    def test_map_pad(self):
        # read
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # process
        pad_map_grid(wrapped_mapobj, ext_dim=(10, 10, 10))
        min_map = wrapped_mapobj.data.min()
        # write
        with mrcfile.new("emd_3488_padded.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)
        wrapped_mapobj.close()
        # check1
        with mrcfile.open("emd_3488_padded.mrc", mode="r") as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
            assert wrapped_mapobj.data.shape == (110, 110, 110)
        min_padded_map = wrapped_mapobj.data.min()
        assert min_map == min_padded_map  # padding filled with min

    def test_interpolate_downsample(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        # copy
        wrapped_mapobj_copy = wrapped_mapobj.copy()
        # interpolate
        interpolate_to_grid(
            wrapped_mapobj, (50, 50, 50), (2.1, 2.1, 2.1), (0.0, 0.0, 0.0)
        )
        # write
        with mrcfile.new("emd_3488_interpolated.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)
        wrapped_mapobj.close()
        # check1
        with mrcfile.open("emd_3488_interpolated.mrc", mode="r") as mrc:
            interpolated_mapobj = MapObjHandle(mrc)
            assert interpolated_mapobj.data.shape == (50, 50, 50)
            assert interpolated_mapobj.origin == (0.0, 0.0, 0.0)
            assert math.isclose(
                interpolated_mapobj.apix[0],
                2.1,
                rel_tol=0.00001,
            )
        # downsample
        downsample_apix(wrapped_mapobj_copy, (2.1, 2.1, 2.1))
        # write
        with mrcfile.new("emd_3488_downsampled.mrc", overwrite=True) as mrc:
            wrapped_mapobj_copy.update_newmap_data_header(mrc)
        # check2
        with mrcfile.open("emd_3488_downsampled.mrc", mode="r") as mrc:
            downsampled_mapobj = MapObjHandle(mrc)
            assert downsampled_mapobj.data.shape == (50, 50, 50)
            assert downsampled_mapobj.origin == (0.0, 0.0, 0.0)
            assert math.isclose(
                downsampled_mapobj.apix[0],
                2.1,
                rel_tol=0.00001,
            )
        assert (
            get_ccc(
                interpolated_mapobj.data,
                downsampled_mapobj.data,
            )
            == 1.0
        )

    def test_lowpass_filter(self):
        emanmapfile = os.path.join(self.test_data, "1ake_molmap45_tanhlp_eman2.mrc")
        emanmapobj = mrcfile.open(emanmapfile, mode="r")
        map_input = os.path.join(self.test_data, "1ake_molmap45.mrc")
        with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
            wrapped_mapobj = MapObjHandle(mrc)
        lowpass_filter(wrapped_mapobj, resolution=7.5, filter_fall=0.5)
        # write1
        with mrcfile.new("1ake_molmap45_lowpass.mrc", overwrite=True) as mrc:
            wrapped_mapobj.update_newmap_data_header(mrc)

        self.assertAlmostEqual(
            np.corrcoef(wrapped_mapobj.data.ravel(), emanmapobj.data.ravel())[0][1],
            1.0,
            2,
        )
        wrapped_mapobj.close()

    def test_run_subprocess_get_map_parameters(self):
        map_input = os.path.join(self.test_data, "emd_3488.mrc")
        subprocess.call(
            [
                "python3 "
                + os.path.realpath(get_map_parameters.__file__)
                + " -m "
                + map_input
                + " -odir "
                + self.test_dir,
            ],
            shell=True,
        )
        assert os.path.isfile(
            os.path.join(self.test_dir, "emd_3488_map_parameters.json")
        )
        assert math.isclose(
            os.stat(
                os.path.join(self.test_dir, "emd_3488_map_parameters.json")
            ).st_size,
            275,
            rel_tol=0.05,
        )
