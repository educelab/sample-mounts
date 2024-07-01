// Includes
use <Generic Mount Disc.scad>
// use <Generic Mount Disc 65mm.scad>
use <cylinder_outer.scad>

//// CLI Params ////
scroll = "/Users/stephen/data/Herculaneum_Scrolls/Bodleian Scrolls/3D/202405 - Diamond scan cases/Scroll 25/4 - Downsampled Model/20240515174439_Bod-Scroll25-full+mask_100k.stl";
lining = "/Users/stephen/data/Herculaneum_Scrolls/Bodleian Scrolls/3D/202405 - Diamond scan cases/Scroll 25/7 - Lining/20240515174439_Bod-Scroll25-full+mask_lining.stl";
liningWall = "/Users/stephen/data/Herculaneum_Scrolls/Bodleian Scrolls/3D/202405 - Diamond scan cases/Scroll 25/7 - Lining/20240515174439_Bod-Scroll25-full+mask_liningwall.stl";
side = "s";
liningCavity = "";

previewLiningWall = false;
previewModel = false;

scrollHeight = 163.89;
liningDiameter = 67;
modelRotate = [0, 0, 107];
modelTranslate = [0, 0, 85];
liningOffset = 3;
wallThickness = 2;

generateOuterCylinder = true;
honeycomb = true;
honeycombHoleEdges = 6;
honeycombNumCols = 12;
honeycombSpacing = 1.5;

alignmentNubs=[
    [-35, 10],
    [-35, 95],
    [-35, 180],
    [35, 10],
    [35, 95],
    [35, 180],
];
alignmentNubSize=3;
alignmentNubDepth=1.5;
alignmentNubMargin=0.5;

overhangRemoval = false;
overhangStepSize = 0.5;

escapeHoles = false;
escapeOffset = 1.5;
escapeDiameter = 4;
escapeAngle = 15;

labelLine1 = "PHerc. Bod. 25";
labelLine2 = "V1a";
labelLineHeight = 3;
labelDepth = 0.5;

markerRings = true;

// Minor Parameters (in mm)
bottomBuffer = 5;
topBuffer = 5;
internalGap = 3;

// Other Minor Parameters
baseLengthScale = 1.0;
$fn = 64;

////////////////////

// Useful Vars
bottomWallThickness = max(2, wallThickness);
liningWallDiameter = liningDiameter + (2 * wallThickness);
liningHeight = scrollHeight + liningOffset * 2;
liningWallHeight = liningHeight + (2 * wallThickness);
innerDiameter = liningWallDiameter + (2 * internalGap);
innerHeight = bottomBuffer + liningWallHeight + topBuffer;
outerDiameter = innerDiameter + (2 * wallThickness) ;
outerHeight = innerHeight + bottomWallThickness + wallThickness;

outerShellZ = 0;
innerCavityZ = outerShellZ + bottomWallThickness;
liningZ = innerCavityZ + bottomBuffer + wallThickness;
overhangIterations = max(ceil((liningDiameter + wallThickness) * 0.5 / overhangStepSize), 1);

cubeWidth = outerDiameter * 1.1;
cubeDepth = outerDiameter * 2;
cubeHeight = outerHeight * 1.1;

escapeDistance = ((((liningDiameter+wallThickness)/2) + ((outerDiameter-wallThickness)/2))/2) + escapeOffset;
escapeOffsetX = cos(escapeAngle) * escapeDistance;
escapeOffsetY = sin(escapeAngle) * escapeDistance;
escapeLBottomZ = -GenericMountDisc_Thickness();
escapeRBottomZ = 0;
escapeTopZ = outerHeight - wallThickness;

// Base
baseLength = GenericMountDisc_Thickness() + outerHeight*baseLengthScale;
baseWidth = max(GenericMountDisc_Diameter(), outerDiameter) + 0.5;
baseThickness = 12.7;
baseWallThickness = 5;
baseOffset = [-baseWidth/2, -baseWidth/2 - baseThickness - 0.5, -GenericMountDisc_Thickness()];
stripWidth = 30;
pegRadius = GenericMountDisc_NotchDiameter() / 2 - 0.2;
pegOffset = [0, -GenericMountDisc_Diameter()/2 + pegRadius/4, GenericMountDisc_NotchZ() - GenericMountDisc_Thickness()];
wallHeight = baseWidth/2 - GenericMountDisc_Diameter()/4 + 0.5;
standWallWidth = outerDiameter + 0.5;
standWallHeight = baseWidth/2 - outerDiameter/4;
standWallThickness = GenericMountDisc_Thickness();
supportWidth = baseWidth;
supportDepth = 15;

//// Model Functions ////
// Scroll 3D model
module scrollModel() {
    if(scroll != "") {
        translate(modelTranslate) rotate(modelRotate) import(scroll);
    } else {
        cylinder(h=liningHeight - 2*wallThickness, d=liningDiameter - 2*wallThickness);
    }
}

// Lining (what the scroll rests on) model
module liningModel() {
    if(lining != "") {
        translate(modelTranslate) rotate(modelRotate) import(lining);
    } else {
        cylinder(h=liningHeight, d=liningDiameter);
    }
}

// Thickened lining model to create wall
module liningWallModel() {
    if(liningWall != "") {
        translate(modelTranslate) rotate(modelRotate) import(liningWall);
    } else {
        translate([0,0,-wallThickness]) cylinder(h=liningWallHeight, d=liningWallDiameter);
    }
}

// Complete model of the lining cavity (lining + wall)
module liningCavity() {
    if(liningCavity != "")
    {
        // Imported lining cavity should have already been rotated
        translate([0, 0, liningZ]) translate(modelTranslate) import(liningCavity);
    } else {
        translate([0, 0, liningZ])  difference() {
            liningWallModel();
            liningModel();
        }
    }
}

module markerRing() {
    rotate_extrude() translate([outerDiameter/2, 0, 0]) circle(0.5, $fn=100);
    ringHeight = 3;
    rotate_extrude() translate([outerDiameter/2-wallThickness, -ringHeight/2, 0]) square([wallThickness, ringHeight]);
}

module honeycombCylinder() {
    gapRot = (honeycombSpacing / outerDiameter) * 180 / PI;
    hexRot = (360 - gapRot * honeycombNumCols) / honeycombNumCols;
    totalRot = hexRot + gapRot;
    hexDiam = outerDiameter * sin(hexRot / 2);
    hexLen = outerDiameter / 2;
    z_step = sin(60) * hexDiam + sin(60) * honeycombSpacing;
    
    difference() {
        cylinder(h=outerHeight, d=outerDiameter);
        translate([0, 0, innerCavityZ]) cylinder(h=innerHeight, d=innerDiameter);
        for(y = [0 : outerHeight / z_step + 1]) {
            translate([0,0, y * z_step]) 
            for(x = [0 : (honeycombNumCols - 1)]) {
                rotate([0,0, x * totalRot + totalRot / 2 * (y % 2)]) 
                translate([0,hexLen/2,0])
                rotate([90,90,0])
                cylinder(h=hexLen, d=hexDiam, $fn=honeycombHoleEdges, center=true);
            }
        }
    }
    
    // Cylinder end caps
    difference() {
        cylinder(h=outerHeight, d=outerDiameter);
        translate([0, 0, innerCavityZ]) cylinder(h=innerHeight, d=innerDiameter);
        cutboxH = outerHeight - wallThickness - bottomWallThickness;
        translate([0, 0, cutboxH/2 + bottomWallThickness]) cube([outerDiameter + 1, outerDiameter + 1, cutboxH], center=true);
    }

    // Scroll top and bottom marker rings
    if(markerRings) {
        // lining bottom
        translate([0, 0, liningZ]) translate(modelTranslate) translate([0, 0, -liningHeight/2]) markerRing();
        // nominal scroll bottom
        translate([0, 0, liningZ]) translate(modelTranslate) translate([0, 0, -scrollHeight/2]) markerRing();
        // nominal scroll top
        translate([0, 0, liningZ]) translate(modelTranslate) translate([0, 0, scrollHeight/2]) markerRing();
        // lining top
        translate([0, 0, liningZ]) translate(modelTranslate) translate([0, 0, liningHeight/2]) markerRing();
        // scroll/lining midpoint
        translate([0, 0, liningZ]) translate(modelTranslate) markerRing();
    }
}

// Generate outer and inner cylinder
module hollowCylinder() {
    difference() {
    if(honeycomb && !previewLiningWall) {
        honeycombCylinder();
    } else {
        difference() {
            cylinder(h=outerHeight, d=outerDiameter);
            translate([0, 0, innerCavityZ]) cylinder(h=innerHeight, d=innerDiameter);
        }
    }
    
    if(!generateOuterCylinder && !previewLiningWall) {
        test_rot = 5;
        translate([0,-outerDiameter/4 - 5,outerHeight+2]) rotate([-test_rot,0,0]) scale([outerDiameter*2,outerDiameter*1.5,outerHeight*2]) sphere(d=1);
        translate([0,outerDiameter/4 + 5,outerHeight+2]) rotate([test_rot,0,0]) scale([outerDiameter*2,outerDiameter*1.5,outerHeight*2]) sphere(d=1);
    }
    }
}

// Wall between the left and right sections
module dividingWall()
{
    dividerWidth = outerDiameter;
    dividerHeight = outerHeight;
    dividerThickness = 2 * wallThickness;
    difference() {
        intersection() {
            translate([-dividerWidth/2,-dividerThickness/2,0]) cube([dividerWidth, dividerThickness, dividerHeight]);
            cylinder(h=outerHeight, d=outerDiameter);
        }
        translate([0,0,liningZ]) liningModel();
    }
}

module escapeHole(base=false)
{
    if(base) {
        cylinder_outer(h=GenericMountDisc_Thickness() + innerCavityZ, r=escapeDiameter/2);
    } else {
        cylinder_outer(h=wallThickness, r=escapeDiameter/2);
    }
}

// Added depth to avoid having coincident faces when differencing
labelDepthExtra = 0.1;
module labelModel() {
    linear_extrude(labelDepth + labelDepthExtra) {
        rotate([0, 180, 0]) {
            text(labelLine1, labelLineHeight, halign="center", font="Arial Rounded MT Bold");
            translate([0, -1.5 * labelLineHeight, 0]) text(labelLine2, labelLineHeight, halign="center", font="Arial Rounded MT Bold");
        }
    }
}

// Full case (unseparated) with cavity + walls
module completeCase()
{
    union() {
        // Outer shell
        hollowCylinder();

        //  Dividing wall
        dividingWall();

        // Generate tray lining and wall
        liningCavity();
    }
}

// Generate the "left" half cylinder
module leftCase() {
    difference() {
        union() {
            completeCase();

            if(overhangRemoval) {
                for(i=[0:overhangIterations]) {
                    translate([0, i*overhangStepSize, liningZ]) liningWallModel();
                }
            }
        }

        translate([-cubeWidth/2, 0, 0]) cube([cubeWidth, cubeDepth, cubeHeight]);

        if(overhangRemoval) {
            for(i=[0:overhangIterations]) {
                translate([0, i*overhangStepSize, liningZ]) liningModel();
            }
        }
    }
}

// Generate the "right" half cylinder
module rightCase() {
    difference() {
        union() {
            completeCase();

            if(overhangRemoval) {
                for(i=[0:overhangIterations]) {
                    translate([0, -i*overhangStepSize, liningZ]) liningWallModel();
                }
            }
        }

        translate([-cubeWidth/2, -cubeDepth, 0]) cube([cubeWidth, cubeDepth, cubeHeight]);

        if(overhangRemoval) {
            for(i=[0:overhangIterations]) {
                translate([0, -i*overhangStepSize, liningZ]) liningModel();
            }
        }
    }
}

//// Case stand pieces ////
module standPeg() {
    translate([0, 0, 0]) rotate([-90,0,0]) cylinder_outer(h=pegRadius, r=pegRadius, center=true);
}

eps = 0.4;
holeDist = 25;
holeDiam = 6.5 + eps*2;
recessDiam = 15 + eps*2;
recessDepth = 6 + eps;
cols = 11;
rows = 11;
plateD = baseThickness;

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
                translate([x*holeDist+7, y*holeDist, -.5]) cylinder_outer(h = plateD + 1, d=holeDiam);
                if(recess) {
                    translate([x*holeDist+7, y*holeDist, recessDepth]) cylinder_outer(h = recessDepth+15, d=recessDiam);
                }
            }
            
        }
    }
}

nubWidth = 6;

module standBase() {
     translate([baseWidth, 0, 0])
     rotate([90, 0, 180])
     difference() {
        union() {
            cube([baseWidth, baseLength, baseThickness]);
            translate([baseWidth, baseLength/8, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([baseWidth, 5*baseLength/16, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([baseWidth, baseLength/2, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([baseWidth, 11*baseLength/16, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([baseWidth, 7*baseLength/8, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([-nubWidth, baseLength/8, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([-nubWidth, 5*baseLength/16, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([-nubWidth, baseLength/2, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([-nubWidth, 11*baseLength/16, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
            translate([-nubWidth, 7*baseLength/8, baseThickness-nubWidth])
            rotate([0, 90, 0])
            cylinder(h=nubWidth, r=3*nubWidth/4);
        }
        
        DiamondInterfaceHoles(rangeX=[1,3], rangeY=[2,6], recess=true);

        // diff out the middle strip
        // diffWidth = (baseWidth - stripWidth) / 2 + 1;
        // diffXOffset = (baseWidth - stripWidth) / 2;
        // diffThickness = baseThickness*2;
        // diffHeight = baseLength - (stripWidth * 2);
        // translate([diffXOffset + stripWidth, -diffThickness/4, stripWidth]) cube([diffWidth, diffThickness, diffHeight]);
        // translate([-1, -diffThickness/4, stripWidth]) cube([diffWidth, diffThickness, diffHeight]);

        // Label
        // translate([baseWidth/2, baseThickness + labelDepthExtra, baseLength / 2])
            // rotate([90, -90, 0]) labelModel();
           
        
    }
}

module standWallSupport(w) {
    hyp = sqrt(2*(supportDepth*supportDepth));
    translate([0,0,supportDepth/2]) rotate([0,0,90]) difference() {
        cube([supportDepth, w, supportDepth], true);
        rotate([0,45,0]) translate([0,0,hyp/6]) cube([hyp + 1, supportWidth+1, supportDepth], true);
    }
}

module standBaseWall() {
    union() {
        cube([baseWidth, wallHeight, standWallThickness], true);
        translate([0,-wallHeight/2 + supportDepth/2, standWallThickness/2 - 0.01]) standWallSupport(supportWidth);
    }
}

module standSupportWall() {
    union() {
        cube([standWallWidth, standWallHeight, standWallThickness], true);
        translate([0,-standWallHeight/2 + supportDepth/2, standWallThickness/2 - 0.01]) standWallSupport(standWallWidth);
    }
}

nubDepth = alignmentNubDepth;
nubSize = alignmentNubSize;
hollowDepth = nubDepth + alignmentNubMargin*2;
hollowSize = nubSize + alignmentNubMargin*2;
wallSize = hollowSize + wallThickness;
wallDepth = nubDepth + wallThickness;
module alignmentNub() {
    translate([0, nubDepth/2, 0]) cube([nubSize, nubDepth, nubSize], center=true);
}

module alignmentWall() {
    translate([0, wallDepth/2, 0]) cube([wallSize, wallDepth, wallSize], center=true);
}

module alignmentHollow() {
    translate([0, hollowDepth/2, 0]) cube([hollowSize, hollowDepth, hollowSize], center=true);
}

// Show just the outer cylinder and the lining wall
// Useful for positioning
if(previewLiningWall) {
    hollowCylinder();
    translate([0, 0, liningZ]) liningWallModel();
} else {


// Show the model
if(previewModel) { 
    translate([0, 0, liningZ]) scrollModel();
}

// Generate left case, right case, or case stand
rs = [0, 45];
if(side == "l" || side == "ls") {
    difference() {
        union() {
            leftCase();
             // Load Mount Disc
            GenericMountDisc([0, 0, -GenericMountDisc_Thickness()]);
            
            // Alignment nubs
            if(len(alignmentNubs) > 0) {
            for(idx = [0 : len(alignmentNubs) - 1]) {
                p = alignmentNubs[idx];
                r = rs[idx % 2];
                translate([-p[0],0,p[1]]) rotate([0, r, 0]) {
                    alignmentNub();
                }
            }
            }
        }

        // Escape holes
        if(escapeHoles) {
            translate([-escapeOffsetX, -escapeOffsetY, escapeLBottomZ]) escapeHole(true);
            translate([ escapeOffsetX, -escapeOffsetY, escapeLBottomZ]) escapeHole(true);
            translate([-escapeOffsetX, -escapeOffsetY, escapeTopZ]) escapeHole();
            translate([ escapeOffsetX, -escapeOffsetY, escapeTopZ]) escapeHole();
        }

        // Label
        translate([0, GenericMountDisc_Diameter() / 4, escapeLBottomZ - labelDepthExtra]) labelModel();
        
        // Alignment notch
        translate([-1,-GenericMountDisc_Diameter()/2-1,-GenericMountDisc_Thickness()-1]) cube([2,2,2]);
    }
} // side l

else if (side == "r") {
    difference() {
        union() {
            rightCase();
            
            // Alignment walls
            if(len(alignmentNubs) > 0) {
            for(p = alignmentNubs) {
                translate([-p[0],0,p[1]]) {
                    alignmentWall();
                }
            }
            }
        }
        
        // Alignment nubs
        for(idx = [0 : len(alignmentNubs) - 1]) {
            p = alignmentNubs[idx];
            r = rs[idx % 2];
            translate([-p[0],0,p[1]]) rotate([0, r, 0]) scale([1.01, 1.01, 1.01]) {
                alignmentHollow();
            }
        }

        // Escape holes
        if(escapeHoles) {
            translate([-escapeOffsetX, escapeOffsetY, escapeRBottomZ]) escapeHole();
            translate([ escapeOffsetX, escapeOffsetY, escapeRBottomZ]) escapeHole();
            translate([-escapeOffsetX, escapeOffsetY, escapeTopZ]) escapeHole();
            translate([ escapeOffsetX, escapeOffsetY, escapeTopZ]) escapeHole();
        }

        // Label
        translate([0, outerDiameter / 4, escapeRBottomZ - labelDepthExtra]) labelModel();
    }
} // side r

// case stand
if (side == "s" || side == "ls"){
union() {
    difference() {
        // Stand base and walls
        union() {
            translate(baseOffset) standBase();
            translate([0, -baseWidth/2 + standWallHeight/2 - 0.5, baseLengthScale*outerHeight - 1.25*baseWallThickness]) rotate([0,180,0]) standSupportWall();
            translate([0, -baseWidth/2 + wallHeight/2 - 0.5, -GenericMountDisc_Thickness()/2]) standBaseWall();
        }

        cylinder(h=outerHeight+1, d=outerDiameter);
        honeycombCylinder();
        translate([0, 0, -GenericMountDisc_Thickness()-1]) cylinder_outer(h=GenericMountDisc_Thickness()+10, d=GenericMountDisc_Diameter(), fn=128);
        
        // Alignment notch
        translate([-1,-GenericMountDisc_Diameter()/2-2,-GenericMountDisc_Thickness()-1]) cube([2,4,2]);
    
    }
    // Stabilization peg
    translate(pegOffset) standPeg();
}
} // case stand
} // Preview wall lining