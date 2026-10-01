"""villa.2026-10 must reproduce upstream's case bodies exactly.

The reference data comes from upstream's own code, via
scripts/villa_reference.py. Upstream puts Z=0 at the scroll bottom; ours is
the case bottom, so our bodies are shifted by the layout's `scroll_z`.
"""

import json
from pathlib import Path

import pytest
from conftest import run_brep

REFERENCE = json.loads((Path(__file__).parent / "data/villa-2026-10-reference.json").read_text())


@pytest.mark.parametrize("ref", REFERENCE, ids=lambda r: f"r{r['radius']}-h{r['height']}")
def test_case_bodies_match_upstream(ref):
    ours = run_brep(
        f"""
        import json
        from build123d import Pos
        from scrollcase.case import left_body, right_body
        from scrollcase.config import Layout, config_from_dict

        cfg = config_from_dict(
            {{"style": "villa.2026-10", "label": {{"line1": "PHERC", "line2": "v3"}}}}
        )
        L = Layout.from_config(cfg, {ref["radius"]}, {ref["height"]})
        out = {{}}
        for side, fn in (("left", left_body), ("right", right_body)):
            body = Pos(0, 0, -L.scroll_z) * fn(cfg, L)
            b = body.bounding_box()
            out[side] = {{
                "volume": body.volume,
                "bbox": [b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z],
            }}
        print(json.dumps(out))
        """
    )
    for side in ("left", "right"):
        assert ours[side]["volume"] == pytest.approx(ref[side]["volume"], rel=1e-6), side
        assert ours[side]["bbox"] == pytest.approx(ref[side]["bbox"], abs=1e-4), side
