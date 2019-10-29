use <cylinder_outer.scad>
use <Generic Mount Disc.scad>

baseH = 16;
baseDiff = baseH-14.9;
baseDiam = 138;
baseRad = baseDiam/2;

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
        cylinder_outer(d=baseDiam, h=baseH, fn=128);
        angle = 30;
        rotate([0,0,30]) translate([-baseRad,0,0]) clamp();
        rotate([0,0,150]) translate([-baseRad,0,0]) clamp();
        rotate([0,0,270]) translate([-baseRad,0,0]) clamp();
    }
}

module clamp() {
    clampW = 12.3;
    translate([0,-clampW/2  ,0]) {
        w = 10;
        diff = w - 5;
        translate([-diff,0,0]) cube([w, clampW, 18.4]);
        translate([0,0,18.4 - 3.5]) cube([10, clampW, 3.5]);
    }
}

//rightArm();
//leftArm();
base();
