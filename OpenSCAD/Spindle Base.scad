use <Generic Mount Disc 65mm.scad>;
use <cylinder_outer.scad>

baseRadius = GenericMountDisc_Diameter() / 2;
baseThickness = GenericMountDisc_Thickness() / 1.5;

// rod types:
// 0 -> 1/8"  -> 3.175mm
// 1 -> 3/16" -> 4.7625mm
// 2 -> 1/4"  -> 6.35mm
// 3 -> 5/16" -> 7.9375mm
rod_type = 0;

// internal variables
thicknesses_in = [1/8, 3/16, 1/4, 5/16];
eps=0.4;
thicknessIn = thicknesses_in[rod_type];
spindleThickness = thicknessIn * 25.4;
spindleRadius = eps + spindleThickness / 2;
spindleHeight = baseThickness + 100;

difference() {
  union() {
    GenericMountDisc();
    translate([0,0,GenericMountDisc_Thickness()]) cylinder_outer(h=baseThickness, r=baseRadius, fn=128);
  }

  translate([0, 0, 2 + GenericMountDisc_Thickness() / 2]) cylinder_outer(h=spindleHeight, r=spindleRadius);
  
  translate([-1,0,0]) intersection() {
  difference() {
    cylinder_outer(h=baseThickness*2, r=34.5, fn=128);
    cylinder_outer(h=baseThickness*2, r=32.5, fn=128);
  };
  translate([18,0,3.5])
  rotate([90, 0, 90]) linear_extrude(25) text(str(spindleThickness, "mm"), halign="center", size=6);
  }
  
  translate([1,0,0]) intersection() {
  difference() {
    cylinder_outer(h=baseThickness*2, r=34.5, fn=128);
    cylinder_outer(h=baseThickness*2, r=32.5, fn=128);
  };
  translate([-18,0,3.5])
  rotate([90, 0, 270]) linear_extrude(25) text(str(thicknessIn, "\""), halign="center", size=6);
  }
}


