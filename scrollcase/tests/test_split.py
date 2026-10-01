import numpy as np
import pytest

from scrollcase.split import make_profile


def test_plane_is_flat():
    p = make_profile("plane", 46, 2)
    assert np.all(p.f(np.linspace(-100, 100, 9)) == 0)


def test_curve_matches_upstream_control_points():
    span, wall = 46.0, 2.0
    r = span + wall
    p = make_profile("curve", span, wall)
    assert p.f([-span, 0, span]) == pytest.approx([0, 0, 0], abs=1e-9)
    assert p.f([-r / 2, r / 2]) == pytest.approx([0.2 * r, -0.2 * r])
    # Flat outside the span
    assert np.all(p.f([-span - 5, span + 5]) == 0)


def test_curve_is_a_continuous_graph():
    p = make_profile("curve", 46, 2)
    xs = p.sample_x(46)
    ys = p.f(xs)
    assert np.all(np.diff(xs) > 0)
    assert np.max(np.abs(np.diff(ys))) < 1.0
    assert np.max(np.abs(ys)) == pytest.approx(0.2 * 48, rel=0.02)


def test_flip_and_amplitude():
    p = make_profile("curve", 46, 2, amplitude=5, flip=True)
    assert p.f([-24]) == pytest.approx([-5])
    with pytest.raises(ValueError, match="too large"):
        make_profile("curve", 46, 2, amplitude=30)
