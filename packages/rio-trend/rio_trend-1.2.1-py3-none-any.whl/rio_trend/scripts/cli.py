"""Main CLI."""
import datetime
import sys

import click
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.rio.options import creation_options
from rasterio.transform import guard_transform
from rio_trend.workers import color_worker

from joblib import Parallel, delayed
import concurrent
import multiprocessing

jobs_opt = click.option(
    "--jobs",
    "-j",
    type=int,
    default=4,
    help="Number of jobs to run simultaneously, Use -1 for all cores, default: 4",
)


def check_jobs(jobs):
    """Validate number of jobs."""
    if jobs == 0:
        raise click.UsageError("Jobs must be >= 1 or == -1")
    elif jobs < 0:
        import multiprocessing

        jobs = multiprocessing.cpu_count()
    return jobs


help_text = """
+──────────+──────────+──────────+──────────+
|          | slope<0  | slope=0  | slope>0  |
+──────────+──────────+──────────+──────────+
| p<=0.05  | -1       | 0        | +1       |
| p>0.05   | -2       | 0        | +2       |
+──────────+──────────+──────────+──────────+
exception: -9999
"""


@click.command("trend")
@jobs_opt
@click.option(
    "--out-dtype",
    "-d",
    type=click.Choice(["uint8", "uint16"]),
    help="Integer data type for output data, default: same as input",
)
# @click.option(
#     '--mask-path',
#     "-m",
#     type=click.Path(exists=True),
#     help="mask file"
# )
@click.argument("src_path", type=click.Path(exists=True))
@click.argument("dst_path", type=click.Path(exists=False))
@click.pass_context
@creation_options
def trend(ctx, jobs, out_dtype, src_path, dst_path, creation_options):
    """long help"""

    with rasterio.open(src_path) as src:
        opts = src.profile.copy()

    opts.update(**creation_options)
    opts["transform"] = guard_transform(opts["transform"])

    out_dtype = out_dtype if out_dtype else opts["dtype"]
    opts["dtype"] = rasterio.float32

    nodata = np.finfo(np.float32).min
    opts.update(count=3, nodata=nodata)

    args = {"out_dtype": out_dtype, "nodatavals": src.nodatavals, "nodata": src.nodata}

    print(args)

    # Just run this for validation this time
    # parsing will be run again within the worker
    # where its returned value will be used
    try:
        # parse_operations(args["ops_string"])
        pass
    except ValueError as e:
        raise click.UsageError(str(e))

    print(help_text)

    jobs = check_jobs(jobs)
    print("jobs =", jobs)

    start_time = datetime.datetime.now()
    print(start_time)

    with rasterio.open(src_path) as src, rasterio.open(dst_path, "w", **opts) as dst:
        windows = [window for ij, window in dst.block_windows()]

        print("windows:", len(windows))

        total_n_jobs = len(windows)

        src_data = ((src.read(window=win), win) for win in windows)

        result = Parallel(n_jobs=16, verbose=10)(
            delayed(color_worker)([data], window, args) for data, window in src_data
        )

        for data, window in zip(result, windows):
            dst.write(data, window=window)

        # with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        #     futures = []
        #     for window, ij in windows:
        #         future = executor.submit(
        #             color_worker, [src.read(window=window)], window, ij, args
        #         )
        #         future.add_done_callback(lambda f: print(".", end="", flush=True))
        #         futures.append(future)
        #     for (window, ij), result in zip(windows, futures):
        #         dst.write(result.result(), window=window)
    print("done")
    # with rasterio.open(dst_path, "w", **opts) as dest:
    #     with rasterio.open(src_path) as src:
    #         rasters = [src]
    #         for window in windows:
    #             arr = color_worker(rasters, window, args)
    #             dest.write(arr, window=window)

    #         # dest.colorinterp = src.colorinterp

    print("Time consumed:", datetime.datetime.now() - start_time)
