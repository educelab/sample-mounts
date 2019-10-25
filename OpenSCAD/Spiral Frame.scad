use <archimedean_spiral.scad>
use <cylinder_outer.scad>

// cp3 - 135mm x 103mm
// WARNING: Lots of hardcoded values in this thing...

sampleHeight = 103;
grooveThickness = 1;
spirals = 3.767;
startRadius = 2;
spacing = 2;
capHeight = 2;
coreHeight = sampleHeight - (capHeight*2);
coreDiameter = 23;
baseHeight = 3;
baseDiameter = coreDiameter + 2;

openFrame = true;
supportWidth = 2;

module spiral(h) {
    difference() {
        cylinder_outer(h=h, d=coreDiameter);
        archimedean_spiral_3d(height=h, thickness=grooveThickness, spirals=spirals, startradius=startRadius, spacing=spacing, armCenter=false, center=true);
        translate([0,-9.95,0]) cube([coreDiameter,grooveThickness,h]);
    }
}

module spiralTube(h) {
    union() {
    intersection() {
        spiral(h);
        translate([2,-coreDiameter/2 + spacing/2 - .15,0]) cylinder_outer(h=h, d=1.33);
    }
    
    
    difference() {
        spiral(h);
        translate([2,-coreDiameter/2 + spacing/2 - .15,0]) {
            cylinder_outer(h=h, d=1.33);
            translate([0, -1.5/2,0]) cube([5, 1.5, h]);
        }
    }
    }
}

module differenceBlocks() {
    translate([-(startRadius*0.5) - spacing, -startRadius - spacing,0]) rotate([0,0,45])cube([2,supportWidth, coreHeight]);
    translate([supportWidth/2, startRadius + 1.75*spacing,0]) rotate([0,0,90]) cube([2,supportWidth, coreHeight]);
    translate([(startRadius*0.5) + 1.75*spacing, -startRadius - 1.15*spacing,0]) rotate([0,0,-45])cube([2,supportWidth, coreHeight]);
    translate([-grooveThickness/2 - 4.25*spacing, -supportWidth/2,0]) rotate([0,0,0]) cube([2,supportWidth, coreHeight]);
    translate([0,-supportWidth*.65 - 5.25*spacing,0]) cube([4,supportWidth, coreHeight]);
    translate([startRadius + 1.*spacing - 2, supportWidth/2 + 4.25*spacing,0]) rotate([0,0,-25])cube([4,supportWidth+1, coreHeight]);
}

// base
translate([0,0,-baseHeight + 0.1]) cylinder_outer(h=baseHeight, d=baseDiameter);

// bottom cap
spiralTube(capHeight);

// core support
translate([0,0,capHeight]) {
    if(openFrame) {
        // Central Spire
        cylinder_outer(h=coreHeight, r=startRadius*.95);
        //translate([0,0,coreHeight /2]) spiralTube(capHeight);
    } else {
        // Alignment walls
        intersection() {
            spiralTube(coreHeight);
            differenceBlocks();
        }
    }
}

// top cap 
translate([0,0,capHeight+coreHeight]) spiralTube(capHeight);