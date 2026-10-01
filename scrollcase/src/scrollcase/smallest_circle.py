"""Smallest enclosing circle (Welzl's algorithm).

Adapted from ScrollPrize/villa foundation/scrollcase (MIT, see LICENSE.villa).
Rewritten iteratively so large point sets don't hit the recursion limit.
"""

import random

import numpy as np


def _contains(center: np.ndarray, radius: float, pt: np.ndarray) -> bool:
    return bool(np.linalg.norm(pt - center) <= radius + 1e-9)


def _circle_two(p1: np.ndarray, p2: np.ndarray) -> tuple[np.ndarray, float]:
    center = (p1 + p2) / 2.0
    return center, float(np.linalg.norm(p1 - center))


def _circle_three(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> tuple[np.ndarray, float]:
    d = 2 * (p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]))
    if abs(d) < 1e-12:
        # Collinear: the circle on the farthest pair covers all three
        pairs = [(p1, p2), (p1, p3), (p2, p3)]
        return max((_circle_two(a, b) for a, b in pairs), key=lambda c: c[1])
    s1, s2, s3 = (p @ p for p in (p1, p2, p3))
    ux = (s1 * (p2[1] - p3[1]) + s2 * (p3[1] - p1[1]) + s3 * (p1[1] - p2[1])) / d
    uy = (s1 * (p3[0] - p2[0]) + s2 * (p1[0] - p3[0]) + s3 * (p2[0] - p1[0])) / d
    center = np.array([ux, uy])
    return center, float(np.linalg.norm(p1 - center))


def smallest_enclosing_circle(points: np.ndarray) -> tuple[np.ndarray, float]:
    """Return the center and radius of the smallest circle enclosing (N, 2) points."""
    pts = [np.asarray(p, dtype=float) for p in points]
    random.Random(0).shuffle(pts)
    if not pts:
        return np.zeros(2), 0.0

    center, radius = pts[0], 0.0
    for i, p in enumerate(pts):
        if _contains(center, radius, p):
            continue
        center, radius = p, 0.0
        for j in range(i):
            q = pts[j]
            if _contains(center, radius, q):
                continue
            center, radius = _circle_two(p, q)
            for k in range(j):
                r = pts[k]
                if not _contains(center, radius, r):
                    center, radius = _circle_three(p, q, r)
    return center, radius
