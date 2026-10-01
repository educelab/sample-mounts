"""B-rep stage: case body halves and stand, ported from `Scroll Case Generator.scad`.

The scroll cavity and lining are added later in the mesh stage, so the bodies
built here are the shell, divider wall, and mount/alignment features only.
"""

import math

from build123d import (
    Align,
    Part,
    Plane,
    Polygon,
    Text,
    Torus,
    extrude,
    mirror,
)

from .config import CaseConfig, Layout
from .mount_disc import MOUNT_DISCS, MountDisc
from .scad import cube, cylinder, rotate, scaled, sphere, translate

_BIG = 5000.0
# Added depth so engraved features don't leave coincident faces
_LABEL_EXTRA = 0.1
# Escape holes this close to tangent with a shell surface get nudged inward
_TANGENT_TOL = 0.05
_MARKER_BAND_HEIGHT = 3
# Nubs alternate between square and diamond orientations
_NUB_ROTATIONS = (0, 45)


def _half_space(side: str) -> Part:
    y = -_BIG if side == "left" else 0
    return translate([-_BIG / 2, y, -_BIG / 2], cube([_BIG, _BIG, _BIG]))


def _prism(h: float, d: float, edges: int) -> Part:
    """OpenSCAD `cylinder(h, d=d, $fn=edges, center=true)`."""
    r = d / 2
    pts = [
        (r * math.cos(2 * math.pi * i / edges), r * math.sin(2 * math.pi * i / edges))
        for i in range(edges)
    ]
    return translate([0, 0, -h / 2], extrude(Polygon(*pts, align=None), amount=h))


def _honeycomb_holes(cfg: CaseConfig, L: Layout) -> list[Part]:
    hc = cfg.shell.honeycomb
    d = L.outer_diameter
    gap_rot = math.degrees(hc.spacing / d)
    hex_rot = (360 - gap_rot * hc.columns) / hc.columns
    total_rot = hex_rot + gap_rot
    hex_d = d * math.sin(math.radians(hex_rot / 2))
    # Slightly past the outer radius so hole ends aren't tangent to the shell
    hex_len = d * 0.52
    z_step = math.sin(math.radians(60)) * (hex_d + hc.spacing)

    hole = rotate([90, 90, 0], _prism(hex_len, hex_d, hc.hole_edges))
    hole = translate([0, hex_len / 2, 0], hole)
    holes = []
    for row in range(int(L.outer_height / z_step + 1) + 1):
        for col in range(hc.columns):
            angle = col * total_rot + total_rot / 2 * (row % 2)
            holes.append(translate([0, 0, row * z_step], rotate([0, 0, angle], hole)))
    return holes


def marker_ring_heights(L: Layout) -> list[float]:
    """Cavity bottom, scroll bottom, scroll middle, scroll top, cavity top."""
    z0 = L.cavity_z
    return [
        z0,
        L.scroll_z,
        L.scroll_z + L.scroll_height / 2,
        L.scroll_z + L.scroll_height,
        z0 + L.cavity_height,
    ]


def _honeycomb_cutter(cfg: CaseConfig, L: Layout) -> Part:
    """Honeycomb holes, limited to where the shell wall should be open.

    The floor, lid, marker ring bands, and divider are left solid by clipping
    the holes rather than adding those parts back, since unions over the
    shell's cylindrical faces give OpenCASCADE trouble.
    """
    d = L.outer_diameter
    mid_h = L.outer_height - L.wall - L.bottom_wall
    keep = translate([0, 0, L.bottom_wall], cylinder(mid_h, d))
    if cfg.shell.marker_rings:
        for z in marker_ring_heights(L):
            keep -= translate([0, 0, z], cylinder(_MARKER_BAND_HEIGHT, d, center=True))
    keep -= translate(
        [0, 0, L.outer_height / 2], cube([2 * d, 2 * L.wall, 2 * L.outer_height], center=True)
    )
    holes = _honeycomb_holes(cfg, L)
    return holes[0].fuse(*holes[1:]) & keep


def shell(cfg: CaseConfig, L: Layout) -> Part:
    """Outer cylinder with floor and lid, optionally honeycombed."""
    outer = cylinder(L.outer_height, L.outer_diameter / 2)
    hollow = translate([0, 0, L.inner_z], cylinder(L.inner_height, L.inner_diameter / 2))
    body = outer - hollow

    if cfg.shell.type == "honeycomb":
        body -= _honeycomb_cutter(cfg, L)
        if cfg.shell.marker_rings:
            for z in marker_ring_heights(L):
                body += translate([0, 0, z], Torus(L.outer_diameter / 2, 0.5))

    if cfg.shell.open_top:
        # Scoop away the upper shell, leaving an open cradle around the lining
        tilt = 5
        size = [L.outer_diameter * 2, L.outer_diameter * 1.5, L.outer_height * 2]
        for sign in (-1, 1):
            scoop = rotate([sign * tilt, 0, 0], scaled(size, sphere(1)))
            body -= translate([0, sign * (L.outer_diameter / 4 + 5), L.outer_height + 2], scoop)
    return body


def divider(L: Layout) -> Part:
    """Wall across the split plane. It ends mid-shell so no faces coincide."""
    w, t, h = L.outer_diameter, 2 * L.wall, L.outer_height
    slab = translate([-w / 2, -t / 2, 0], cube([w, t, h]))
    return slab & cylinder(h, (L.inner_diameter + L.outer_diameter) / 4)


def label(cfg: CaseConfig) -> Part | None:
    """Engraving tool for the label, mirrored to read correctly from below."""
    lb = cfg.label
    sketches = []
    for i, line in enumerate((lb.line1, lb.line2)):
        if line:
            text = Text(line, lb.height, font=lb.font, align=(Align.CENTER, Align.MIN))
            sketches.append(translate([0, -1.5 * lb.height * i, 0], text))
    if not sketches:
        return None
    flat = mirror(sum(sketches[1:], sketches[0]), Plane.YZ)
    return extrude(flat, amount=lb.depth + _LABEL_EXTRA)


def _escape_xy(cfg: CaseConfig, L: Layout) -> tuple[float, float]:
    eh = cfg.escape_holes
    lining_mid = (L.cavity_diameter + L.wall) / 2
    shell_mid = (L.outer_diameter - L.wall) / 2
    dist = (lining_mid + shell_mid) / 2 + eh.offset
    r = eh.diameter / 2
    for surface in (L.inner_diameter / 2, L.outer_diameter / 2):
        for edge in (dist - r, dist + r):
            if abs(edge - surface) < _TANGENT_TOL:
                dist -= 2 * _TANGENT_TOL
    return math.cos(math.radians(eh.angle)) * dist, math.sin(math.radians(eh.angle)) * dist


def _escape_holes(cfg: CaseConfig, L: Layout, disc: MountDisc, side: str) -> list[Part]:
    ex, ey = _escape_xy(cfg, L)
    r = cfg.escape_holes.diameter / 2
    # Overshoot both faces so no cut ends flush with an existing face. Inside,
    # the holes can straddle the shell wall, so keep that overshoot small.
    over, inner_over = 1.0, 0.2
    if side == "left":
        ey = -ey
        bottom_z = -disc.thickness - over
    else:
        bottom_z = -over
    bottom = translate([0, 0, bottom_z], cylinder(L.inner_z + inner_over - bottom_z, r))
    top_z = L.outer_height - L.wall - inner_over
    top = translate([0, 0, top_z], cylinder(L.outer_height + over - top_z, r))
    return [translate([sx * ex, ey, 0], h) for sx in (-1, 1) for h in (bottom, top)]


def _nub_box(size: float, depth: float) -> Part:
    return translate([0, depth / 2, 0], cube([size, depth, size], center=True))


def left_body(cfg: CaseConfig, L: Layout) -> Part:
    disc = MOUNT_DISCS[cfg.mount.type]
    body = (shell(cfg, L) + divider(L)) & _half_space("left")
    body += disc.solid()

    n = cfg.nubs
    for i, (x, z) in enumerate(n.positions):
        nub = rotate([0, _NUB_ROTATIONS[i % 2], 0], _nub_box(n.size, n.depth))
        body += translate([-x, 0, z], nub)

    if cfg.escape_holes.enabled:
        body = body.cut(*_escape_holes(cfg, L, disc, "left"))
    if (tool := label(cfg)) is not None:
        body -= translate([0, disc.diameter / 4, -disc.thickness - _LABEL_EXTRA], tool)
    # Orientation notch on the disc rim
    body -= translate([-1, -disc.diameter / 2 - 1, -disc.thickness - 1], cube([2, 2, 2]))
    return body


def right_body(cfg: CaseConfig, L: Layout) -> Part:
    disc = MOUNT_DISCS[cfg.mount.type]
    body = (shell(cfg, L) + divider(L)) & _half_space("right")

    n = cfg.nubs
    socket = n.size + 2 * n.margin
    socket_depth = n.depth + 2 * n.margin
    for x, z in n.positions:
        housing = _nub_box(socket + L.wall, n.depth + L.wall)
        body += translate([-x, 0, z], housing)
    for i, (x, z) in enumerate(n.positions):
        hollow = scaled([1.01] * 3, _nub_box(socket, socket_depth))
        body -= translate([-x, 0, z], rotate([0, _NUB_ROTATIONS[i % 2], 0], hollow))

    if cfg.escape_holes.enabled:
        body = body.cut(*_escape_holes(cfg, L, disc, "right"))
    if (tool := label(cfg)) is not None:
        body -= translate([0, L.outer_diameter / 4, -_LABEL_EXTRA], tool)
    return body


def _gusset(width: float, depth: float) -> Part:
    hyp = math.sqrt(2 * depth * depth)
    cutter = rotate(
        [0, 45, 0], translate([0, 0, hyp / 6], cube([hyp + 1, width + 1, depth], center=True))
    )
    block = cube([depth, width, depth], center=True) - cutter
    return translate([0, 0, depth / 2], rotate([0, 0, 90], block))


def _stand_wall(width: float, height: float, thickness: float, support: float) -> Part:
    wall = cube([width, height, thickness], center=True)
    gusset = _gusset(width, support)
    return wall + translate([0, -height / 2 + support / 2, thickness / 2 - 0.01], gusset)


def stand(cfg: CaseConfig, L: Layout) -> Part:
    """Cradle that holds the left half upright on its disc during assembly."""
    disc = MOUNT_DISCS[cfg.mount.type]
    base_len = disc.thickness + L.outer_height * cfg.stand.length_scale
    base_w = max(disc.diameter, L.outer_diameter) + 0.5
    base_t = 5
    strip = 30
    support = 15

    base = cube([base_w, base_t, base_len])
    window_h = base_len - 2 * strip
    if window_h > 0:
        window_w = (base_w - strip) / 2 + 1
        for x in ((base_w - strip) / 2 + strip, -1):
            base -= translate([x, -base_t / 2, strip], cube([window_w, base_t * 2, window_h]))
    if (tool := label(cfg)) is not None:
        base -= translate(
            [base_w / 2, base_t + _LABEL_EXTRA, base_len / 2], rotate([90, -90, 0], tool)
        )
    base = translate([-base_w / 2, -base_w / 2 - base_t - 0.5, -disc.thickness], base)

    top_h = base_w / 2 - L.outer_diameter / 4
    top = rotate([0, 180, 0], _stand_wall(L.outer_diameter + 0.5, top_h, disc.thickness, support))
    top = translate(
        [0, -base_w / 2 + top_h / 2 - 0.5, cfg.stand.length_scale * L.outer_height - 1.25 * base_t],
        top,
    )
    bottom_h = base_w / 2 - disc.diameter / 4 + 0.5
    bottom = translate(
        [0, -base_w / 2 + bottom_h / 2 - 0.5, -disc.thickness / 2],
        _stand_wall(base_w, bottom_h, disc.thickness, support),
    )

    body = base + top + bottom
    body -= cylinder(L.outer_height + 1, L.outer_diameter / 2)
    body -= translate([0, 0, -disc.thickness - 1], cylinder(disc.thickness + 10, disc.diameter / 2))
    body -= translate([-1, -disc.diameter / 2 - 2, -disc.thickness - 1], cube([2, 4, 2]))

    peg_r = disc.notch_diameter / 2 - 0.2
    peg = rotate([-90, 0, 0], cylinder(peg_r, peg_r, center=True))
    body += translate([0, -disc.diameter / 2 + peg_r / 4, disc.notch_z - disc.thickness], peg)
    return body


PARTS = {"left": left_body, "right": right_body, "stand": stand}
