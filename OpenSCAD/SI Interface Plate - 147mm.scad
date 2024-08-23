use <Generic Mount Ring.scad>;
use <Generic Mount Disc.scad>;
use <cylinder_outer.scad>

plateW = 148; // diameter mm
plateD = 12.7; // depth mm

eps = 0.4;
holeDist = 18.5; // hole pitch mm
holeDiam = 8 + eps*2; // 8-32 nominal OD: 4.1646mm
recessDiam = 18 + eps*2;
recessDepth = 6 + eps;
cols = 7;
rows = 8;

function SIPlateWidth() = plateW;
function SIPlateDepth() = plateD;


module SIHoleGrid(rangeX = [0 : cols - 1], rangeY = [0 : rows - 1]) {
    colT = (cols - 1) * holeDist / 2;
    rowT = (rows - 1) * holeDist / 2;
    translate([-colT, -rowT, 0]) {
    for(y = rangeY) {
        for(x = rangeX) {
            translate([x*holeDist, y*holeDist, -.5]) cylinder_outer(h = plateD + 1, d=holeDiam, fn=64);
            translate([x*holeDist, y*holeDist, recessDepth]) cylinder_outer(h = recessDepth+15, d=recessDiam, fn=64);
        }
    }
    }
}

module SIMountRing() {
    h=11;
    difference() {
    union() {
        difference() {
            translate([0,0 , -h]) cylinder_outer(h = h, d = plateW, fn=128);
            translate([0, 0, -h-0.5]) cylinder_outer(h=12, d=44, fn=128);
        }
        GenericMountRing();
    }
    
    translate([0, 0, -plateD]) {    
        // cols 0,6
        SIHoleGrid(rangeX=[0:6:6], rangeY=[2:5]);
        // cols 1,5
        SIHoleGrid(rangeX=[1:4:5], rangeY=[1:6]);
        // cols 2,4
        SIHoleGrid(rangeX=[2:2:4], rangeY=[2:3:5]);
    }
    
    // remove cutouts in recesses
    translate([-46.25, 0, -recessDepth+0.1]) translate([-15.5/2, -35, 0]) cube([15.5, 70, recessDepth+eps]);
    translate([46.25, 0, -recessDepth+0.1]) translate([-15.5/2, -35, 0]) cube([15.5, 70, recessDepth+eps]);
    translate([-37, 0, -recessDepth+0.1]) translate([-6, -45, 0]) cube([12, 90, recessDepth+eps]);
    translate([37, 0, -recessDepth+0.1]) translate([-6, -45, 0]) cube([12, 90, recessDepth+eps]);
    translate([-37, 27.75, -recessDepth+0.1]) translate([-20, -5, 0]) cube([40, 10, recessDepth+eps]);
    translate([37, 27.75, -recessDepth+0.1]) translate([-20, -5, 0]) cube([40, 10, recessDepth+eps]);
    translate([-37, -27.75, -recessDepth+0.1]) translate([-20, -5, 0]) cube([40, 10, recessDepth+eps]);
    translate([37, -27.75, -recessDepth+0.1]) translate([-20, -5, 0]) cube([40, 10, recessDepth+eps]);
    }
    // support struts
    translate([-48, 0, -recessDepth]) translate([-20, -3.5/2, 0]) cube([40, 3.5, recessDepth]);
    translate([48, 0, -recessDepth]) translate([-20, -3.5/2, 0]) cube([40, 3.5, recessDepth]);
}



translate([0,0,-GenericMountDisc_Thickness()]) SIMountRing();