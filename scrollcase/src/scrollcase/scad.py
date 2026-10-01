"""OpenSCAD-style primitives on top of build123d.

These keep the ported geometry readable side by side with the original
OpenSCAD: same anchoring defaults and the same X-then-Y-then-Z rotation order.
"""

from build123d import Align, Box, Cylinder, Extrinsic, Part, Pos, Rotation, Sphere, scale

_MIN = (Align.MIN, Align.MIN, Align.MIN)
_CENTER = (Align.CENTER, Align.CENTER, Align.CENTER)
_CENTER_XY = (Align.CENTER, Align.CENTER, Align.MIN)


def cube(size, center: bool = False) -> Part:
    return Box(*size, align=_CENTER if center else _MIN)


def cylinder(h: float, r: float, center: bool = False) -> Part:
    """True cylinder; matches `cylinder_outer` since flats land on `r`."""
    return Cylinder(r, h, align=_CENTER if center else _CENTER_XY)


def sphere(d: float) -> Part:
    return Sphere(d / 2)


def translate(v, shape: Part) -> Part:
    return Pos(*v) * shape


def rotate(angles, shape: Part) -> Part:
    # OpenSCAD rotates about global X, then Y, then Z
    return Rotation(*angles, ordering=Extrinsic.XYZ) * shape


def scaled(v, shape: Part) -> Part:
    return scale(shape, by=tuple(v))
