"""Split surface between the case halves, as a profile y = f(x) extruded in Z.

Pure Python so both the mesh and B-rep stages can share it. Requiring y = f(x)
keeps undercut removal valid: from anywhere in a half, moving straight along
Y reaches the split.

The curve is ScrollPrize/villa's S-shaped divider: two three-point arcs
through (-X, 0), (-R/2, A), (0, 0), (R/2, -A), (X, 0), where X is the span and
R = X + wall. With no shell X is the cavity radius and this is exactly
upstream's curve. Beyond the span the split continues along y = 0.
"""

import math
from dataclasses import dataclass

import numpy as np

from .config import ConfigError

# Arcs sampled for meshes use this many points; the chord error is negligible
_ARC_SAMPLES = 256


@dataclass(frozen=True)
class Arc:
    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]

    def circle(self) -> tuple[float, float, float]:
        (ax, ay), (bx, by), (cx, cy) = self.start, self.mid, self.end
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        ux = (
            (ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)
        ) / d
        uy = (
            (ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)
        ) / d
        return ux, uy, math.hypot(ax - ux, ay - uy)

    def y(self, x: np.ndarray) -> np.ndarray:
        cx, cy, r = self.circle()
        # The branch of the circle the arc's midpoint lies on
        sign = 1.0 if self.mid[1] >= cy else -1.0
        return cy + sign * np.sqrt(np.maximum(r**2 - (x - cx) ** 2, 0))


@dataclass(frozen=True)
class Profile:
    """Split profile across [-span, span]; y = 0 outside it."""

    span: float
    arcs: tuple[Arc, ...] = ()

    def f(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        y = np.zeros_like(x)
        for arc in self.arcs:
            lo, hi = sorted((arc.start[0], arc.end[0]))
            inside = (x >= lo) & (x <= hi)
            y[inside] = arc.y(x[inside])
        return y

    def slope(self, x: float, h: float = 1e-3) -> float:
        return float((self.f(x + h) - self.f(x - h)) / (2 * h))

    def sample_x(self, extent: float) -> np.ndarray:
        """X samples over [-extent, extent], dense along the arcs."""
        xs = [np.array([-extent, extent])]
        for arc in self.arcs:
            xs.append(np.linspace(arc.start[0], arc.end[0], _ARC_SAMPLES))
        return np.unique(np.concatenate(xs))


def make_profile(split_type: str, span: float, wall: float, amplitude=None, flip=False) -> Profile:
    if split_type == "plane":
        return Profile(span)
    if split_type != "curve":
        raise ConfigError(f"Unknown split type {split_type!r}")

    r = span + wall
    a = 0.2 * r if amplitude is None else amplitude
    if flip:
        a = -a
    mid_x = r / 2
    # Each arc must stay a graph over x, i.e. less than a semicircle. That
    # holds when its midpoint is inside the circle on its chord (-span, 0).
    limit = math.sqrt(max((span / 2) ** 2 - (mid_x - span / 2) ** 2, 0))
    if abs(a) >= limit:
        raise ConfigError(
            f"split.amplitude = {abs(a):.2f} is too large: for this case's split span of "
            f"{span:.2f} mm it must be under {limit:.2f}"
        )
    arcs = (
        Arc((-span, 0.0), (-mid_x, a), (0.0, 0.0)),
        Arc((0.0, 0.0), (mid_x, -a), (span, 0.0)),
    )
    return Profile(span, arcs)


def profile_for(cfg, layout) -> Profile:
    """The split profile for a resolved config and layout."""
    s = cfg.split
    return make_profile(s.type, layout.split_span, layout.wall, s.amplitude, s.flip)
