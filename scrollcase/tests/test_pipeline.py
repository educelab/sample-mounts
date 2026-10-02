import meshlib.mrmeshpy as mm
import pytest
from conftest import inside, is_closed

from scrollcase.config import ConfigError, config_from_dict
from scrollcase.pipeline import build
from scrollcase.split import profile_for


def _bounds(mesh):
    b = mesh.computeBoundingBox()
    return (b.min.x, b.min.y, b.min.z), (b.max.x, b.max.y, b.max.z)


@pytest.fixture(scope="module")
def full_case(tmp_path_factory):
    cfg = config_from_dict(
        {
            "name": "t",
            "nubs": {"positions": [[-44, 20], [44, 150]]},
            "escape_holes": {"enabled": True},
            "label": {"line1": "TEST", "line2": "V1"},
        }
    )
    out = tmp_path_factory.mktemp("full")
    result = build(cfg, out)
    meshes = {k: mm.loadMesh(p) for k, p in result.outputs.items()}
    return result.layout, meshes


def test_outputs_are_closed_single_bodies(full_case):
    _, meshes = full_case
    assert set(meshes) == {"scroll", "left", "right", "stand"}
    for name, mesh in meshes.items():
        assert is_closed(mesh), name
        assert len(mm.getAllComponents(mesh)) == 1, name


def test_halves_fit_layout(full_case):
    L, meshes = full_case
    r = L.outer_diameter / 2
    (lx0, ly0, lz0), (lx1, ly1, lz1) = _bounds(meshes["left"])
    (rx0, ry0, rz0), (rx1, ry1, rz1) = _bounds(meshes["right"])

    # Left carries the 112.5mm mount disc below Z=0, right stops at the split
    assert (lz0, lz1) == pytest.approx((-12.5, L.outer_height), abs=1e-3)
    assert lx1 == pytest.approx(112.5 / 2, abs=0.05)
    assert ry0 == pytest.approx(0, abs=1e-3)
    assert (rz0, rz1) == pytest.approx((0, L.outer_height), abs=1e-3)
    # Marker ring tori stand 0.5mm proud of the shell
    assert rx1 == pytest.approx(r + 0.5, abs=0.05)
    assert ry1 == pytest.approx(r + 0.5, abs=0.05)


def test_scroll_cavity_and_lining(full_case):
    L, meshes = full_case
    mid = L.scroll_z + L.scroll_height / 2
    lining_r = L.cavity_diameter / 2 + L.wall / 2
    for side, sign in (("left", -1), ("right", 1)):
        mesh = meshes[side]
        assert not inside(mesh, (0, sign * 10, mid)), side
        assert inside(mesh, (0, sign * lining_r, mid)), side
        # Gap between lining and shell is empty
        gap_r = (L.lining_diameter + L.inner_diameter) / 4
        assert not inside(mesh, (0, sign * gap_r, mid)), side


def test_nubs_and_sockets(full_case):
    _, meshes = full_case
    for x, z in ([-44, 20], [44, 150]):
        assert inside(meshes["left"], (-x, 1.0, z))
        assert not inside(meshes["right"], (-x, 1.0, z))
        assert inside(meshes["right"], (-x, 3.2, z))


def test_generic_open_cradle(tmp_path):
    cfg = config_from_dict({"name": "g", "shell": {"open_top": True}})
    result = build(cfg, tmp_path, parts=("left",))
    mesh = mm.loadMesh(result.outputs["left"])
    assert is_closed(mesh)
    # The upper shell is scooped away, so the shell wall near the top is gone
    L = result.layout
    assert not inside(mesh, (0, -(L.outer_diameter / 2 - L.wall / 2), L.outer_height - 1))


@pytest.fixture(scope="module")
def curved_case(tmp_path_factory):
    cfg = config_from_dict(
        {
            "name": "c",
            "split": {"type": "curve"},
            "nubs": {"positions": [[-44, 20], [44, 150]]},
            "escape_holes": {"enabled": True},
        }
    )
    result = build(cfg, tmp_path_factory.mktemp("curved"), parts=("left", "right"))
    meshes = {k: mm.loadMesh(p) for k, p in result.outputs.items()}
    return cfg, result.layout, meshes


def test_curved_halves_are_closed_and_follow_the_curve(curved_case):
    cfg, L, meshes = curved_case
    profile = profile_for(cfg, L)
    for side in ("left", "right"):
        assert is_closed(meshes[side]), side
        assert len(mm.getAllComponents(meshes[side])) == 1, side

    # The divider band sits on both sides of the curve, between lining and shell
    z = L.scroll_z + L.scroll_height / 2
    for x in (-43.0, 43.0):
        fy = float(profile.f(x))
        assert inside(meshes["left"], (x, fy - L.wall / 2, z))
        assert inside(meshes["right"], (x, fy + L.wall / 2, z))
        assert not inside(meshes["left"], (x, fy + L.wall / 2, z))
    # The right half reaches below y = 0 where the curve dips
    assert _bounds(meshes["right"])[0][1] < -5


def test_nubs_follow_the_curve(curved_case):
    cfg, L, meshes = curved_case
    profile = profile_for(cfg, L)
    for x, z in cfg.nubs.positions:
        xn, fy = -x, float(profile.f(-x))
        assert inside(meshes["left"], (xn, fy + 1.0, z))
        assert not inside(meshes["right"], (xn, fy + 1.0, z))
        assert inside(meshes["right"], (xn, fy + 3.2, z))


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"nubs": {"positions": [[-30, 20]]}}, "into the scroll cavity"),
        ({"nubs": {"positions": [[-60, 20]]}}, "past the outside"),
        ({"style": "villa.2026-10", "nubs": {"positions": [[-44, 20]]}}, "divider .* is only"),
    ],
)
def test_nubs_off_the_divider_are_rejected(tmp_path, data, message):
    with pytest.raises(ConfigError, match=rf"nubs.positions\[0\].*{message}"):
        build(config_from_dict(data), tmp_path, parts=("left",))


@pytest.fixture(scope="module")
def villa_case(tmp_path_factory):
    cfg = config_from_dict({"style": "villa.2026-10", "name": "v", "label": {"line1": "PHERC"}})
    result = build(cfg, tmp_path_factory.mktemp("villa"))
    assert set(result.outputs) == {"scroll", "left", "right"}
    meshes = {k: mm.loadMesh(p) for k, p in result.outputs.items()}
    return cfg, result.layout, meshes


def test_villa_case_features(villa_case):
    cfg, L, meshes = villa_case
    left, right = meshes["left"], meshes["right"]
    for mesh in (left, right):
        assert is_closed(mesh)
        assert len(mm.getAllComponents(mesh)) == 1

    half, h = L.cap_half_width, cfg.ends.cap_height
    (x0, _, z0), (x1, _, z1) = _bounds(left)
    # Bolt tabs stick out one cap height past the square; disc below the cap
    assert (x0, x1) == pytest.approx((-half - h, half + h), abs=0.05)
    assert (z0, z1) == pytest.approx((-10, L.outer_height), abs=1e-3)

    tab = half + h / 2
    for mesh in (left, right):
        assert not inside(mesh, (tab, 0.0, h / 2)) and not inside(mesh, (-tab, 0.0, h / 2))
    # Tab material clear of the bolt hole, counterbore, and nut pocket
    assert inside(left, (tab, -3.0, 0.5))
    # Kinematic slot at 90 degrees, cut into the disc bottom
    assert not inside(left, (0, 37.5, -9.9))
    # The right half's side of the disc top is lowered 0.5mm
    assert inside(left, (0, -30, -0.25)) and not inside(left, (0, 30, -0.25))
    # No shell: the space beside the lining is open
    z = L.scroll_z + L.scroll_height / 2
    assert not inside(left, (0, -(L.lining_diameter / 2 + 2), z))


def test_components_compose(tmp_path):
    """villa's caps and disc around the honeycomb shell, on a curved split."""
    cfg = config_from_dict(
        {
            "name": "mix",
            "split": {"type": "curve"},
            "ends": {"type": "caps"},
            "mount": {"type": "kinematic"},
            "stand": {"enabled": False},
            "escape_holes": {"enabled": True},
        }
    )
    result = build(cfg, tmp_path)
    for side in ("left", "right"):
        mesh = mm.loadMesh(result.outputs[side])
        assert is_closed(mesh), side
        assert len(mm.getAllComponents(mesh)) == 1, side


def test_solid_shell_without_mount(tmp_path):
    """Marker rings on a solid shell, and the left label engraved on its own floor."""
    data = {
        "name": "s",
        "shell": {"type": "solid"},
        "mount": {"type": "none"},
        "stand": {"enabled": False},
    }
    volumes = []
    for line1 in ("", "TEST"):
        cfg = config_from_dict({**data, "label": {"line1": line1}})
        result = build(cfg, tmp_path / (line1 or "blank"), parts=("left",))
        left = mm.loadMesh(result.outputs["left"])
        # A solid shell seals the gap around the lining, so it's a second surface
        assert is_closed(left)
        volumes.append(left.volume())
    L = result.layout
    z = L.scroll_z + L.scroll_height / 2
    assert inside(left, (0, -(L.outer_diameter / 2 + 0.25), z))
    assert volumes[1] < volumes[0] - 1


def test_caps_around_a_wider_shell(tmp_path):
    cfg = config_from_dict(
        {
            "name": "c",
            "scroll": {"generic_diameter": 110.0},
            "ends": {"type": "caps"},
            "mount": {"type": "none"},
            "stand": {"enabled": False},
        }
    )
    result = build(cfg, tmp_path)
    for side in ("left", "right"):
        mesh = mm.loadMesh(result.outputs[side])
        assert is_closed(mesh), side
        assert len(mm.getAllComponents(mesh)) == 1, side
