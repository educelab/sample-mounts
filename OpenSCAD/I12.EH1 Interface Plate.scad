use <cylinder_outer.scad>
// use <Generic Mount Ring.scad>
// use <Generic Mount Disc.scad>
use <Generic Mount Ring 65mm.scad>
use <Generic Mount Disc 65mm.scad>

plateW = 300;
plateD = 12.7;

eps = 0.4;
holeDist = 25;
holeDiam = 6.5 + eps*2;
recessDiam = 15 + eps*2;
recessDepth = 6 + eps;
cols = 11;
rows = 11;

function DiamondPlateWidth() = plateW;
function DiamondPlateDepth() = plateD;

module DiamondInterfaceHoles(rangeX = [1, cols], rangeY = [1, rows], recess = false, circular = false) {
    for(y = [rangeY[0] : rangeY[1]]) {
        for(x = [rangeX[0] : rangeX[1]]) {
            if(circular) {
                x2 = abs(x - 12/2);
                y2 = abs(y - 12/2);
                if(x2 + y2 <= 14/2) {
                    translate([x*holeDist, y*holeDist, -.5]) cylinder_outer(h = plateD + 1, d=holeDiam);
                    if(recess) {
                        translate([x*holeDist, y*holeDist, recessDepth]) cylinder_outer(h = recessDepth+15, d=recessDiam);
                    }
                }
            } else {    
                translate([x*holeDist, y*holeDist, -.5]) cylinder_outer(h = plateD + 1, d=holeDiam);
                if(recess) {
                    translate([x*holeDist, y*holeDist, recessDepth]) cylinder_outer(h = recessDepth+15, d=recessDiam);
                }
            }
            
        }
    }
}

module DiamondInterfacePlate() {
    translate([-plateW/2, -plateW/2, -plateD])
    difference() {
        cube([plateW, plateW, plateD]);
        DiamondInterfaceHoles();
    }
}

module DiamondInterfacePlateCircular() {
    difference() {
        translate([0,0,-plateD]) cylinder_outer(h=plateD, d=400);
        translate([-plateW/2, -plateW/2, -plateD]) DiamondInterfaceHoles(circular=true);
    }
}

module DiamondMountRing() {
    h=11;
    difference() {
    union() {
        translate([0,0 , -h]) cylinder_outer(h = h, d = 175);
        GenericMountRing();
    }
    
    
    translate([-plateW/2, -plateW/2, -plateD]) {
        DiamondInterfaceHoles(rangeX=[3,3], rangeY=[5,7]);
        DiamondInterfaceHoles(rangeX=[9,9], rangeY=[5,7]);
        DiamondInterfaceHoles(rangeX=[4,4], rangeY=[4,8]);
        DiamondInterfaceHoles(rangeX=[8,8], rangeY=[4,8]);
        DiamondInterfaceHoles(rangeX=[5,7], rangeY=[3,3]);
        DiamondInterfaceHoles(rangeX=[5,7], rangeY=[9,9]);
    
        // recessed for bolts
        DiamondInterfaceHoles(rangeX=[3,3], rangeY=[6,6], recess=true);
        DiamondInterfaceHoles(rangeX=[4,4], rangeY=[4,4], recess=true);
        DiamondInterfaceHoles(rangeX=[4,4], rangeY=[8,8], recess=true);
        DiamondInterfaceHoles(rangeX=[8,8], rangeY=[4,4], recess=true);
        DiamondInterfaceHoles(rangeX=[8,8], rangeY=[8,8], recess=true);
        DiamondInterfaceHoles(rangeX=[9,9], rangeY=[6,6], recess=true);
    }
    }
}

translate([0,0,-GenericMountDisc_Thickness()]) DiamondMountRing();