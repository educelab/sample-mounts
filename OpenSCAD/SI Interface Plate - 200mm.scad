use <Generic Mount Ring.scad>;
use <Generic Mount Disc.scad>;
use <cylinder_outer.scad>

plateW = 200; // diameter mm
plateD = 12.7; // depth mm

eps = 0.4;
holeDist = 18.5; // hole pitch mm
holeDiam = 8 + eps*2; // 8-32 nominal OD: 4.1646mm
recessDiam = 18 + eps*2;
recessDepth = 6 + eps;
cols = 11;
rows = 10;

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
    
    // holes and recesses
    translate([0, 0, -plateD]) {    
        // cols 1,9
        SIHoleGrid(rangeX=[1:8:9], rangeY=[2:7]);
        // cols 2,8
        SIHoleGrid(rangeX=[2:6:8], rangeY=[1:8]);
        // rows 1,10
        SIHoleGrid(rangeX=[4:1:6], rangeY=[0:9:9]);
    }
    
    // remove cutouts in recesses
    translate([-64.75, 0, -recessDepth+0.1]) translate([-18/2, -111.25/2, 0]) cube([18, 111.25, recessDepth+eps]);
    translate([64.75, 0, -recessDepth+0.1]) translate([-18/2, -111.25/2, 0]) cube([18, 111.25, recessDepth+eps]);
    translate([-55.5, 0, -recessDepth+0.1]) translate([-6, -116/2, 0]) cube([12, 116, recessDepth+eps]);
    translate([55.5, 0, -recessDepth+0.1]) translate([-6, -116/2, 0]) cube([12, 116, recessDepth+eps]);
    translate([-74, 0, -recessDepth+0.1]) translate([-6, -90/2, 0]) cube([12, 90, recessDepth+eps]);
    translate([74, 0, -recessDepth+0.1]) translate([-6, -90/2, 0]) cube([12, 90, recessDepth+eps]);
    translate([0, 83.25, -recessDepth+0.1]) translate([-46.25/2, -6, 0]) cube([46.25, 12, recessDepth+eps]);
    translate([0, -83.25, -recessDepth+0.1]) translate([-46.25/2, -6, 0]) cube([46.25, 12, recessDepth+eps]);
    }

}



translate([0,0,-GenericMountDisc_Thickness()]) SIMountRing();