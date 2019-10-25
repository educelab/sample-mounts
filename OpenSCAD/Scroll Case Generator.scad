// Includes
use <Generic Mount Disc.scad>;
use <cylinder_outer.scad>

//// CLI Params ////
scroll = "";
lining = "";
liningWall = "";
side = "l";
liningCavity = "";

previewLiningWall = false;

modelRotate = [0, 0, 0];
modelTranslate = [0, 0, 0];
liningDiameter = 80;
liningHeight = 155;
wallThickness = 2.5;

generateOuterCylinder = true;
honeycomb = true;
honeycombHoleEdges = 6;
honeycombNumCols = 12;
honeycombSpacing = 1.5;

alignmentNubs=[];
alignmentNubDiameter=7.5;

overhangRemoval = false;
overhangStepSize = 0.5;

escapeHoles = false;
escapeOffset = 0;
escapeDiameter = 4;
escapeAngle = 45;

labelLine1 = "GEN CYL";
labelLine2 = "V2";
labelLineHeight = 5;
labelDepth = 0.5;

// Minor Parameters (in mm)
bottomBuffer = 10;
topBuffer = 3;
internalGap = 4;

// Other Minor Parameters
baseLengthScale = 1.0;
$fn = 48;

////////////////////

// Useful Vars
bottomWallThickness = max(2, wallThickness);
liningWallDiameter = liningDiameter + (2 * wallThickness);
liningWallHeight = liningHeight + (2 * wallThickness);
innerDiameter = liningWallDiameter + (2 * internalGap);
innerHeight = bottomBuffer + liningWallHeight + topBuffer;
outerDiameter = innerDiameter + (2 * wallThickness) ;
outerHeight = innerHeight + bottomWallThickness + wallThickness;

outerShellZ = 0;
innerCavityZ = outerShellZ + bottomWallThickness;
liningZ = innerCavityZ + bottomBuffer + wallThickness;
overhangIterations = max(ceil((liningDiameter + wallThickness) * 0.5 / overhangStepSize), 1);

cubeWidth = outerDiameter + 1;
cubeDepth = 0.55 * outerDiameter;
cubeHeight = outerHeight + 1;

escapeDistance = ((((liningDiameter+wallThickness)/2) + ((outerDiameter-wallThickness)/2))/2) + escapeOffset;
escapeOffsetX = cos(escapeAngle) * escapeDistance;
escapeOffsetY = sin(escapeAngle) * escapeDistance;
escapeLBottomZ = -GenericMountDisc_Thickness();
escapeRBottomZ = 0;
escapeTopZ = outerHeight - wallThickness;

// Base
baseLength = GenericMountDisc_Thickness() + outerHeight*baseLengthScale;
baseWidth = max(GenericMountDisc_Diameter(), outerDiameter) + 0.5;
baseThickness = 5;
baseOffset = [-baseWidth/2, -baseWidth/2 - baseThickness - 0.5, -GenericMountDisc_Thickness()];
stripWidth = 30;
pegRadius = GenericMountDisc_NotchDiameter() / 2 - 0.2;
pegOffset = [0, -GenericMountDisc_Diameter()/2 + pegRadius/4, GenericMountDisc_NotchZ() - GenericMountDisc_Thickness()];
wallHeight = baseWidth/2 - GenericMountDisc_Diameter()/4 + 0.5;
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
        completeCase();
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
        completeCase();
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

module standBase() {
     difference() {
        cube([baseWidth, baseThickness, baseLength]);

        // diff out the middle strip
        diffWidth = (baseWidth - stripWidth) / 2 + 1;
        diffXOffset = (baseWidth - stripWidth) / 2;
        diffThickness = baseThickness*2;
        diffHeight = baseLength - (stripWidth * 2);
        translate([diffXOffset + stripWidth, -diffThickness/4, stripWidth]) cube([diffWidth, diffThickness, diffHeight]);
        translate([-1, -diffThickness/4, stripWidth]) cube([diffWidth, diffThickness, diffHeight]);

        // Label
        translate([baseWidth/2, baseThickness + labelDepthExtra, baseLength / 2])
            rotate([90, -90, 0]) labelModel();
    }
}

module standWallSupport() {
    hyp = sqrt(2*(supportDepth*supportDepth));
    translate([0,0,supportDepth/2]) rotate([0,0,90]) difference() {
        cube([supportDepth, supportWidth, supportDepth], true);
        rotate([0,45,0]) translate([0,0,hyp/6]) cube([hyp + 1, supportWidth+1, supportDepth], true);
    }
}

module standWall() {
    union() {
        cube([baseWidth, wallHeight, standWallThickness], true);
        translate([0,-wallHeight/2 + supportDepth/2, standWallThickness/2 - 0.01]) standWallSupport();
    }
}

nubDepth = 3;
nubYScale = nubDepth * 2 / alignmentNubDiameter;
module alignmentNub() {
    difference() {
        scale([1,nubYScale,1]) sphere(d=alignmentNubDiameter);
        translate([0,-alignmentNubDiameter/2,0]) cube(alignmentNubDiameter, center=true);
    }
}

module alignmentPoleWall() {
    wallDiam = alignmentNubDiameter + wallThickness * 2;
    wallYScale = (alignmentNubDiameter * nubYScale + wallThickness * 2) / wallDiam;
    difference() {
        scale([1,wallYScale,1]) sphere(d=wallDiam);
        translate([0,-wallDiam/2,0]) cube(wallDiam, center=true);
    }
}

// Show just the outer cylinder and the lining wall
// Useful for positioning
if(previewLiningWall) {
    hollowCylinder();
    translate([0, 0, liningZ]) liningWallModel();
} else {


// Generate left case, right case, or case stand
if(side == "l" || side == "ls") {
    difference() {
        union() {
            leftCase();
             // Load Mount Disc
            GenericMountDisc([0, 0, -GenericMountDisc_Thickness()]);
            
            // Alignment spheres
            for(p = alignmentNubs) {
                translate([-p[0],0,p[1]]) {
                    alignmentNub();
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
            for(p = alignmentNubs) {
                translate([-p[0],0,p[1]]) {
                    alignmentPoleWall();
                }
            }
        }
        
        // Alignment spheres
        for(p = alignmentNubs) {
            translate([-p[0],0,p[1]]) {
                alignmentNub();
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
            translate([0, -baseWidth/2 + wallHeight/2 - 0.5, baseLengthScale*outerHeight - 1.25*baseThickness]) rotate([0,180,0]) standWall();
            translate([0, -baseWidth/2 + wallHeight/2 - 0.5, -GenericMountDisc_Thickness()/2]) standWall();
        }

        
        cylinder(h=outerHeight+1, d=outerDiameter); 
        translate([0, 0, -GenericMountDisc_Thickness()-1]) cylinder_outer(h=GenericMountDisc_Thickness()+10, d=GenericMountDisc_Diameter(), fn=128);
        
        // Alignment notch
        translate([-1,-GenericMountDisc_Diameter()/2-2,-GenericMountDisc_Thickness()-1]) cube([2,4,2]);
    
    }
    // Stabilization peg
    translate(pegOffset) standPeg();
}
} // case stand
} // Preview wall lining