import meshlib.mrmeshpy as mm
import pytest
from conftest import inside, is_closed

from scrollcase.config import CaseConfig, EscapeHoleConfig, LabelConfig, NubConfig
from scrollcase.pipeline import build


def _bounds(mesh):
    b = mesh.computeBoundingBox()
    return (b.min.x, b.min.y, b.min.z), (b.max.x, b.max.y, b.max.z)


@pytest.fixture(scope="module")
def full_case(tmp_path_factory):
    cfg = CaseConfig(
        name="t",
        nubs=NubConfig(positions=[[-44, 20], [44, 150]]),
        escape_holes=EscapeHoleConfig(enabled=True),
        label=LabelConfig(line1="TEST", line2="V1"),
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
    cfg = CaseConfig(name="g", outer_cylinder=False)
    result = build(cfg, tmp_path, parts=("left",))
    mesh = mm.loadMesh(result.outputs["left"])
    assert is_closed(mesh)
    # The upper shell is scooped away, so the shell wall near the top is gone
    L = result.layout
    assert not inside(mesh, (0, -(L.outer_diameter / 2 - L.wall / 2), L.outer_height - 1))
