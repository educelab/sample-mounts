use <cylinder_outer.scad>
use <Diamond Interface Plate.scad>

// Measurements in mm
objWidth = 212;
objHeight = 325;
objDepth = 15;

part="";
showObjectModel = false;

frameWindowBuffer = 3.1;
frameWindowHeight = objHeight;

bottomBuffer = 20;
horzSupportWidth = objWidth;
horzSupportHeight = 7;
horzSupportDepth = 5;

frameTotalHeight = bottomBuffer + frameWindowHeight + horzSupportHeight;

vertSupportWidth = objWidth / 5;
vertSupportHeight = frameTotalHeight;
vertSupportDepth = 2;

wallThickness = 3;
innerBuffer = 11.5;
innerDiameter = horzSupportWidth + (2 * innerBuffer);
outerDiameter = innerDiameter + (2 * wallThickness);

// Useful offsets
objOffsetZ = bottomBuffer + frameWindowBuffer;
topSupportOffsetZ = horzSupportHeight + frameWindowHeight;
vertSupportOffsetY = (objDepth / 2) + 1;

// Cap design
discDepth = 15;
discDiameter = outerDiameter + 2*wallThickness;
discInnerDiameter = outerDiameter - 2*wallThickness;

// tray parameters
ww = outerDiameter+5;
wo = objDepth / 2 + 10;
wd = 2;
standLength = 2*wo+wallThickness;
standDepth = 10;
standY = 0;
standZ = 1.5/2 + discDepth - wallThickness + 0.35;

stopperWallThickness = 1.5;

ribWallThickness=wallThickness;
ribHeight=2*ribWallThickness;

// paddle params
diag=sqrt(25*25 + 25*25);
wB = 60;
lB = 60;
wS = 125;
lS = 30;

$fn = 64;

module objModel() 
{
    translate([-objWidth/2, -objDepth/2, 0]) cube([objWidth, objDepth, objHeight]);
}

module foamModel() {
    difference() {
        translate([-objWidth/2, -wo, 0]) cube([objWidth, wo*2, objHeight]);
        objModel();
    }
}

module vacuumPackageModel() {
    pkgHeight = objHeight + (380 - objHeight)/2;
    translate([-objWidth/2, -1.5/2, 0]) cube([objWidth, 1.5, pkgHeight]);
}

module mountDisc() 
{   
    difference() {
        translate([0,0,-wallThickness]) cylinder_outer(discDepth, d=discDiameter);
        //cylinder_outer(discDepth, d=discInnerDiameter);
    }
}

module frameHorizontalSupport()
{
    translate([-horzSupportWidth/2, -horzSupportDepth/2, 0]) cube([horzSupportWidth, horzSupportDepth, horzSupportHeight]);
}

module frameVerticalSupportBase()
{
    tw = vertSupportWidth;
    bw = tw + 10;
    toi = (bw - tw) / 2;
    hi = vertSupportOffsetY;
    d = horzSupportHeight;
    b = 0.1;
    h = hi + b;
    tol = toi * h / hi;
    tor = bw - (tol);
    Points = [
      [  0,  0,  0 ],  //0
      [ bw,  0,  0 ],  //1
      [ bw,  d,  0 ],  //2
      [  0,  d,  0 ],  //3
      [ tol,  0,  h ],  //4
      [ tor,  0,  h ],  //5
      [ tor,  d,  h ],  //6
      [ tol,  d,  h ]]; //7
  
    Faces = [
      [0,1,2,3],  // bottom
      [4,5,1,0],  // front
      [7,6,5,4],  // top
      [5,6,2,1],  // right
      [6,7,3,2],  // back
      [7,4,0,3]]; // left
      
    translate([-bw/2, -hi, d]) rotate([-90, 0, 0]) polyhedron(Points, Faces);
}

module frameVerticalSupport()
{
    translate([-vertSupportWidth/2, 0, 0]) cube([vertSupportWidth, vertSupportDepth, vertSupportHeight]);
    frameVerticalSupportBase();
    translate([0,0,topSupportOffsetZ]) frameVerticalSupportBase();
}


module frame() 
{
    // bottom support
    frameHorizontalSupport();
    
    // Top support
    translate([0,0,topSupportOffsetZ]) frameHorizontalSupport();
    
    translate([-objWidth * (1.5/5), vertSupportOffsetY,0]) frameVerticalSupport();
    translate([ objWidth * (1.5/5), vertSupportOffsetY,0]) frameVerticalSupport();
}

module outerShell()
{
    difference() {
        cylinder_outer(h = frameTotalHeight, d = outerDiameter);
        cylinder_outer(h = frameTotalHeight, d = innerDiameter);
    }    
}

module innerShell()
{
    difference() {
        cylinder_outer(h = frameTotalHeight, d = innerDiameter);
        cylinder_outer(h = frameTotalHeight, d = innerDiameter - 2*stopperWallThickness);
    }   
}

module innerRib()
{
    difference() {
        cylinder_outer(h = ribHeight, d = innerDiameter);
        cylinder_outer(h = ribHeight, d = innerDiameter - 2*ribWallThickness);
    }   
}

module mergedTrays(stands=true)
{   
    difference() {
        union() {
            // base
            intersection() {
                translate([0, wo, frameTotalHeight / 2]) cube([ww, wallThickness, frameTotalHeight], center=true);
                cylinder_outer(h = frameTotalHeight, d = outerDiameter);
            }
            
            intersection() {
                translate([0, -wo, frameTotalHeight / 2]) cube([ww, wallThickness, frameTotalHeight], center=true);
                cylinder_outer(h = frameTotalHeight, d = outerDiameter);
            }
        }
        
        // Tray holes
        if(true) {
        num=4;
        gapSize = 10;
        totalWidth = ww - 4*wallThickness;
        holeSize = (totalWidth - (num+1)*gapSize)/num;
        totalHeight = frameTotalHeight - 2*wallThickness - holeSize/2 + gapSize;
        offsetX = holeSize + gapSize;
        rows = floor(totalHeight/offsetX) - 1;
        offsetY = (frameTotalHeight - rows*offsetX - gapSize)/2;
        translate([-totalWidth/2 + holeSize/2 + gapSize, 0, offsetY]) {
        for(y = [0 : rows]) {
            for(x = [0 : (y % 2) ? num - 2 : num - 1]) {
                translate([offsetX * x + (y % 2) * offsetX/2, 0, offsetX * y ]) rotate([90, 0, 0]) cylinder(h=2*wo + 2*wallThickness, d=holeSize, center=true);
            }
        }
        }
        }// if false
    }
   
    
    // alignment ridges
    if(false) {
        supportX = objWidth/2 - wallThickness/2;
        supportY = wo - wallThickness/2 - wd/2;
        supportZ = frameTotalHeight/2;
        translate([-supportX, -supportY, supportZ]) cube([wallThickness, wd, frameTotalHeight], center=true);
        translate([ supportX, -supportY, supportZ]) cube([wallThickness, wd, frameTotalHeight], center=true);
    }
    

    // stands
    if(stands) {
        translate([outerDiameter/3, 0, standZ]) cube([standLength, 2*(wo+wallThickness)+wallThickness, 1.5], center=true);
        translate([-outerDiameter/3, 0, standZ]) cube([standLength, 2*(wo+wallThickness)+wallThickness, 1.5], center=true);
        translate([outerDiameter/3, -wo-wallThickness, frameTotalHeight-2.5-1.5/2-.5]) cube([standLength, wallThickness, 1.5], center=true);
        translate([-outerDiameter/3, -wo-wallThickness, frameTotalHeight-2.5-1.5/2-.5]) cube([standLength, wallThickness, 1.5], center=true);
        translate([outerDiameter/3, wo+wallThickness, frameTotalHeight-2.5-1.5/2-.5]) cube([standLength, wallThickness, 1.5], center=true);
        translate([-outerDiameter/3, wo+wallThickness, frameTotalHeight-2.5-1.5/2-.5]) cube([standLength, wallThickness, 1.5], center=true);
    }
   
    
    // walls
    intersection() {
        translate([0, 0, frameTotalHeight / 2]) cube([ww, wo*2, frameTotalHeight], center=true);
        outerShell();
        
    }
    
    intersection() {
        translate([0, 0, standZ]) cube([ww, wo*2, 1.5], center=true);
        cylinder_outer(h = frameTotalHeight, d = outerDiameter);
    }
}

module trayLockCylinder() {
    scale([1,1,2]) rotate([0, 90, 0]) cylinder_outer(h = wallThickness+10, r = .9*wo, center=true);
}

module trayLockStopper() {
    
    scale([1,.4,3]) rotate([0, 90, 0]) 
    difference() {
        cylinder_outer(h = wallThickness+10, r = wo, center=true);
        translate([0, -wo, 0]) cube([wo*2, wo*2, wallThickness+10], center=true);
    }
}

module leftTray()
{
    intersection() {
        translate([outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
        outerShell();
    }
    
    difference() {
        // tray lock stopper
        intersection() {
            translate([-outerDiameter/2, -wo, frameTotalHeight/2]) trayLockStopper();
            innerShell();
        }
        
        // but make it flat so opposite tray's lock can slide in vertically
        intersection() {
            h2 = (innerDiameter/2) * (innerDiameter/2);
            lh2 = (wo/2) * (wo/2);
            y = sqrt(h2 - lh2);
            translate([-wallThickness-y+0.5,-wo, frameTotalHeight/2-3*wo])cube([wallThickness, wo, 6*wo]);
            translate([-outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
        }
    }
    
    difference() { 
        mergedTrays();
        translate([0, (outerDiameter+1)/2, frameTotalHeight / 2]) cube([outerDiameter+1, outerDiameter+1, frameTotalHeight+10], center=true);
        intersection() {
            translate([-outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
            outerShell();
        }
    }
}

module rightTray()
{
    intersection() {
        translate([-outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
        outerShell();
    }
    
    difference() {
        // tray lock stopper
        intersection() {
            translate([outerDiameter/2, wo, frameTotalHeight/2]) rotate([180,0,0]) trayLockStopper();
            innerShell();
        }
        // but make it flat so opposite tray's lock can slide in vertically
        intersection() {
            h2 = (innerDiameter/2) * (innerDiameter/2);
            lh2 = (wo/2) * (wo/2);
            y = sqrt(h2 - lh2);
            translate([y-0.5,0, frameTotalHeight/2-3*wo])cube([wallThickness, wo, 6*wo]);
            translate([outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
        }
    }
    
    difference() { 
        mergedTrays();
        translate([0, -(outerDiameter+1)/2, frameTotalHeight / 2]) cube([outerDiameter+1, outerDiameter+1, frameTotalHeight+10], center=true);
        intersection() {
            translate([outerDiameter/2, 0, frameTotalHeight/2]) trayLockCylinder();
            outerShell();
        }
    }
}

module cap() {
    difference() {
        mountDisc();
        mergedTrays();
        intersection() {
            translate([0,0,frameTotalHeight / 2]) cube([outerDiameter, wo*2 - 3*wallThickness, frameTotalHeight], center=true);
            cylinder_outer(h = frameTotalHeight, d = innerDiameter - 2*wallThickness);
        }
        difference() {
            outerShell();
            translate([0,0,frameTotalHeight / 2]) cube([outerDiameter+10, 2*wo + 3*wallThickness, frameTotalHeight], center=true);
        }
        difference() {
            cylinder_outer(h = frameTotalHeight, d = innerDiameter - 2*wallThickness);
            translate([0,0,frameTotalHeight / 2]) cube([outerDiameter+10, 2*wo + 3*wallThickness, frameTotalHeight], center=true);
        }
    }
}

module chambers() {
    difference() {
        union() {
            outerShell();
            translate([0,0,frameTotalHeight-ribHeight]) innerRib();
        }
        translate([0,0,frameTotalHeight / 2]) cube([outerDiameter+1, 2*wo + wallThickness, frameTotalHeight+1], center=true);
        notchDepth = discDepth - wallThickness;
        translate([0,0,notchDepth / 2]) cube([outerDiameter+10, 2*wo + 3*wallThickness, notchDepth], center=true);
        clip();
    }
    
    positionedHooks();
}

module chamberLeft() {
    difference() {
        chambers();
        translate([0, outerDiameter, frameTotalHeight / 2]) cube([outerDiameter*2, outerDiameter*2, frameTotalHeight+10], center=true);
    }
}

module chamberRight() {
    difference() {
        chambers();
        translate([0, -outerDiameter, frameTotalHeight / 2]) cube([outerDiameter*2, outerDiameter*2, frameTotalHeight+10], center=true);
    }
}

module clip() {
    difference() {
        union() {
            difference() {
                translate([0,0,frameTotalHeight-2.5]) {
                    intersection() {
                        translate([0,0,(wallThickness+5)/2]) cube([outerDiameter+2*wallThickness, 2*wo+wallThickness, wallThickness+5], center=true);
                        cylinder_outer(h = frameTotalHeight, d = outerDiameter+2*wallThickness);
                    }
                }
                cylinder_outer(h = frameTotalHeight, d = outerDiameter);
            }
            // stands
            difference() {
                translate([outerDiameter/3,0,frameTotalHeight-2.5]) rotate([0,0,90]) translate([0,0,(wallThickness+5)/2]) cube([2*wo+3*wallThickness, standLength, wallThickness+5], center=true);
                hull() mergedTrays(false);
            }
            difference() {
                translate([-outerDiameter/3,0,frameTotalHeight-2.5]) rotate([0,0,90]) translate([0,0,(wallThickness+5)/2]) cube([2*wo+3*wallThickness, standLength, wallThickness+5], center=true);
                hull() mergedTrays(false);
            }
            // vertical wall
            translate([-(innerDiameter)/2, wallThickness-1, frameTotalHeight+wallThickness+2.5]) cube([innerDiameter, wallThickness, 7.5]);
        }
        // gap
        translate([-(innerDiameter)/2, -4/2, frameTotalHeight]) cube([innerDiameter, 4, objHeight]);
    }
}

module hook() 
{
    hookOffset = ribWallThickness;
    hookGrooveWidth = 7;
    hookExtra = 1;
    hookLength = hookOffset + hookGrooveWidth + hookExtra;
    hookDiam = 8;
    
    cylinder(h=hookLength, d=hookDiam);
    translate([0,0,-ribWallThickness]) cylinder(h=hookLength*.5, d1=hookDiam+5, d2=hookDiam);
    translate([0,0,hookLength]) cylinder(h = 2, d = hookDiam+2.5);
}

module positionedHook()
{
    theta = 75.5;
    offset = outerDiameter; // (innerDiameter + outerDiameter)/2;
    x = sin(theta)*offset/2;
    y = cos(theta)*offset/2;
    difference() {
        translate([x,y,frameTotalHeight - 3*wallThickness]) rotate([0,90,0]) hook();
        cylinder_outer(h = frameTotalHeight, d = outerDiameter);
    }
}

module positionedHooks()
{
    positionedHook();
    mirror([1,0,0]) positionedHook();
    
    mirror([0,1,0]) {
         positionedHook();
         mirror([1,0,0]) positionedHook();
    }
}

module mountingPaddles()
{
    rotate([0,0,0]) {
    difference() {
        translate([0, 0, -wallThickness]) cylinder_outer(20, d=discDiameter+20, fn=128);
        mountDisc();
        cylinder_outer(h = frameTotalHeight, d = outerDiameter);
        translate([0,-(discDiameter+15)/2 + 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
        translate([0,(discDiameter+15)/2 - 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
        translate([0,(discDiameter+21)/2, 20-7-2.5]) rotate([90,0,0]) cylinder_outer(discDiameter+21, d=7);
        rotate([0,0,90]) {
            translate([0,-(discDiameter+15)/2 + 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
            translate([0,(discDiameter+15)/2 - 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
            translate([0,(discDiameter+21)/2, 20-7-2.5]) rotate([90,0,0]) cylinder_outer(discDiameter+21, d=7);
        }
    }
    difference() {
        union() {
            translate([-wB/2,-(discDiameter+10)/2 - lB, -wallThickness]) cube([wB, lB, 5]);
            mirror([0,1,0]) translate([-wB/2,-(discDiameter+10)/2 - lB, -wallThickness]) cube([wB, lB, 5]);
            rotate([0,0,90]){
                translate([-wB/2,-(discDiameter+10)/2 - lB, -wallThickness]) cube([wB, lB, 5]);
                mirror([0,1,0]) translate([-wB/2,-(discDiameter+10)/2 - lB, -wallThickness]) cube([wB, lB, 5]);
            }
        }
        rotate([0,0,45]) translate([-DiamondPlateWidth()/2, -DiamondPlateWidth()/2, -wallThickness]) {
             DiamondInterfaceHoles(rangeX=[1,2], rangeY=[1,2]);
             DiamondInterfaceHoles(rangeX=[1,2], rangeY=[10,11]);
             DiamondInterfaceHoles(rangeX=[10,11], rangeY=[1,2]);
             DiamondInterfaceHoles(rangeX=[10,11], rangeY=[10,11]);
        }
    }
    }
}

module thinMountingPaddles()
{
    rotate([0,0,0]) {
    difference() {
    union() {
        difference() {
            translate([0, 0, -wallThickness]) cylinder_outer(20, d=discDiameter+20, fn=128);
            translate([0,-(discDiameter+15)/2 + 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
            translate([0,(discDiameter+15)/2 - 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
            translate([0,(discDiameter+16)/2, 20-7-2.5]) rotate([90,0,0]) cylinder_outer(discDiameter+21, d=7);
            rotate([0,0,90]) {
                translate([0,-(discDiameter+15)/2 + 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
                translate([0,(discDiameter+15)/2 - 3, 20-12.7-wallThickness]) rotate([0,0,90]) translate([-6.5/2, -13/2, 0]) cube([6.5, 13, 12.8]);
                translate([0,(discDiameter+16)/2, 20-7-2.5]) rotate([90,0,0]) cylinder_outer(discDiameter+21, d=7);
            }
        }

        translate([-wS/2, -(discDiameter-20)/2 - lS, -wallThickness]) cube([wS, lS, 5]);
        mirror([0,1,0]) translate([-wS/2, -(discDiameter-20)/2 - lS, -wallThickness]) cube([wS, lS, 5]);
        rotate([0,0,90]){
            translate([-wS/2,-(discDiameter-20)/2 - lS, -wallThickness]) cube([wS, lS, 5]);
            mirror([0,1,0]) translate([-wS/2,-(discDiameter-20)/2 - lS, -wallThickness]) cube([wS, lS, 5]);
        }
    }
    mountDisc();
    cylinder_outer(h = frameTotalHeight, d = outerDiameter);
    rotate([0,0,0]) translate([-DiamondPlateWidth()/2, -DiamondPlateWidth()/2, -wallThickness - 1]) {
        DiamondInterfaceHoles(rangeX=[1,1],rangeY=[4,4],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[1,1],rangeY=[8,8],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[4,4],rangeY=[1,1],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[4,4],rangeY=[11,11],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[8,8],rangeY=[1,1],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[8,8],rangeY=[11,11],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[11,11],rangeY=[4,4],recess = true, circular=true);
        DiamondInterfaceHoles(rangeX=[11,11],rangeY=[8,8],recess = true, circular=true);
    }
    }
    }
}

if(showObjectModel){
    translate([0,0,objOffsetZ]) {
        color([1,0,0]) objModel();
        vacuumPackageModel();
    }
}

if(part == "l") {
    leftTray();
} else if (part == "r") {
    rightTray();
} else if (part == "cl") {
    chamberLeft();
} else if (part == "cr") {
    chamberRight();
} else if (part == "cap") {
    cap();
} else if (part == "clip") {
    clip();
} else if (part == "sm_mounts") {
    intersection() {
        thinMountingPaddles();
        translate([0, (discDiameter+100)/2, 0]) cube([wS+10, discDiameter+100, 50], center = true);
    }
} else if (part == "lg_mounts") {
    intersection() {
        mountingPaddles();
        translate([0, (discDiameter+2*lB + 20)/2, 0]) cube([wB+25, discDiameter+2*lB + 20, 50], center = true);
    }
} else if (part == "all") {
    translate([0,0,-discDepth]) cap();
    translate([0,-10,0]) chamberLeft();
    translate([0, 10,0]) chamberRight();
    translate([0,-5,0]) leftTray();
    translate([0, 5,0]) rightTray();
    translate([0,0,10]) clip();
} else if (part == "") {
    cap();
    chamberLeft();
    chamberRight();
    leftTray();
    rightTray();
    clip();
}

