"""B-rep stage: case body halves and stand, ported from `Scroll Case Generator.scad`.

The scroll cavity and lining are added later in the mesh stage, so the bodies
built here are the shell, divider wall, and mount/alignment features only.
"""

import math

from build123d import (
    Align,
    Kind,
    Line,
    Part,
    Plane,
    Polygon,
    Side,
    Text,
    ThreePointArc,
    Torus,
    Wire,
    extrude,
    make_face,
    mirror,
    offset,
)

from .caps import bottom_cap, top_cap
from .config import NUB_ROTATIONS, CaseConfig, Layout, nub_extent
from .mount_disc import MOUNT_DISCS, KinematicDisc
from .scad import cube, cylinder, rotate, scaled, sphere, translate
from .split import Profile, profile_for

_BIG = 5000.0
# Added depth so engraved features don't leave coincident faces
_LABEL_EXTRA = 0.1
# Escape holes this close to tangent with a shell surface get nudged inward
_TANGENT_TOL = 0.05
_MARKER_BAND_HEIGHT = 3


def _profile_edges(profile: Profile, extent: float) -> list:
    """Edges along the split profile from x = -extent to +extent."""
    if not profile.arcs:
        return [Line((-extent, 0), (extent, 0))]
    edges = [ThreePointArc(a.start, a.mid, a.end) for a in profile.arcs]
    if extent > profile.span:
        edges = [
            Line((-extent, 0), (-profile.span, 0)),
            *edges,
            Line((profile.span, 0), (extent, 0)),
        ]
    return edges


def _half_space(profile: Profile, side: str) -> Part:
    if not profile.arcs:
        y = -_BIG if side == "left" else 0
        return translate([-_BIG / 2, y, -_BIG / 2], cube([_BIG, _BIG, _BIG]))
    y = -_BIG if side == "left" else _BIG
    edges = _profile_edges(profile, _BIG) + [
        Line((_BIG, 0), (_BIG, y)),
        Line((_BIG, y), (-_BIG, y)),
        Line((-_BIG, y), (-_BIG, 0)),
    ]
    return translate([0, 0, -_BIG / 2], extrude(make_face(edges), amount=_BIG))


def _band(profile: Profile, half_width: float, extent: float, h: float) -> Part:
    """Wall of constant thickness along the profile, with round ends."""
    outline = offset(
        Wire(_profile_edges(profile, extent)), amount=half_width, side=Side.BOTH, kind=Kind.ARC
    )
    return extrude(make_face(outline), amount=h)


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
    mid_h = L.outer_height - L.lid_thickness - L.bottom_wall
    keep = translate([0, 0, L.bottom_wall], cylinder(mid_h, d))
    if cfg.shell.marker_rings:
        for z in marker_ring_heights(L):
            keep -= translate([0, 0, z], cylinder(_MARKER_BAND_HEIGHT, d, center=True))
    profile = profile_for(cfg, L)
    if profile.arcs:
        keep -= translate(
            [0, 0, -L.outer_height / 2], _band(profile, L.wall, d, 2 * L.outer_height)
        )
    else:
        keep -= translate(
            [0, 0, L.outer_height / 2], cube([2 * d, 2 * L.wall, 2 * L.outer_height], center=True)
        )
    holes = _honeycomb_holes(cfg, L)
    return holes[0].fuse(*holes[1:]) & keep


def shell(cfg: CaseConfig, L: Layout) -> Part | None:
    """Outer cylinder, optionally honeycombed.

    With shell ends it includes the floor and lid. With caps it's an open
    tube whose ends are buried halfway into the caps, so no faces coincide.
    """
    if cfg.shell.type == "none":
        return None
    if cfg.ends.type == "shell":
        outer = cylinder(L.outer_height, L.outer_diameter / 2)
        hollow = translate([0, 0, L.inner_z], cylinder(L.inner_height, L.inner_diameter / 2))
        body = outer - hollow
    else:
        z0, z1 = L.bottom_wall / 2, L.outer_height - L.lid_thickness / 2
        tube = cylinder(z1 - z0, L.outer_diameter / 2) - cylinder(z1 - z0, L.inner_diameter / 2)
        body = translate([0, 0, z0], tube)

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


def divider(cfg: CaseConfig, L: Layout) -> Part:
    """Wall along the split, holding the lining.

    With a shell it ends mid-shell so no faces coincide. Without one it ends
    at the cavity edge in round posts, as upstream. With caps it's buried
    halfway into each cap.
    """
    profile = profile_for(cfg, L)
    if cfg.ends.type == "shell":
        z0, z1 = 0.0, L.outer_height
    else:
        z0, z1 = L.bottom_wall / 2, L.outer_height - L.lid_thickness / 2
    h = z1 - z0
    if cfg.shell.type == "none":
        return translate([0, 0, z0], _band(profile, L.wall, profile.span, h))
    mid = (L.inner_diameter + L.outer_diameter) / 4
    if profile.arcs:
        wall = _band(profile, L.wall, profile.span, h) & cylinder(h, mid)
    else:
        w, t = L.outer_diameter, 2 * L.wall
        wall = translate([-w / 2, -t / 2, 0], cube([w, t, h])) & cylinder(h, mid)
    return translate([0, 0, z0], wall) if z0 else wall


def _case_body(cfg: CaseConfig, L: Layout) -> Part:
    """Everything that gets split: shell, divider, and caps."""
    body = divider(cfg, L)
    if (sh := shell(cfg, L)) is not None:
        body = sh + body
    if cfg.ends.type == "caps":
        body += bottom_cap(cfg, L)
        body += translate([0, 0, L.outer_height - L.lid_thickness], top_cap(cfg, L))
    return body


def _mount_thickness(cfg: CaseConfig) -> float:
    return MOUNT_DISCS[cfg.mount.type].thickness if cfg.mount.type != "none" else 0.0


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


def _escape_holes(cfg: CaseConfig, L: Layout, side: str) -> list[Part]:
    ex, ey = _escape_xy(cfg, L)
    r = cfg.escape_holes.diameter / 2
    # Overshoot both faces so no cut ends flush with an existing face. Inside,
    # the holes can straddle the shell wall, so keep that overshoot small.
    over, inner_over = 1.0, 0.2
    if side == "left":
        ey = -ey
        bottom_z = -_mount_thickness(cfg) - over
    else:
        bottom_z = -over
    bottom = translate([0, 0, bottom_z], cylinder(L.inner_z + inner_over - bottom_z, r))
    top_z = L.outer_height - L.lid_thickness - inner_over
    top = translate([0, 0, top_z], cylinder(L.outer_height + over - top_z, r))
    return [translate([sx * ex, ey, 0], h) for sx in (-1, 1) for h in (bottom, top)]


def _nub_box(size: float, depth: float, sink: float = 0.0) -> Part:
    """Box standing `depth` proud of the split, extending `sink` below it."""
    return translate([0, (depth - sink) / 2, 0], cube([size, depth + sink, size], center=True))


def _nub_anchors(cfg: CaseConfig, L: Layout):
    """Each nub's position on the split surface and how far to sink its base.

    On a sloped split the base sinks far enough to stay attached across its
    width, but no deeper than the divider is thick.
    """
    profile = profile_for(cfg, L)
    for i, (x, z) in enumerate(cfg.nubs.positions):
        xn = -x
        sink = min(abs(profile.slope(xn)) * nub_extent(cfg, i), L.wall)
        yield i, (xn, float(profile.f(xn)), z), sink


def _mount(cfg: CaseConfig, L: Layout, profile: Profile) -> Part | None:
    if cfg.mount.type == "none":
        return None
    disc = MOUNT_DISCS[cfg.mount.type]
    solid = disc.solid()
    if isinstance(disc, KinematicDisc):
        top = translate([-_BIG / 2, -_BIG / 2, -disc.right_clearance], cube([_BIG, _BIG, _BIG]))
        solid -= _half_space(profile, "right") & top
    else:
        # Orientation notch on the rim
        solid -= translate([-1, -disc.diameter / 2 - 1, -disc.thickness - 1], cube([2, 2, 2]))
    return solid


def left_body(cfg: CaseConfig, L: Layout) -> Part:
    profile = profile_for(cfg, L)
    body = _case_body(cfg, L) & _half_space(profile, "left")
    if (mount := _mount(cfg, L, profile)) is not None:
        body += mount

    n = cfg.nubs
    for i, pos, sink in _nub_anchors(cfg, L):
        nub = rotate([0, NUB_ROTATIONS[i % 2], 0], _nub_box(n.size, n.depth, sink))
        body += translate(pos, nub)

    if cfg.escape_holes.enabled:
        body = body.cut(*_escape_holes(cfg, L, "left"))
    # Caps carry the label on the top cap instead
    if cfg.ends.type == "shell" and (tool := label(cfg)) is not None:
        y = (
            MOUNT_DISCS[cfg.mount.type].diameter / 4
            if cfg.mount.type != "none"
            # Without a disc the left half only spans -Y
            else -L.outer_diameter / 4
        )
        body -= translate([0, y, -_mount_thickness(cfg) - _LABEL_EXTRA], tool)
    return body


def right_body(cfg: CaseConfig, L: Layout) -> Part:
    profile = profile_for(cfg, L)
    body = _case_body(cfg, L) & _half_space(profile, "right")

    n = cfg.nubs
    socket = n.size + 2 * n.margin
    socket_depth = n.depth + 2 * n.margin
    anchors = list(_nub_anchors(cfg, L))
    for _, pos, sink in anchors:
        housing = translate(pos, _nub_box(socket + L.wall, n.depth + L.wall, sink))
        if sink > 0:
            # Keep the housing from crossing the split into the left half
            housing &= _half_space(profile, "right")
        body += housing
    for i, pos, sink in anchors:
        hollow = scaled([1.01] * 3, _nub_box(socket, socket_depth, sink))
        body -= translate(pos, rotate([0, NUB_ROTATIONS[i % 2], 0], hollow))

    if cfg.escape_holes.enabled:
        body = body.cut(*_escape_holes(cfg, L, "right"))
    if cfg.ends.type == "shell" and (tool := label(cfg)) is not None:
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
