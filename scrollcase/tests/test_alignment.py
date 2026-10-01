import itertools

import numpy as np
from scipy.spatial.transform import Rotation

from scrollcase.alignment import fit_cylinder
from scrollcase.smallest_circle import smallest_enclosing_circle


def test_smallest_circle_matches_brute_force():
    rng = np.random.default_rng(1)
    pts = rng.normal(size=(40, 2))
    _, radius = smallest_enclosing_circle(pts)

    # The optimum is defined by 2 or 3 points; brute force all of them
    best = np.inf
    for a, b in itertools.combinations(pts, 2):
        c, r = (a + b) / 2, np.linalg.norm(a - b) / 2
        if np.all(np.linalg.norm(pts - c, axis=1) <= r + 1e-9):
            best = min(best, r)
    for a, b, c in itertools.combinations(pts, 3):
        m = np.array([b - a, c - a])
        if abs(np.linalg.det(m)) < 1e-12:
            continue
        center = np.linalg.solve(2 * m, [b @ b - a @ a, c @ c - a @ a])
        r = np.linalg.norm(a - center)
        if np.all(np.linalg.norm(pts - center, axis=1) <= r + 1e-9):
            best = min(best, r)
    assert np.isclose(radius, best)


def test_smallest_circle_handles_many_points():
    rng = np.random.default_rng(2)
    angles = rng.uniform(0, 2 * np.pi, 20000)
    pts = np.c_[np.cos(angles), np.sin(angles)] * 5 + [3, -2]
    center, radius = smallest_enclosing_circle(pts)
    assert np.allclose(center, [3, -2], atol=1e-3)
    assert np.isclose(radius, 5, atol=1e-3)


def test_fit_cylinder_recovers_tilted_cylinder():
    rng = np.random.default_rng(3)
    theta = rng.uniform(0, 2 * np.pi, 4000)
    z = rng.uniform(0, 120, 4000)
    pts = np.c_[30 * np.cos(theta), 30 * np.sin(theta), z]
    rot = Rotation.from_euler("xyz", [30, -20, 10], degrees=True).as_matrix()
    pts = pts @ rot.T + [5, -8, 12]

    rotation, translation, radius, height = fit_cylinder(pts)
    aligned = pts @ rotation.T + translation

    assert np.isclose(radius, 30, rtol=0.01)
    assert np.isclose(height, 120, rtol=0.01)
    assert np.isclose(aligned[:, 2].min(), 0, atol=1e-6)
    assert np.linalg.norm(aligned[:, :2], axis=1).max() <= radius + 1e-6
