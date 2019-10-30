use <cylinder_outer.scad>
use <Generic Mount Disc.scad>

clampVertW = 5;
clampHorzW = 7;
clampDepth = 12;
clampTotalH = 18.4;
clampHorzH = 3.5;
clampHorzYPos = clampTotalH - clampHorzH;

baseH = 16;
baseOffset = .9;
baseDiff = baseH - clampHorzYPos + baseOffset;
baseDiam = 138;
baseRad = baseDiam/2;

showClamps = false;
flatEdges = false;

module rightArm()
{
    translate([0,0,baseDiff]) rotate([90,0,0]) import("../Models/Book-Base.stl");
    base();
}

module leftArm() {
    translate([0,0,baseDiff]) rotate([90,0,0]) import("../Models/Book-Arm.stl");
}

module base() {
    difference() {
        cylinder_outer(d=baseDiam, h=baseH, fn=512);
        rotate([0,0,0]) translate([-baseRad,0,0]) diffClamp(); 
        rotate([0,0,120]) translate([-baseRad,0,0]) diffClamp();
        rotate([0,0,240]) translate([-baseRad,0,0]) diffClamp();
    }
    
    if(showClamps) {
        color("MediumAquaMarine") {
        rotate([0,0,0]) translate([-baseRad,0,0]) clamp(); 
        rotate([0,0,120]) translate([-baseRad,0,0]) clamp();
        rotate([0,0,240]) translate([-baseRad,0,0]) clamp();
        }
    }
}

module diffClamp() {
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

module clamp() {
    translate([0, -clampDepth/2  ,0]) {
        translate([0,0,0]) cube([clampVertW, clampDepth, clampTotalH]);
        translate([0,0,clampHorzYPos]) cube([clampHorzW, clampDepth, clampHorzH]);
    }
}

rightArm();
//leftArm();
// base();