"""Minimum enclosing cylinder fit.

Adapted from ScrollPrize/villa foundation/scrollcase (MIT, see LICENSE.villa).
"""

import logging

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull

from .smallest_circle import smallest_enclosing_circle

logger = logging.getLogger(__name__)


def _plane_basis(normal: np.ndarray) -> np.ndarray:
    reference = np.array([0.0, 1.0, 0.0])
    if abs(normal @ reference) > 0.99:
        reference = np.array([1.0, 0.0, 0.0])
    u = np.cross(normal, reference)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    return np.vstack([u, v])


def fit_cylinder(
    points: np.ndarray, tol: float = 1e-6
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Fit the smallest enclosing cylinder to a point cloud.

    The axis is found by minimizing the radius of the smallest circle enclosing
    the points projected onto the axis-normal plane, starting from the first
    principal component. A loose `tol` stops ~1 degree off-axis, which
    oversizes the radius by about a millimeter on a typical scroll.

    Returns:
        A rotation matrix and translation that map points into cylinder
        coordinates (axis along +Z, centered on it, bottom at Z=0), plus the
        cylinder radius and height.
    """
    hull_points = points[ConvexHull(points).vertices]

    centered = hull_points - hull_points.mean(axis=0)
    eigenvalues, eigenvectors = np.linalg.eigh(np.cov(centered, rowvar=False))
    initial_axis = eigenvectors[:, np.argmax(eigenvalues)]

    def projected_radius(n: np.ndarray) -> float:
        n = n / np.linalg.norm(n)
        local = hull_points @ _plane_basis(n).T
        return smallest_enclosing_circle(local)[1]

    result = minimize(
        projected_radius,
        initial_axis,
        constraints=[{"type": "eq", "fun": lambda n: n @ n - 1}],
        method="SLSQP",
        tol=tol,
    )
    axis = result.x / np.linalg.norm(result.x)

    basis = _plane_basis(axis)
    center_2d, radius = smallest_enclosing_circle(hull_points @ basis.T)
    d = hull_points @ axis
    logger.info("Cylinder fit: axis %s, radius %.2f", axis, radius)

    rotation = np.vstack([basis, axis])
    translation = rotation @ -(basis.T @ center_2d)
    translation[2] -= d.min()
    return rotation, translation, float(radius), float(d.max() - d.min())
