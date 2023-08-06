import argparse
import mrcfile
import os
import pathlib
from typing import Union
from ccpem_utils.map.mrc_map_utils import lowpass_filter
from ccpem_utils.map.parse_mrcmapobj import MapObjHandle


def parse_args():
    parser = argparse.ArgumentParser(description="lowpass filter mrc map")
    parser.add_argument(
        "-m",
        "--map",
        required=True,
        help="Input map (MRC)",
    )
    parser.add_argument(
        "-odir",
        "--odir",
        required=False,
        default=None,
        help="Output directory",
    )

    return parser.parse_args()


def lowpass_filter_map(
    mapfile: Union[str, pathlib.Path], outdir: Union[str, pathlib.Path, None] = None
):
    with mrcfile.open(mapfile, mode="r", permissive=True) as mrc:
        wrapped_mapobj = MapObjHandle(mrc)
        lowpass_filter(wrapped_mapobj, resolution=7.5, filter_fall=0.5)
    map_basename = os.path.splitext(os.path.basename(mapfile))[0]
    if outdir:
        out_map = os.path.join(outdir, map_basename + "_lowpass.mrc")
    else:
        out_map = map_basename + "_lowpass.mrc"
    # write1
    with mrcfile.new(out_map, overwrite=True) as mrc:
        wrapped_mapobj.update_newmap_data_header(mrc)


def main():
    args = parse_args()
    lowpass_filter_map(args.map, outdir=args.odir)


if __name__ == "__main__":
    main()
