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
        "-r",
        "--res",
        required=True,
        type=float,
        help="Resolution to filter to",
    )
    parser.add_argument(
        "-f",
        "--fall",
        required=False,
        type=float,
        help="Filter fall-off [0 - 1]",
        default=0.3,
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
    mapfile: Union[str, pathlib.Path],
    resolution: float,
    filter_fall: float = 0.3,
    outdir: Union[str, pathlib.Path, None] = None,
):
    with mrcfile.open(mapfile, mode="r", permissive=True) as mrc:
        wrapped_mapobj = MapObjHandle(mrc)
        lowpass_filter(wrapped_mapobj, resolution=resolution, filter_fall=filter_fall)
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
    fall = args.fall
    if fall < 0 or fall > 1:
        raise argparse.ArgumentTypeError("fall (-f) should be between 0. and 1.0")
    lowpass_filter_map(args.map, args.res, filter_fall=args.fall, outdir=args.odir)


if __name__ == "__main__":
    main()
