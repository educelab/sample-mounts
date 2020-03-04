//Optimal Settings for 3D Printing
$fa = 1;
$fs = 0.4;

//NEEDS MAX WIDTH AND HEIGHT
function overlap() = 0.001;

//Create a base for the model
// ** REMOVE COLOR BEFORE EXPORTING **
color("#808080")
    cube([10,10,1], center=true);

module createLines(baseLength, baseWidth, lineSpacing, lineWidth, lineHeight){
    for(i=[0:3]){
        rotate([0,0,i*90])
        translate([0, baseWidth-lineSpacing, lineHeight-overlap()]);
            cube([baseLength, lineWidth, lineHeight], center=true);
    }   
}

module constructGrid(baseLength, baseWidth){
    if(linePos != [0,0,0]){
        echo("Complete");
    }
    else{
        createLines();
    }
}
