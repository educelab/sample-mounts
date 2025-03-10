use <cylinder_outer.scad>
use <Generic Mount Ring.scad>
$fn = 64;


module rodHole() {
    translate([0,0,-10]) cylinder_outer (h=10, d=19.05, center=true);
}
module num8Screw() {
    //the shaft of the screw
    cylinder_outer(h=20, d=7.9375, center=true);
    //the head of the screw
    translate([0, 0, 1.04]) cylinder_outer(h= 7.9348, d= 11.9226, center=true);  
} 
difference() {
    GenericMountRing();
    num8Screw();
    rodHole();
} 
difference() {
    translate([0,0,-4]) cylinder_outer(h=7, d=60, center=true);
    num8Screw();
    rodHole();
}
difference() {
    translate([0,0,-1.5]) cube(12, center=true);
    num8Screw();
    rodHole();
}

difference() {
    translate([0,0,-10.9]) cylinder_outer(h=7, r=67.4, center = true);
    num8Screw();
    rodHole();
}