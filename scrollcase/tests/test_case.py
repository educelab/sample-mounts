import math

import pytest
from conftest import run_brep


def test_rotate_matches_openscad_order():
    result = run_brep(
        """
        import json
        from build123d import Location, Vector
        from scrollcase.scad import rotate
        p = rotate([90, 90, 0], Location(Vector(1, 0, 0))).position
        q = rotate([90, 90, 0], Location(Vector(0, 0, 1))).position
        print(json.dumps([[p.X, p.Y, p.Z], [q.X, q.Y, q.Z]]))
        """
    )
    # OpenSCAD rotate([90, 90, 0]): X first, then Y
    assert result[0] == pytest.approx([0, 0, -1], abs=1e-9)
    assert result[1] == pytest.approx([0, -1, 0], abs=1e-9)


@pytest.mark.parametrize("name", ["generic-112.5", "generic-65"])
def test_mount_disc_matches_openscad_dimensions(name):
    result = run_brep(
        f"""
        import json
        from scrollcase.mount_disc import MOUNT_DISCS
        d = MOUNT_DISCS["{name}"]
        s = d.solid()
        b = s.bounding_box()
        print(json.dumps(dict(volume=s.volume, zmin=b.min.Z, zmax=b.max.Z, xmax=b.max.X,
            r=d.diameter / 2, t=d.thickness, w=d.pocket_width, ph=d.pocket_height,
            hole_r=d.notch_diameter / 2 + (d.margin if d.widen_notch else 0),
            hole_len=d.notch_depth - d.margin)))
        """
    )
    r, t = result["r"], result["t"]
    expected = (
        math.pi * r**2 * t
        - result["w"] ** 2 * result["ph"]
        # Notch holes overshoot the rim by `margin`; only the inner part removes material
        - 2 * math.pi * result["hole_r"] ** 2 * result["hole_len"]
    )
    assert result["zmin"] == pytest.approx(-t, abs=1e-6)
    assert result["zmax"] == pytest.approx(0, abs=1e-6)
    assert result["xmax"] == pytest.approx(r, abs=1e-6)
    # The notch hole ends are flat while the rim is curved, hence the tolerance
    assert result["volume"] == pytest.approx(expected, rel=2e-4)


def test_mount_diameters_match_mount_discs():
    from scrollcase.config import MOUNT_DIAMETERS

    result = run_brep(
        """
        import json
        from scrollcase.mount_disc import MOUNT_DISCS
        print(json.dumps({k: d.diameter for k, d in MOUNT_DISCS.items()}))
        """
    )
    assert result == {k: v for k, v in MOUNT_DIAMETERS.items() if k != "none"}
