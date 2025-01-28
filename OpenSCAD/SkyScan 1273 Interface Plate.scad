use <cylinder_outer.scad>
use <Generic Mount Ring 65mm.scad>
use <Generic Mount Disc 65mm.scad>

clampVertW = 5;
clampHorzW = 7;
clampDepth = 12;
clampTotalH = 18.4;
clampHorzH = 3.5;
clampHorzYPos = clampTotalH - clampHorzH;

baseH = 16;
baseOffset = .9;
baseDiff = baseH - clampHorzYPos + baseOffset;
baseDiam = 112.5 + 45;
baseRad = baseDiam/2;

showClamps = false;
flatEdges = true;


module SkyScan1273BasePlate() {
    translate([0,0,-baseH]) {
    difference() {
        cylinder_outer(d=baseDiam, h=baseH, fn=512);
        rotate([0,0,0]) translate([-baseRad,0,0]) SkyScan1273ClampCutout(); 
        rotate([0,0,120]) translate([-baseRad,0,0]) SkyScan1273ClampCutout();
        rotate([0,0,240]) translate([-baseRad,0,0]) SkyScan1273ClampCutout();
    }
    
    if(showClamps) {
        color("MediumAquaMarine") {
        rotate([0,0,0]) translate([-baseRad,0,0]) SkyScan1273Clamp(); 
        rotate([0,0,120]) translate([-baseRad,0,0]) SkyScan1273Clamp();
        rotate([0,0,240]) translate([-baseRad,0,0]) SkyScan1273Clamp();
        }
    }
    }
}

// cutouts for clamps
module SkyScan1273ClampCutout() {
    diffVertW = 10;
    diffVertXPos = -(diffVertW - clampVertW);
    diffHorzW = 10;
    diffHorzXPos = 0;
    diffDepth = (flatEdges) ? baseDiam : clampDepth + 2;
    diffVertBuffer = 1;
    diffVertH = clampTotalH + diffVertBuffer;
    diffVertZPos = 0 - diffVertBuffer;
    diffHorzBuffer = 0.5;
    diffHorzH = clampHorzH + diffHorzBuffer;
    diffHorzYPos = clampHorzYPos - diffHorzBuffer;
    translate([0, -diffDepth/2  ,0]) {
        translate([diffVertXPos,0,diffVertZPos]) cube([diffVertW, diffDepth, diffVertH]);
        translate([diffHorzXPos,0,diffHorzYPos]) cube([diffHorzW, diffDepth, diffHorzH]);
    }
}


// Clamps (for testing)
module SkyScan1273Clamp() {
    translate([0, -clampDepth/2  ,0]) {
        translate([0,0,0]) cube([clampVertW, clampDepth, clampTotalH]);
        translate([0,0,clampHorzYPos]) cube([clampHorzW, clampDepth, clampHorzH]);
    }
}

module SkyScan1273InterfacePlate() {
  union() {
    GenericMountRing();
    SkyScan1273BasePlate();
  }
}

SkyScan1273InterfacePlate();