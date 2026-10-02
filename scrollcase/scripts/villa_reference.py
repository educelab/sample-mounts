"""Build ScrollPrize/villa's case bodies as reference data for `villa.2026-10`.

Run with villa's own pinned dependencies, not this package's environment:

    uv venv --python 3.12 villa-env
    uv pip install --python villa-env/bin/python numpy scipy \\
        "build123d @ git+https://github.com/gumyr/build123d@30bbe96cfe0410e3c9cd3f1418ba9e227a546bce"
    villa-env/bin/python scripts/villa_reference.py VILLA_CHECKOUT OUT_DIR

VILLA_CHECKOUT is a clone of ScrollPrize/villa at 7d6a82c. Writes
`reference.json` (volumes and bounding boxes, used by the test suite) and
STEP files of each body for exact comparisons.
"""

import importlib
import json
import sys
import types
from pathlib import Path

from build123d import export_step

# Scroll (radius, height) pairs to build. Copy reference.json to
# tests/data/villa-2026-10-reference.json after regenerating.
SIZES = [(38.0, 155.0), (20.0, 60.0), (44.41, 167.58), (32.83, 178.06)]
LABEL = ("PHERC", "v3")


def load_villa_case(checkout: Path):
    """Import villa's case.py without running its package __init__, which imports meshlib."""
    package = types.ModuleType("villa_case")
    package.__path__ = [str(checkout / "foundation/scrollcase/src/scrollcase")]
    sys.modules["villa_case"] = package
    return importlib.import_module("villa_case.case")


def main(checkout: str, out_dir: str) -> None:
    case = load_villa_case(Path(checkout))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    reference = []
    for radius, height in SIZES:
        cfg = case.ScrollCaseConfig(
            scroll_height_mm=height,
            scroll_radius_mm=radius,
            label_line_1=LABEL[0],
            label_line_2=LABEL[1],
        )
        left, right = case.build_case(cfg)
        entry = {"radius": radius, "height": height}
        for side, solid in (("left", left), ("right", right)):
            b = solid.bounding_box()
            entry[side] = {
                "volume": solid.volume,
                "bbox": [b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z],
            }
            export_step(solid, str(out / f"villa-r{radius}-h{height}-{side}.step"))
        reference.append(entry)
        volumes = ", ".join(f"{side} {entry[side]['volume']:.1f}" for side in ("left", "right"))
        print(f"r={radius} h={height}: {volumes}")
    (out / "reference.json").write_text(json.dumps(reference, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
