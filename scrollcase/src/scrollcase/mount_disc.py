"""Port of `Generic Mount Disc.scad` and `Generic Mount Disc 65mm.scad`.

Keep these dimensions in sync with the OpenSCAD files, which the interface
plates and spindle bases still use.
"""

from dataclasses import dataclass

from build123d import Part

from .scad import cube, cylinder, rotate, translate


@dataclass(frozen=True)
class MountDisc:
    diameter: float
    thickness: float
    notch_z: float
    notch_diameter: float
    notch_depth: float
    # Clearance applied to the notch holes and the bottom pocket
    margin: float
    # Whether `margin` also widens the notch holes (65mm variant only)
    widen_notch: bool
    pocket_height: float
    pocket_width: float = 13.5

    def solid(self) -> Part:
        """The disc with its top face at Z=0."""
        radius = self.diameter / 2
        hole_r = self.notch_diameter / 2 + (self.margin if self.widen_notch else 0)
        offset = radius - self.notch_depth / 2 + self.margin

        disc = cylinder(self.thickness, radius)
        for sign, angle in ((1, 90), (-1, -90)):
            hole = rotate([angle, 0, 0], cylinder(self.notch_depth, hole_r, center=True))
            disc -= translate([0, sign * offset, self.notch_z], hole)

        w = self.pocket_width
        disc -= translate(
            [-w / 2, -w / 2, -self.margin],
            cube([w, w, self.pocket_height + self.margin]),
        )
        return translate([0, 0, -self.thickness], disc)


# Keyed by `mount.type`
MOUNT_DISCS = {
    "generic-112.5": MountDisc(
        diameter=112.5,
        thickness=12.5,
        notch_z=6.025,
        notch_diameter=6.8,
        notch_depth=5.75,
        margin=0.07,
        widen_notch=False,
        pocket_height=7,
    ),
    "generic-65": MountDisc(
        diameter=65,
        thickness=12.5,
        notch_z=6.025,
        notch_diameter=6.8,
        notch_depth=5.75,
        margin=0.4,
        widen_notch=True,
        pocket_height=6,
    ),
}
