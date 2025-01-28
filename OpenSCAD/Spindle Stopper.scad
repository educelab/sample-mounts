use <cylinder_outer.scad>


// rod types:
// 0 -> 1/8"  -> 3.175mm
// 1 -> 3/16" -> 4.7625mm
// 2 -> 1/4"  -> 6.35mm
// 3 -> 5/16" -> 7.9375mm
rod_type = 3;
// stopper height (mm)
height = 20;

// internal variables
rod_diams = [3.175, 4.7625, 6.35, 7.93375];
bases = [10, 10, 10, 10];
lock1_positions = [0.5, 0.5, 0.55, 0.65];
lock2_positions = [0.275, 0.36, 0.44, 0.52];
eps = 0.4;
rounding = 0.25;
ring_diam = 6.35; 
ring_thickness = 1.778;
rod_diam = rod_diams[rod_type];
base = bases[rod_type];
lock1 = lock1_positions[rod_type];
lock2 = lock2_positions[rod_type];


module stopper(ring_cutout=false) {

hole = rod_diam;


difference() {
  rotate_extrude($fn=128)
  minkowski() {
    translate([rounding + hole/2, 0])
    polygon([[0,0],[base/2,0],[0,height]]);
    circle(rounding, $fn=64);
  }
  if(ring_cutout) {
    translate([0,0,height*.3]) cylinder_outer(d=ring_diam+eps, h=ring_thickness+eps, fn=128);
  }
}
}

box_w = base + rod_diam + rounding*2 + 1;
box_h = height + 1;
lock_depth = 1.25;

translate([2,0,0])
union() {
difference() {
  stopper();
  translate([0, base*lock1, 2.1]) cube([lock_depth,1,2], center=true);
  translate([0, -base*lock2, height*.6]) cube([lock_depth,1,2], center=true);
  translate([-box_w/2, 0, box_h/2 - rounding*2]) cube([box_w, box_w, box_h], center=true);
}
translate([0, -base*lock1, 2.1]) cube([lock_depth,1,2], center=true);
translate([0, base*lock2, height*.6]) cube([lock_depth,1,2], center=true);
}


/* 

Each half is identical, so only need one

translate([-2,0,0])
union() {
difference() {
  stopper();
  translate([0, -base*0.5, 2.1]) cube([lock_depth,1,2], center=true);
  translate([0, base*0.275, height*.6]) cube([lock_depth,1,2], center=true);
  translate([box_w/2, 0, box_h/2 - rounding*2]) cube([box_w, box_w, box_h], center=true);
}
translate([0, base*0.5, 2.1]) cube([lock_depth,1,2], center=true);
translate([0, -base*0.275, height*.6]) cube([lock_depth,1,2], center=true);
}
*/
