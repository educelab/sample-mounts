"""Subprocess entry point for the B-rep stage.

Usage: python -m scrollcase.brep_worker JOB.json

The job file (written by `pipeline`) holds the config, layout, part name, and
output STL path. This module must not import meshlib (see `lining`).
"""

import json
import os
import sys

from build123d import export_stl

from .case import PARTS
from .config import Layout, config_from_dict


def main(job_path: str) -> None:
    with open(job_path) as f:
        job = json.load(f)
    cfg = config_from_dict(job["config"])
    layout = Layout(**job["layout"])
    shape = PARTS[job["part"]](cfg, layout)
    # Write then rename, so the parent never sees a partial file
    tmp = job["out"] + ".partial"
    if not export_stl(shape, tmp, tolerance=job["tolerance"], angular_tolerance=0.1):
        raise RuntimeError(f"STL export failed for {job['part']}")
    os.replace(tmp, job["out"])


if __name__ == "__main__":
    main(sys.argv[1])
