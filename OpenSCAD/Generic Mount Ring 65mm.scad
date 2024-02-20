use <Generic Mount Disc 65mm.scad>;
use <cylinder_outer.scad>


function GenericMountRing_Diameter() = GenericMountDisc_Diameter() + 20;
function GenericMountRing_Thickness() = 7.5;

module GenericMountRing(pos = [0,0,0]) {
// Parameters (in mm)
eps=0.4;
baseDiam = GenericMountRing_Diameter();
baseRadius = baseDiam / 2;
baseThickness = GenericMountRing_Thickness();
boxHeight = 6 - 2 * eps;
boxWidth = 12.5 - 2 * eps;

wallHeight = 12.5;
wallThickness = 10 - eps;

nutWidth = 13 + 2 * eps;
nutDepth = 6.25 + 2 * eps;
nutHeight = 12.5 + 2 * eps;

holeZ = 6.025;
holeRadius = 6.9 / 2 + 2 * eps;
holeDepth = 12;

// Offset to position
translate(pos) {

    // Base
    translate([0,0,-baseThickness]) cylinder_outer(h=baseThickness, r=baseRadius, fn=128);
    
    // Walls
    difference() {
      cylinder_outer(h=wallHeight, r=baseRadius, fn=128);
      cylinder_outer(h=wallHeight, r=baseRadius-wallThickness, fn=128);
      translate([12.5, -baseRadius,0]) cube([baseRadius, baseDiam, wallHeight+eps]);
      translate([-12.5-baseRadius, -baseRadius,0]) cube([baseRadius, baseDiam, wallHeight+eps]);
      // Bolt holes
      translate([0, 0, holeZ]) {
          offset = baseRadius + 1 - holeDepth/2 + eps;
          translate([0, offset, 0]) rotate([90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
          translate([0, -offset, 0]) rotate([-90,0,0]) cylinder_outer(h=holeDepth, r=holeRadius, center=true);
      }
      // Nut cutouts
      x = -nutWidth / 2;
      translate([x,-baseRadius+2.3-2*eps,0.3]) cube([nutWidth, nutDepth, nutHeight]);
      translate([x,baseRadius-nutDepth+2*eps-2.3,0.3]) cube([nutWidth, nutDepth, nutHeight]);
    }


    // Box
    offset = boxWidth / 2;
    translate([-offset, -offset, -eps]) cube([boxWidth, boxWidth, boxHeight + eps]);
}
}

GenericMountRing();
// GenericMountDisc();