import meshlib.mrmeshnumpy as mn
import numpy as np
import pytest
from conftest import inside, is_closed

from scrollcase import lining
from scrollcase.config import CaseConfig, Layout


@pytest.fixture(scope="module")
def built(undercut_scroll):
    cfg = CaseConfig()
    cfg.scroll.mesh = str(undercut_scroll)
    scroll, radius, height = lining.prepare_scroll(cfg)
    layout = Layout.from_config(cfg, radius, height)
    return cfg, layout, scroll, lining.build_lining(scroll, cfg, layout)


def test_scroll_is_aligned_to_case_axis(built):
    _, layout, scroll, _ = built
    verts = mn.getNumpyVerts(scroll)
    assert verts[:, 2].min() == pytest.approx(0, abs=1e-4)
    assert np.linalg.norm(verts[:, :2], axis=1).max() == pytest.approx(layout.scroll_radius)
    # The tilted I-beam is 60mm long with a 40 x 24mm cross-section
    assert layout.scroll_height == pytest.approx(60, abs=0.05)
    assert layout.scroll_radius == pytest.approx(np.hypot(20, 12), abs=0.05)


def test_halves_stay_on_their_side(built):
    _, _, _, halves = built
    for side, sign in (("left", -1), ("right", 1)):
        half = halves[side]
        assert is_closed(half.cavity) and is_closed(half.wall)
        wall_y = mn.getNumpyVerts(half.wall)[:, 1] * sign
        assert wall_y.min() >= -1e-3


def test_scroll_slides_out_toward_split(built):
    """Every point of the scroll can move straight to the split plane unobstructed."""
    _, layout, scroll, halves = built
    placed = lining.place_scroll(scroll, layout)
    r = layout.scroll_radius
    grid = [
        (x, y, z)
        for x in np.linspace(-r, r, 13)
        for y in np.linspace(-r, r, 13)
        for z in layout.scroll_z + np.linspace(2, layout.scroll_height - 2, 4)
    ]
    sample = np.array([p for p in grid if inside(placed, p)])
    assert len(sample) > 50

    for side, toward in (("left", 1), ("right", -1)):
        cavity = halves[side].cavity
        for p in sample[sample[:, 1] * toward < 0]:
            for y in np.arange(p[1], 0, toward * 0.5):
                assert inside(cavity, (p[0], y, p[2])), (side, p, y)


def test_overhang_removal_can_be_disabled(undercut_scroll):
    cfg = CaseConfig(overhang_removal=False)
    cfg.scroll.mesh = str(undercut_scroll)
    scroll, radius, height = lining.prepare_scroll(cfg)
    layout = Layout.from_config(cfg, radius, height)
    halves = lining.build_lining(scroll, cfg, layout)

    # Without removal, paths from under the flanges leave the cavity
    for side, toward in (("left", 1), ("right", -1)):
        cavity = halves[side].cavity
        start = (15, -toward * 9, layout.scroll_z + 30)
        ys = np.arange(start[1], 0, toward * 0.5)
        assert any(not inside(cavity, (start[0], y, start[2])) for y in ys), side
