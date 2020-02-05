$fa = 1;
$fs = 0.4;

color("#808080")
cube([10,10,1], center=true);
translate([0,4.5,2.5-0.001])
    cube([10,1,5], center=true);
rotate([0,0,90])
    translate([0,4.5,2.5-0.001])
    cube([10,1,5], center=true);
    
translate([0,4.5-(1+0.75),2-0.001])
    cube([10,0.75,4], center=true);
rotate([0,0,90])
    translate([0,4.5-(1+0.75),2-0.001])
    cube([10,0.75,4], center=true);
    
translate([0,4.5-(1.5+1.25),1.5-0.001])
    cube([10,0.5,3], center=true);
rotate([0,0,90])
    translate([0,4.5-(1.5+1.25),1.5-0.001])
    cube([10,0.5,3], center=true);
    
translate([0,4.5-(2+1.5),1.0-0.001])
    cube([10,0.25,2], center=true);
rotate([0,0,90])
    translate([0,4.5-(2+1.5),1.0-0.001])
    cube([10,0.25,2], center=true);
    
translate([0,4.5-(2.5+1.675),0.5-0.001])
    cube([10,0.175,1], center=true);
rotate([0,0,90])
    translate([0,4.5-(2.5+1.675),0.5-0.001])
    cube([10,0.175,1], center=true);
    
translate([0,4.5-(2.75+1.7625),0.5-0.001])
    cube([10,0.0875,0.5], center=true);
rotate([0,0,90])
    translate([0,4.5-(2.75+1.7625),0.5-0.001])
    cube([10,0.0875,0.5], center=true);
    

rotate([0,0,180]){
    translate([0,4.5,2.5-0.001])
        cube([10,1,5], center=true);
    rotate([0,0,90])
        translate([0,4.5,2.5-0.001])
        cube([10,1,5], center=true);
        
    translate([0,4.5-(1+0.75),2-0.001])
        cube([10,0.75,4], center=true);
    rotate([0,0,90])
        translate([0,4.5-(1+0.75),2-0.001])
        cube([10,0.75,4], center=true);
        
    translate([0,4.5-(1.5+1.25),1.5-0.001])
        cube([10,0.5,3], center=true);
    rotate([0,0,90])
        translate([0,4.5-(1.5+1.25),1.5-0.001])
        cube([10,0.5,3], center=true);
        
    translate([0,4.5-(2+1.5),1.0-0.001])
        cube([10,0.25,2], center=true);
    rotate([0,0,90])
        translate([0,4.5-(2+1.5),1.0-0.001])
        cube([10,0.25,2], center=true);
        
    translate([0,4.5-(2.5+1.675),0.5-0.001])
        cube([10,0.175,1], center=true);
    rotate([0,0,90])
        translate([0,4.5-(2.5+1.675),0.5-0.001])
        cube([10,0.175,1], center=true);
}