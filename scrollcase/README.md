# scrollcase

Generates the split honeycomb scroll case (left half with mount disc, right
half, and stand) around a scroll mesh. See
[`docs/creating-scroll-case.md`](../docs/creating-scroll-case.md) for the
workflow and [`docs/scroll-case-config.md`](../docs/scroll-case-config.md)
for every config option.

```bash
uv sync
uv run scrollcase build -c examples/generic.toml -o out/
uv run pytest
```

Library use:

```python
from scrollcase import load_config
from scrollcase.pipeline import build

result = build(load_config("my-scroll.toml"), "out/")
```

## How it works

1. **Mesh stage** (`lining.py`, meshlib). Decimate and optionally smooth the
   scroll, fit the smallest enclosing cylinder, and rotate the scroll's wide
   direction into the split plane. Offset by `lining_offset` to get the
   cavity, split it at Y=0, extrude each half toward the split to remove
   undercuts, then offset by `wall_thickness` to get the lining wall.
2. **B-rep stage** (`case.py`, `mount_disc.py`, build123d). Shell, divider,
   mount disc, nubs, escape holes, labels, and stand, ported from the old
   OpenSCAD generator. `scad.py` provides OpenSCAD-style primitives so the
   port stays readable.
3. **Assembly** (`pipeline.py`). Each half is `(body ∪ wall) − cavity`.

meshlib's wheel bundles its own OpenCASCADE, which conflicts with
build123d's and crashes when both load in one process. The pipeline runs the
B-rep stage in `brep_worker` subprocesses and exchanges STLs. Don't import
`case` or build123d anywhere that imports `lining`.

`mount_disc.py` mirrors `OpenSCAD/Generic Mount Disc*.scad`, which the
interface plates and spindle bases still use. Keep them in sync.

`villa.2026-10` is checked against upstream's own code: run
`scripts/villa_reference.py` in an environment with villa's pinned
dependencies (see its docstring) to regenerate the reference data in
`tests/data/`. See [`docs/villa-2026-10-comparison.md`](../docs/villa-2026-10-comparison.md).

## Attribution

The alignment approach and mesh pipeline are adapted from the
[ScrollPrize/villa](https://github.com/ScrollPrize/villa/tree/main/foundation/scrollcase)
`scrollcase` package (MIT). `alignment.py` and `smallest_circle.py` are
derived from it; see `src/scrollcase/LICENSE.villa`.
