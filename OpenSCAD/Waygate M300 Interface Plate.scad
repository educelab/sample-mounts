use <cylinder_outer.scad>
use <Generic Mount Ring.scad>
$fn = 64;
module rodHole() {
    translate([0,0,-6]) cylinder_outer (h=10, d=9.535, center=true, fn=$fn);
}
module num8Screw() {
    //the shaft of the screw
    cylinder_outer(h=20, d=4.21, center=true, fn=$fn);
    //the head of the screw
    translate([0, 0, 3.477]) cylinder_outer(h= 3.048, d= 7.9248, center=true, fn=$fn);  
} 
difference() {
    GenericMountRing();
    num8Screw();
} 
difference() {
    translate([0,0,-4]) cylinder_outer(h=7, d=60, center=true);
    translate([0,0,-1.6]) rodHole();
    num8Screw();
}
difference() {
    translate([0,0,-1.5]) cube(12, center=true);
    translate([0,0,-1.6]) rodHole();
    num8Screw();
}