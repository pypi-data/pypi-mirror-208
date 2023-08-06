from ccpem_utils.map.parse_mrcmapobj import MapObjHandle
from ccpem_utils.map.mrc_map_utils import (
    crop_map_grid,
    pad_map_grid,
    downsample_apix,
)
import mrcfile
from typing import Sequence, Union
import os


def get_mapobjhandle(map_input):
    # read
    with mrcfile.open(map_input, mode="r", permissive=True) as mrc:
        wrapped_mapobj = MapObjHandle(mrc)
    return wrapped_mapobj


def write_newmapobj(mapobj, map_output):
    with mrcfile.new(map_output, overwrite=True) as mrc:
        mapobj.update_newmap_data_header(mrc)
    mapobj.close()


def crop_mrc_map(
    map_input: str,
    map_output: str = None,
    new_dim: Sequence[int] = None,
    contour: float = None,
    ext: int = 0,
    cubic: bool = False,
    inplace: bool = True,
    mask_map: MapObjHandle = None,
):
    mapobj = get_mapobjhandle(map_input)
    crop_map_grid(
        mapobj,
        new_dim=new_dim,
        contour=contour,
        ext=ext,
        cubic=cubic,
        inplace=inplace,
        mask_map=mask_map,
    )
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_cropped.mrc"
    write_newmapobj(mapobj, map_output)


def pad_mrc_map(
    map_input: str,
    ext_dim: Sequence[int],
    map_output: str = None,
    inplace: bool = True,
):
    mapobj = get_mapobjhandle(map_input)
    pad_map_grid(
        mapobj,
        ext_dim=ext_dim,
        inplace=inplace,
    )
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_padded.mrc"
    write_newmapobj(mapobj, map_output)


def bin_mrc_map(
    map_input: str,
    new_dim: Union[int, Sequence[int]] = None,
    new_spacing: Union[float, Sequence[float]] = None,
    map_output: str = None,
    inplace: bool = True,
):
    if not new_spacing and not new_dim:
        raise ValueError("Please provide either new_dim or new_spacing")
    mapobj = get_mapobjhandle(map_input)
    if isinstance(new_dim, int):
        max_dim = new_dim
        new_spacing = (
            max(
                mapobj.x_size() * mapobj.apix[0],
                mapobj.y_size() * mapobj.apix[1],
                mapobj.z_size() * mapobj.apix[2],
            )
            / max_dim
        )

    elif new_dim:
        new_spacing = (
            (mapobj.x_size() / new_dim[0]) * mapobj.apix[0],
            (mapobj.y_size() / new_dim[1]) * mapobj.apix[1],
            (mapobj.z_size() / new_dim[2]) * mapobj.apix[2],
        )
    downsample_apix(
        mapobj,
        new_spacing=new_spacing,
        inplace=inplace,
    )
    if not map_output:
        map_output = os.path.splitext(map_input)[0] + "_binned.mrc"
    write_newmapobj(mapobj, map_output)
