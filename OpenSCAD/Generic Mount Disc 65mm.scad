use <cylinder_outer.scad>

// Globals (in mm)
function GenericMountDisc_Diameter() = 65;
function GenericMountDisc_Thickness() = 12.5;
function GenericMountDisc_NotchZ() = 6.025;
function GenericMountDisc_NotchDiameter() = 6.8;
function GenericMountDisc_NotchDepth() = 5.75;

module GenericMountDisc(pos = [0,0,0]) {
// Parameters (in mm)
eps=0.4;
baseDiam = GenericMountDisc_Diameter();
baseRadius = baseDiam / 2;
baseThickness = GenericMountDisc_Thickness();
holeCenter = GenericMountDisc_NotchZ();
holeDiam = GenericMountDisc_NotchDiameter() + 2 * eps;
holeRadius = holeDiam / 2;
holeDepth = GenericMountDisc_NotchDepth();
boxHeight = 6;
boxWidth = 13.5;

// Offset to position
translate(pos) {

    // Base
    difference() {
    cylinder_outer(h=baseThickness, r=baseRadius, fn=128);

    // Bolt holes
    translate([0, 0, holeCenter]) {
        offset = baseRadius - holeDepth/2 + eps;
        translate([0, offset, 0]) rotate([90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
        translate([0, -offset, 0]) rotate([-90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
    }

    // Box
    offset = boxWidth / 2;
    translate([-offset, -offset, -eps]) cube([boxWidth, boxWidth, boxHeight + eps]);
    }
    }
}

GenericMountDisc();
