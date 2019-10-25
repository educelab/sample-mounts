use <Diamond Interface Plate.scad>;
use <cylinder_outer.scad>

// fr34
paperWidth = 73;
paperHeight = 82;
objWidth = 16;
objHeight = 23;
label = "Paris1, fr34";


/*
// fr39
paperWidth = 75;
paperHeight = 85;
objWidth = 16;
objHeight = 29;
label = "Paris1, fr39";
*/


/*
// fr47
paperWidth = 65;
paperHeight = 85;
objWidth = 18;
objHeight = 23;
label = "Paris2, fr47";
*/

/*
// fr143
paperWidth = 105;
paperHeight = 132;
objWidth = 30;
objHeight = 45;
label = "Paris2, fr143";
*/


layerThickness = 3;
buffer = 12.5;
backerHeight = paperHeight + 25;
showObject = false;

module object() {
    cube([paperWidth, .1, paperHeight], center=true);
    translate([0,.1,0]) cube([ objWidth, 1, objHeight], center = true);
}

module backer() {
    difference() {
        translate([0,-layerThickness/2,0]) cube([paperWidth-2*buffer, layerThickness, backerHeight], center = true);
        translate([(paperWidth-2*buffer)/2 - 1.5, -0.5, -paperHeight/2 - 2]) rotate([90,0,180]) linear_extrude(height=1) text(label, size=3, font="Arial Rounded MT Bold");
    }
}

module frame() {
    translate([0,0,0]) {
        difference() {
            cube([paperWidth-2*buffer, layerThickness, paperHeight+10], center = true);
            cube([paperWidth-2*buffer-10, layerThickness, paperHeight-10], center = true);
            translate([(paperWidth-2*buffer)/2 - 1.5,layerThickness/2 - 0.5, -paperHeight/2 - 1]) rotate([90,0,180]) linear_extrude(height=1) text(label, size=3, font="Arial Rounded MT Bold");
        }
    }
}

module stand() {
    difference() {
        union() {
            translate([0,-75/4,-backerHeight/2 + 2.5]) cube([20, 75/2, 5], center = true);
            translate([-35/2,-2*layerThickness,-backerHeight/2]) cube([35, layerThickness, 15]);
        }
        backer();
        translate([0,-27.5+12/2,-backerHeight/2-0.1]) cube([6.3, 20, DiamondPlateDepth() + 1], center=true);
        translate([0,-12,-backerHeight/2-0.1]) cylinder_outer(h=DiamondPlateDepth() + 1, d=6.3);
        translate([0,-31,-backerHeight/2-0.1]) cylinder_outer(h=DiamondPlateDepth() + 1, d=6.3);
    }    
}

/*
backer();
translate([0,0,(backerHeight - paperHeight - 10)/2]) {
    if(showObject) object();
    translate([0,layerThickness/2 + 1,0]) frame();
}*/

stand();
