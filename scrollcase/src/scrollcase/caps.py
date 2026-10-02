"""Square bolted end caps, ported from ScrollPrize/villa's `case.py`.

Kept close to upstream's builder-mode code so the two are easy to compare.
Each cap is built with its bottom face at Z=0.
"""

from build123d import (
    Align,
    Arrow,
    Axis,
    BuildPart,
    BuildSketch,
    Cylinder,
    Line,
    Location,
    Locations,
    Mode,
    Part,
    Rectangle,
    RegularPolygon,
    Text,
    add,
    extrude,
    fillet,
)

from .config import CaseConfig, Layout


def _hex_nut(diameter: float, depth: float) -> Part:
    with BuildPart() as hex_part:
        with BuildSketch():
            RegularPolygon(radius=diameter / 2, side_count=6)
        extrude(amount=depth)
    return hex_part.part


def cap(cfg: CaseConfig, L: Layout) -> Part:
    """Square cap with bolt tabs on both sides of the split."""
    e = cfg.ends
    half, h = L.cap_half_width, e.cap_height
    tab_x = half + h / 2
    # Built first: a BuildPart nested in another modifies the outer one
    nut = _hex_nut(e.nut_diameter, e.nut_depth + 10)
    with BuildPart() as cap_part:
        with BuildSketch():
            r = Rectangle(2 * half, 2 * half)
            fillet(r.vertices(), e.corner_fillet)
            with Locations((-half, 0)):
                r2 = Rectangle(h, h * 2, align=(Align.MAX, Align.CENTER))
            fillet(r2.vertices(), h / 2)
            with Locations((half, 0)):
                r3 = Rectangle(h, h * 2, align=(Align.MIN, Align.CENTER))
            fillet(r3.vertices(), h / 2)
        extrude(amount=h)

        # Bolt holes along Y through each tab
        with Locations((-tab_x, 0, h / 2), (tab_x, 0, h / 2)):
            Cylinder(e.bolt_hole_diameter / 2, 4 * h, rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        # Bolt head counterbores on the +Y face
        with Locations(
            (-tab_x, h - e.bolt_counterbore_depth, h / 2),
            (tab_x, h - e.bolt_counterbore_depth, h / 2),
        ):
            Cylinder(
                e.bolt_counterbore_diameter / 2,
                2 * h,
                mode=Mode.SUBTRACT,
                rotation=(90, 0, 0),
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
        # Nut pockets on the -Y face
        with Locations((-tab_x, -h + e.nut_depth, h / 2), (tab_x, -h + e.nut_depth, h / 2)):
            add(nut, mode=Mode.SUBTRACT, rotation=(90, 0, 0))
    return cap_part.part


def top_cap(cfg: CaseConfig, L: Layout) -> Part:
    """Top cap engraved with upstream's label layout and the lining size."""
    lb = cfg.label
    half = L.cap_half_width
    size = f"{L.lining_diameter:.2f}D x {L.cavity_height:.2f}H"
    lines = [
        ((0, 40), lb.line1),
        ((0, 40 - half), lb.line1),
        ((0, 30 - half), lb.line2),
        ((0, 20 - half), size),
    ]
    with BuildPart() as top_cap_part:
        add(cap(cfg, L))
        top_face = top_cap_part.faces().sort_by(Axis.Z)[-1]
        with BuildSketch(top_face):
            for pos, text in lines:
                if text:
                    with Locations(pos):
                        Text(text, lb.height, font=lb.font)
        extrude(amount=-lb.depth, mode=Mode.SUBTRACT)
    return top_cap_part.part


def bottom_cap(cfg: CaseConfig, L: Layout) -> Part:
    """Bottom cap with counterbored mounting holes and an alignment arrow."""
    e = cfg.ends
    half, h, s = L.cap_half_width, e.cap_height, e.mount_hole_spacing
    # Created outside the builder, which only accepts lines in a BuildLine
    shaft = Line((0, half), (0, half - h))
    with BuildPart() as bottom_cap_part:
        add(cap(cfg, L))
        with Locations((-s, -s, h), (s, -s, h), (-s, s, h), (s, s, h)):
            Cylinder(
                e.mount_hole_diameter / 2,
                h,
                mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            Cylinder(
                e.mount_counterbore_diameter / 2,
                e.mount_counterbore_depth,
                mode=Mode.SUBTRACT,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
        with BuildSketch(Location((0, 0, h))):
            Arrow(h / 2, shaft, h / 8)
        extrude(amount=-cfg.label.depth, mode=Mode.SUBTRACT)
    return bottom_cap_part.part
