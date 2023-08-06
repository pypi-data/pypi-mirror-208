from __future__ import annotations
import numpy as np
import copy
from typing import Union


class MapObjHandle(object):
    def __init__(self, mapobject, datacopy=True):
        if type(mapobject) is MapObjHandle:
            super(MapObjHandle, self).__init__()
            if not datacopy:
                self.__dict__ = mapobject.__dict__.copy()
            else:
                try:
                    mapobject.close()
                    self.mrc = mapobject.mrc
                except AttributeError:  # input map object detached
                    pass
                for k, v in mapobject.__dict__.items():
                    try:
                        self.__dict__[k] = copy.deepcopy(v)
                    except TypeError:  # skip file object pickle failures
                        pass
        else:
            super(MapObjHandle, self).__init__()
            # map data and header details
            # add other attributes?
            self.mrc = mapobject
            self.class_name = self.mrc.__class__.__name__
            if datacopy:
                self.initialize(inplace=False)
            else:
                self.initialize(inplace=True)

    def shape(self):
        return self.data.shape

    def min(self):
        return np.amin(self.data)

    def max(self):
        return np.amax(self.data)

    def std(self):
        return np.std(self.data)

    def x_size(self):
        """
        size of the map array in x direction.
        """
        return self.data.shape[2]

    def y_size(self):
        """
        size of the map array in y direction.
        """
        return self.data.shape[1]

    def z_size(self):
        """
        size of the map array in z direction.
        """
        return self.data.shape[0]

    def copy(self, deep=True, detach=True):
        """
        Copy contents to a new object
        """
        # create MapEdit object
        copymap = MapObjHandle(self)
        # detach from initial mrc mapfile
        if detach:
            copymap.mrc = None
        # copy data and header
        copymap.origin = copy.deepcopy(self.origin)
        if deep:
            copymap.data = self.data.copy()
        else:
            copymap.data = self.data
        copymap.apix = copy.deepcopy(self.apix)
        copymap.dim = copy.deepcopy(self.dim)
        return copymap

    def data_copy(self):
        """
        Copy data (not to modify inplace)
        """
        if self.class_name == "MrcFile":
            self.data = self.mrc.data.copy()
        elif self.class_name == "Map":
            self.data = self.mrc.fullMap.copy()

    def reinitialize_data(self, inplace=False):
        """
        Initialize or re-initialize data
        """
        if inplace:
            if self.class_name == "MrcFile":
                self.data = self.mrc.data
            elif self.class_name == "Map":
                self.data = self.mrc.fullMap
        else:
            self.data_copy()

    def reinitialize_header(self):
        """
        Initialize or re-initialize header
        """
        if self.class_name == "MrcFile":
            self.origin = self.mrc.header.origin.item()
            self.apix = self.mrc.voxel_size.item()
            self.dim = self.mrc.header.cella.item()
            self.nstart = (
                self.mrc.header.nxstart,
                self.mrc.header.nystart,
                self.mrc.header.nzstart,
            )
        elif self.class_name == "Map":
            self.origin = tuple(self.mrc.origin)
            self.apix = (
                round(self.mrc.header[10] / self.mrc.header[7], 2),
                round(self.mrc.header[11] / self.mrc.header[8], 2),
                round(self.mrc.header[12] / self.mrc.header[9], 2),
            )
            self.dim = (
                self.x_size() * self.apix[0],
                self.y_size() * self.apix[1],
                self.z_size() * self.apix[2],
            )
            self.nstart = self.mrc.header[4:7]
        else:
            raise TypeError(
                """Only MrcFile and TEMPY Map objects currently
                    supported"""
            )

    def initialize(self, inplace=False):
        """
        Initialize/re-initialize data/header
        """
        self.reinitialize_data(inplace=inplace)
        self.reinitialize_header()

    # update map header records
    def update_input_header(self):
        """
        Update map header records to current values
        """
        if self.class_name == "MrcFile":
            # origin
            self.mrc.header.origin.x = self.origin[0]
            self.mrc.header.origin.y = self.origin[1]
            self.mrc.header.origin.z = self.origin[2]
            # dimensions
            self.mrc.header.cella.x = self.dim[0]
            self.mrc.header.cella.y = self.dim[1]
            self.mrc.header.cella.z = self.dim[2]
            # voxel_size
            if type(self.apix) is float:
                self.mrc.voxel_size = (self.apix, self.apix, self.apix)
            else:
                self.mrc.voxel_size = self.apix
            self.mrc.header.nxstart = self.nstart[0]
            self.mrc.header.nystart = self.nstart[1]
            self.mrc.header.nzstart = self.nstart[2]
        elif self.class_name == "Map":
            # origin
            self.mrc.origin[0] = self.origin[0]
            self.mrc.origin[1] = self.origin[1]
            self.mrc.origin[2] = self.origin[2]
            # tempy takes a single voxel_size [TODO]
            self.mrc.apix = self.apix[0]
            self.mrc.header[4] = self.nstart[0]
            self.mrc.header[5] = self.nstart[1]
            self.mrc.header[6] = self.nstart[2]

    @staticmethod
    def compare_tuple(tuple1, tuple2):
        for val1, val2 in zip(tuple1, tuple2):
            if type(val2) is float:
                if round(val1, 2) != round(val2, 2):
                    return False
            else:
                if val1 != val2:
                    return False
        return True

    # update map array data
    def update_input_data(self):
        """
        Update input data array with current
        """
        if self.class_name == "MrcFile":
            if self.compare_tuple(self.data.shape, self.mrc.data.shape):
                self.mrc.data[:] = self.data
            else:
                self.mrc.set_data(self.data)
        elif self.class_name == "Map":
            self.mrc.fullMap[:] = self.data

    def update_input_data_header(self):
        """
        Update data and header with current values
        """
        self.update_input_data()
        self.update_input_header()

    def close(self):
        if self.class_name == "MrcFile":
            self.mrc.close()
        elif self.class_name == "Map":
            self.mrc.fullMap = None
            self.mrc = None

    # update map header records
    def update_newmap_header(self, newmap):
        """
        Copy current values to a newmap (mrcfile/ TEMPy Map obj)
        """
        if newmap.__class__.__name__ == "MrcFile":
            # origin
            newmap.header.origin.x = self.origin[0]
            newmap.header.origin.y = self.origin[1]
            newmap.header.origin.z = self.origin[2]
            # dimensions
            newmap.header.cella.x = self.dim[0]
            newmap.header.cella.y = self.dim[1]
            newmap.header.cella.z = self.dim[2]
            # voxel_size
            newmap.voxel_size = self.apix
            newmap.header.nxstart = self.nstart[0]
            newmap.header.nystart = self.nstart[1]
            newmap.header.nzstart = self.nstart[2]

        elif newmap.__class__.__name__ == "Map":
            # origin
            newmap.origin[0] = self.origin[0]
            newmap.origin[1] = self.origin[1]
            newmap.origin[2] = self.origin[2]
            # voxel_size
            newmap.apix = self.apix[0]
            newmap.header[4] = self.nstart[0]
            newmap.header[5] = self.nstart[1]
            newmap.header[6] = self.nstart[2]

    # update map array data
    def update_newmap_data(self, newmap):
        """
        Update new map (mrcfile/TEMPy) data array with current
        """
        if newmap.__class__.__name__ == "MrcFile":
            if str(self.data.dtype) == "float64":
                newmap.set_data(self.data.astype("float32", copy=False))
            else:
                newmap.set_data(self.data)
        elif newmap.__class__.__name__ == "Map":
            newmap.fullMap[:] = self.data

    def update_newmap_data_header(self, newmap):
        """
        Update data and header of mrcfile map obj with current values
        """
        self.update_newmap_data(newmap)
        self.update_newmap_header(newmap)

    def update_header_by_data(self):
        self.dim = (
            self.x_size() * self.apix[0],
            self.y_size() * self.apix[1],
            self.z_size() * self.apix[2],
        )

    def set_attributes_tempy(self):
        """
        Set class attributes to use with TEMPy functions
        """
        self.fullMap = self.data
        self.nxstart = self.nstart[0]
        self.nystart = self.nstart[1]
        self.nzstart = self.nstart[2]

    def set_dim_apix(self, apix):
        """
        Set dimensions (Angstroms) given voxel size
        """
        self.apix = apix
        self.dim = (
            self.x_size() * self.apix[0],
            self.y_size() * self.apix[1],
            self.z_size() * self.apix[2],
        )

    def set_apix_dim(self, dim):
        """
        Set voxel size given dimensions (Angstroms) of Grid
        """
        self.dim = dim
        self.apix = (
            np.around(self.dim[0] / self.x_size(), decimals=3),
            np.around(self.dim[1] / self.y_size(), decimals=3),
            np.around(self.dim[2] / self.z_size(), decimals=3),
        )

    def set_apix_tempy(self):
        """
        Set apix to single float value for using TEMPy functions
        """
        if isinstance(self.apix, tuple):
            if self.apix[0] == self.apix[1] == self.apix[2]:
                self.apix = self.apix[0]
            else:
                self.downsample_apix(max(self.apix), inplace=True)
                self.apix = self.apix[0]

    def shift_origin(self, new_origin: Union[list, tuple, np.ndarray]):
        """
        Shift map to given origin
        """
        assert len(new_origin) == 3
        self.origin = tuple(new_origin)

    def shift_nstart(self, new_nstart: Union[list, tuple, np.ndarray]):
        """
        Update nstart record to given nstart
        """
        assert len(new_nstart) == 3
        self.nstart = tuple(new_nstart)

    def fix_origin(self):
        """
        Set origin record based on nstart if non-zero
        """
        if self.origin[0] == 0.0 and self.origin[1] == 0.0 and self.origin[2] == 0.0:
            if self.nstart[0] != 0 or self.nstart[1] != 0 or self.nstart[2] != 0:
                self.set_apix_as_tuple()
                # origin
                self.origin = (
                    self.nstart[0] * self.apix[0],
                    self.nstart[1] * self.apix[1],
                    self.nstart[2] * self.apix[2],
                )

    def set_apix_as_tuple(self):
        if isinstance(self.apix, (int, float)):
            self.apix = (self.apix, self.apix, self.apix)
