use <cylinder_outer.scad>

// Mirrored in scrollcase/src/scrollcase/mount_disc.py; keep in sync

// Globals (in mm)
function GenericMountDisc_Diameter() = 112.5;
function GenericMountDisc_Thickness() = 12.5;
function GenericMountDisc_NotchZ() = 6.025;
function GenericMountDisc_NotchDiameter() = 6.8;
function GenericMountDisc_NotchDepth() = 5.75;

module GenericMountDisc(pos = [0,0,0]) {
// Parameters (in mm)
errorMargin=0.07;
baseDiam = GenericMountDisc_Diameter();
baseRadius = baseDiam / 2;
baseThickness = GenericMountDisc_Thickness();
holeCenter = GenericMountDisc_NotchZ();
holeDiam = GenericMountDisc_NotchDiameter();
holeRadius = holeDiam / 2;
holeDepth = GenericMountDisc_NotchDepth();
boxHeight = 7;
boxWidth = 13.5;

// Offset to position
translate(pos) {

    // Base
    difference() {
    cylinder_outer(h=baseThickness, r=baseRadius, fn=128);

    // Bolt holes
    translate([0, 0, holeCenter]) {
        offset = baseRadius - holeDepth/2 + errorMargin;
        translate([0, offset, 0]) rotate([90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
        translate([0, -offset, 0]) rotate([-90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
    }

    // Box
    offset = boxWidth / 2;
    translate([-offset, -offset, -errorMargin]) cube([boxWidth, boxWidth, boxHeight + errorMargin]);
    }
    }
}

GenericMountDisc();
