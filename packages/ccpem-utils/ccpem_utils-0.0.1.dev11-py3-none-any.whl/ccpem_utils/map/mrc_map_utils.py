#
#     Copyright (C) 2019 CCP-EM
#
#     This code is distributed under the terms and conditions of the
#     CCP-EM Program Suite Licence Agreement as a CCP-EM Application.
#     A copy of the CCP-EM licence can be obtained by writing to the
#     CCP-EM Secretary, RAL Laboratory, Harwell, OX11 0FA, UK.

from ccpem_utils.other.cluster import generate_kdtree
import numpy as np
from ccpem_utils.map.array_utils import (
    crop_array,
    pad_array,
    tanh_lowpass,
    apply_filter,
    calculate_fft,
    calculate_ifft,
)
from typing import Sequence
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from scipy.ndimage import map_coordinates


def crop_map_grid(
    input_map: MapObjHandle,
    new_dim: Sequence[int] = None,
    contour: float = None,
    ext: int = 0,
    cubic: bool = False,
    inplace: bool = True,
    mask_map: MapObjHandle = None,
):
    """
    Crop grid based on given dimensions or contour or mask

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_dim:
        new dimensions to crop to
    :contour: float, optional
        map threshold (slices with all values lower than this are cropped)
    :ext: int, optional
        number of pixels/voxels as padding
    :mask_map: MapObjHandle
        mask to be applied before cropping (slices with all zeros are cropped)
    :cubic: bool
        whether to crop to a cubic box?
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    cropped map object if not inplace
    """
    if mask_map:
        cropped_array, start = crop_array(
            arr=input_map.data,
            new_dim=new_dim,
            contour=contour,
            cubic=cubic,
            ext=ext,
            mask_array=mask_map.data,
        )
    else:
        cropped_array, start = crop_array(
            arr=input_map.data,
            new_dim=new_dim,
            contour=contour,
            cubic=cubic,
            ext=ext,
        )
    ox = input_map.origin[0] + start[0] * input_map.apix[0]
    oy = input_map.origin[1] + start[1] * input_map.apix[1]
    oz = input_map.origin[2] + start[2] * input_map.apix[2]
    nstx = input_map.nstart[0] + start[0]
    nsty = input_map.nstart[1] + start[1]
    nstz = input_map.nstart[2] + start[2]
    if inplace:
        input_map.origin = (ox, oy, oz)
        input_map.data = cropped_array
        input_map.nstart = (nstx, nsty, nstz)
        input_map.update_header_by_data()
    else:
        newmap = input_map.copy()
        newmap.origin = (ox, oy, oz)
        newmap.data = cropped_array
        newmap.nstart = (nstx, nsty, nstz)
        newmap.update_header_by_data()
        return newmap


def pad_map_grid(
    input_map: MapObjHandle,
    ext_dim: Sequence[int],
    inplace: bool = True,
):
    """
    Pad grid based on given dimensions

    Arguments
    ---------
    :input_map: MapObjHandle
        input Map object
    :ext_dim:
        extension to add to each dimension (nx,ny,nz)
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    New padded map object if not inplace, otherwise padded input_map
    """
    padded_array, start = pad_array(
        arr=input_map.data, nx=ext_dim[0], ny=ext_dim[1], nz=ext_dim[2]
    )
    # shift origin
    ox = input_map.origin[0] - start[0] * input_map.apix[0]
    oy = input_map.origin[1] - start[1] * input_map.apix[1]
    oz = input_map.origin[2] - start[2] * input_map.apix[2]
    nstx = input_map.nstart[0] - start[0]
    nsty = input_map.nstart[1] - start[1]
    nstz = input_map.nstart[2] - start[2]
    if inplace:
        input_map.origin = (ox, oy, oz)
        input_map.data = padded_array
        input_map.nstart = (nstx, nsty, nstz)
        input_map.update_header_by_data()
    else:
        newmap = input_map.copy()
        newmap.origin = (ox, oy, oz)
        newmap.data = padded_array
        newmap.nstart = (nstx, nsty, nstz)
        newmap.update_header_by_data()
        return newmap


# interpolate to a new grid
def interpolate_to_grid(
    input_map, new_gridshape, new_spacing, new_origin, reset_nstart=False, inplace=True
):
    """
    Interpolate to a new map grid given new shape, spacing and origin

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_gridshape: tuple
        new dimensions to interpolate to
    :new_spacing: float
        spacing of the new grid
    :new_origin: float
        origin of the new grid
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    new map object with new grid properties
    """
    if not isinstance(new_spacing, tuple):
        new_spacing = (new_spacing, new_spacing, new_spacing)
    ox, oy, oz = (input_map.origin[0], input_map.origin[1], input_map.origin[2])
    o1x, o1y, o1z = (
        float(new_origin[0]),
        float(new_origin[1]),
        float(new_origin[2]),
    )
    scale = (
        float(new_spacing[0]) / input_map.apix[0],
        float(new_spacing[1]) / input_map.apix[1],
        float(new_spacing[2]) / input_map.apix[2],
    )
    offset = (o1x - ox, o1y - oy, o1z - oz)

    gridshape = new_gridshape
    # get z, y and x indices
    grid_indices = np.indices(gridshape, dtype=np.uint16)
    z_ind = grid_indices[0]
    z_ind.ravel()
    y_ind = grid_indices[1]
    y_ind.ravel()
    x_ind = grid_indices[2]
    x_ind.ravel()
    z_ind = ((offset[2]) / input_map.apix[2]) + scale[2] * z_ind
    y_ind = ((offset[1]) / input_map.apix[1]) + scale[1] * y_ind
    x_ind = ((offset[0]) / input_map.apix[0]) + scale[0] * x_ind
    # cubic interpolation by default
    new_array = map_coordinates(input_map.data, [z_ind, y_ind, x_ind], mode="nearest")

    if inplace:
        input_map.data = new_array.reshape(gridshape)
        input_map.origin = (o1x, o1y, o1z)
        if reset_nstart:
            input_map.nstart = (
                int(round(o1x / new_spacing[0])),
                int(round(o1y / new_spacing[1])),
                int(round(o1z / new_spacing[2])),
            )
        input_map.set_dim_apix(new_spacing)
        input_map.update_header_by_data()
    else:
        newmap = input_map.copy(deep=False)
        newmap.data = new_array.reshape(gridshape)
        newmap.origin = (o1x, o1y, o1z)
        if reset_nstart:
            newmap.nstart = (
                int(round(o1x / new_spacing[0])),
                int(round(o1y / new_spacing[1])),
                int(round(o1z / new_spacing[2])),
            )
        newmap.set_dim_apix(new_spacing)
        newmap.update_header_by_data()
        return newmap


# interpolate to a new grid with different voxel size
def downsample_apix(input_map, new_spacing, inplace=True):
    """
    Downsample map based on voxel size

    Arguments
    ---------
    :input_map: MapObjHandle
        input map object
    :new_spacing: float
        spacing of the new grid
    :inplace: bool
        whether to modify existing map object inplace or create new?

    Return
    ------
    new map object with downsampled grid
    """
    if not isinstance(new_spacing, tuple):
        new_spacing = (new_spacing, new_spacing, new_spacing)
    apix_ratio = (
        input_map.apix[0] / new_spacing[0],
        input_map.apix[1] / new_spacing[1],
        input_map.apix[2] / new_spacing[2],
    )
    grid_shape = (
        int(round(input_map.z_size() * apix_ratio[2])),
        int(round(input_map.y_size() * apix_ratio[1])),
        int(round(input_map.x_size() * apix_ratio[0])),
    )
    if inplace:
        interpolate_to_grid(
            input_map, grid_shape, new_spacing, input_map.origin, inplace=inplace
        )
    else:
        return interpolate_to_grid(
            input_map, grid_shape, new_spacing, input_map.origin, inplace=inplace
        )


def lowpass_filter(
    input_map: MapObjHandle,
    resolution: float,
    filter_fall: float = 0.3,
    new_spacing: Sequence[float] = None,
    inplace: bool = True,
):
    """Lowpass filter a given map (MapObjHandle instance)

    :param input_map: input map instance to lowpass filter
    :type input_map: MapObjHandle
    :param resolution: resolution for lowpass cutoff
    :type resolution: float
    :param filter_fall: smoothness of falloff [0-> tophat,1.0-> gaussian],
        defaults to 0.3
    :type filter_fall: float
    :param new_spacing: filtered map spacing, defaults to None (current spacing)
    :type new_spacing: Sequence[float], optional
    :param inplace: to overwrite map array inplace?, defaults to True
    :type inplace: bool, optional
    """
    ftmap = calculate_fft(input_map.data, keep_shape=False)
    cutoff = min(0.5, max(input_map.apix) / resolution)
    tanh_filter = tanh_lowpass(
        input_map.data.shape,
        cutoff=cutoff,
        fall=filter_fall,
        keep_shape=False,
    )
    ftmap[:] = np.fft.fftshift(ftmap, axes=(0, 1))
    filt_ftmap = apply_filter(ftmap, tanh_filter)
    filt_ftmap[:] = np.fft.ifftshift(filt_ftmap, axes=(0, 1))
    filt_map = calculate_ifft(filt_ftmap, output_shape=input_map.data.shape)

    if inplace:
        input_map.data = filt_map
    else:
        newmap = input_map.copy(deep=False)
        newmap.data = filt_map

    if new_spacing is not None:
        if inplace:
            downsample_apix(input_map, new_spacing, inplace=True)
        else:
            return downsample_apix(newmap, new_spacing, inplace=True)


def mrcmap_kdtree(map_instance):
    """
    Returns the KDTree of coordinates from a mrc map grid.

    Arguments:
        *map_instance*
            MrcFile or MapObjHandle Map instance.
    """
    if map_instance.__class__.__name__ == "MrcFile":
        origin = map_instance.header.origin.item()
        apix = map_instance.voxel_size.item()
        nz, ny, nx = map_instance.data.shape
    else:
        origin = map_instance.origin
        apix = map_instance.apix
        nz, ny, nx = map_instance.data.shape

    # convert to real coordinates
    zg, yg, xg = np.mgrid[0:nz, 0:ny, 0:nx]
    # to get indices in real coordinates
    zg = zg * apix[2] + origin[2] + apix[2] / 2.0
    yg = yg * apix[1] + origin[1] + apix[1] / 2.0
    xg = xg * apix[0] + origin[0] + apix[0] / 2.0
    indi = list(zip(xg.ravel(), yg.ravel(), zg.ravel()))
    gridtree = generate_kdtree(indi, leaf_size=42)
    return gridtree, indi
