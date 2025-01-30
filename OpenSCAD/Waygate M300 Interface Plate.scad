use <cylinder_outer.scad>
use <Generic Mount Ring.scad>


module num12Screw(shaftClyinder, headWidth, headHeight) {
  $fn = 64;
  cylinder_outer(h=20, d=shaftClyinder, center=true, fn=$fn);
  translate([0, 0, 3.51]) cylinder_outer(h= headHeight, d= headWidth, center=true, fn=$fn);  
} 
difference() {
  GenericMountRing();
  num12Screw(5.55625, 10.7, 3);
}           
