use <cylinder_outer.scad>

// fr 1: 28 x 38 mm
// fr 2: 26 x 40 mm

objW = 28;
objH = 38;
objD = 3;
objBuffer = 3;
theta = 45;

wallThickness = 1;

bufferedW = objW + objBuffer;
bufferedH = objH + objBuffer;
bufferedD = objD + objBuffer;

projW = bufferedW;
projL1 = bufferedH * cos(theta);
projL2 = bufferedD * cos(90 - theta);
projH1 = bufferedH * sin(theta);
projH2 = bufferedD * sin(90 - theta);
projH = max(bufferedD, projL1 + projL2);

pts = [
        [0, -projL2, projH2], 
        [projW, -projL2, projH2],
        [projW, -projL2, projH1],
        [projW, projL1, projH1],
        [0, projL1, projH1],
        [0, -projL2, projH1]
      ];
      
faces = [
        [0, 1, 2, 5],
        [5, 2, 3, 4],
        [4, 3, 1, 0],
        [0, 5, 4],
        [1, 3, 2]
      ];

cylH = max(bufferedD, projH1);
cylD = sqrt(projW * projW + projH * projH) + 2 * wallThickness;


module trayCavity() {
    translate([-projW/2, -projL1/2 + projL2/2, wallThickness]) { 
        rotate([theta,0,0]) cube([bufferedW,bufferedH,bufferedD]);
        polyhedron(points = pts, faces = faces);
    }
}


difference() {
  cylinder_outer(h=cylH, d=cylD);
  trayCavity();
}

// translate([-4.75,-3.5,-2]) rotate([26,0,0]) cube([9.5,10.,.1]);


echo(cylD);