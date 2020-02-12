//All units are in millimeters

//Optimal settings
$fa = 1;
$fs = 0.4;

//Global constants
function separation() = 0.75;
function baseWidth() = 50;
function baseLength() = 50;
function baseHeight() = 2;

rotate([0, 0, 90])
    translate([0,-50,0])
        cube([100, 50, 1]);
translate([0,0,1-0.1])    
    pattern();

module pattern(){
    cube([baseWidth(), baseLength(), baseHeight()]);

    translate([0,baseWidth()+separation(),0])
        cube([baseWidth()/2-separation()/2, baseLength()/2, baseHeight()]);
    translate([baseLength()/2+separation()/2,baseWidth()+separation(),0])
        cube([baseWidth()/2-separation()/2, baseLength()/2, baseHeight()]);
        
    translate([0,baseWidth()+separation(),0])
        cube([baseWidth()/2-separation()/2, baseLength()/2, baseHeight()]);
    translate([baseLength()/2+separation()/2,baseWidth()+separation(),0])
        cube([baseWidth()/2-separation()/2, baseLength()/2, baseHeight()]);
        
    translate([0,baseWidth()+ baseWidth()/2 + separation()*2,0])
        cube([baseWidth()/4-separation()/4, baseLength()/4, baseHeight()]);
    translate([baseLength()/4+separation()/4,baseWidth()+baseWidth()/2+separation()*2,0])
        cube([baseWidth()/4-separation()/4, baseLength()/4, baseHeight()]);
    translate([2*baseLength()/4+separation()/4,baseWidth()+ baseWidth()/2 + separation()*2,0])
        cube([baseWidth()/4-separation()/4, baseLength()/4, baseHeight()]);
    translate([3*baseLength()/4+separation()/4,baseWidth()+baseWidth()/2+separation()*2,0])
        cube([baseWidth()/4-separation()/4, baseLength()/4, baseHeight()]);
        
    translate([0,baseWidth()+ baseWidth()/2+ baseWidth()/4 + separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([2*baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([3*baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([4*baseLength()/8+separation()/8,baseWidth()+ baseWidth()/2+ baseWidth()/4 + separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([5*baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([6*baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
    translate([7*baseLength()/8+separation()/8,baseWidth()+baseWidth()/2+baseWidth()/4+separation()*3,0])
        cube([baseWidth()/8-separation()/8, baseLength()/8, baseHeight()]);
       
       
    translate([0,baseWidth()+ baseWidth()/2+ baseWidth()/4 + baseWidth()/8 + separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([2*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([3*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([4*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([5*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([6*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([7*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([8*baseLength()/16+separation()/16,baseWidth()+ baseWidth()/2+ baseWidth()/4 + baseWidth()/8 + separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([9*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([10*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([11*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([12*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([13*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([14*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
    translate([15*baseLength()/16+separation()/16,baseWidth()+baseWidth()/2+baseWidth()/4+baseWidth()/8+separation()*4,0])
        cube([baseWidth()/16-separation()/16, baseLength()/16, baseHeight()]);
}