use <cylinder_outer.scad>
use <Generic Mount Ring.scad>
use <Generic Mount Disc.scad>
// use <Generic Mount Ring 65mm.scad>
// use <Generic Mount Disc 65mm.scad>

plateW = 140;
plateD = 12.7;

eps = 0.4;
holeDist = 25;
holeDiam = 6.5 + eps*2;
recessDiam = 15 + eps*2;
recessDepth = 6 + eps;
cols = 11;
rows = 11;

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
    difference() {
    union() {
        translate([-plateW/2,-plateW/2,-plateD]) cube([plateW, plateW, plateD]);
        GenericMountRing();
    }

    translate([0,0,-plateD]) {
        // recessed for bolts
        DiamondInterfaceHoles(rangeX=[-2,-2], rangeY=[-2,2], recess=true);
        DiamondInterfaceHoles(rangeX=[-1,-1], rangeY=[-1,1], recess=true);
        DiamondInterfaceHoles(rangeX=[0,0], rangeY=[-1,-1], recess=true);
        DiamondInterfaceHoles(rangeX=[0,0], rangeY=[1,1], recess=true);
        DiamondInterfaceHoles(rangeX=[1,1], rangeY=[-1,1], recess=true);
        DiamondInterfaceHoles(rangeX=[2,2], rangeY=[-2,2], recess=true);
    }
    }
}

//translate([0,0,-GenericMountDisc_Thickness()]) DiamondInterfacePlate();
DiamondInterfacePlate();