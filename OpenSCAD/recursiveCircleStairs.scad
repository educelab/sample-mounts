//Optimal settings
$fa = 1;
$fs = 0.4;

function overlapForPrinting() = 0.001;

function height(maxHeight, divisor) = maxHeight * (1/divisor);
function addHeight(currHeight, addHeight) = currHeight+addHeight;
function width(maxWidth, divisor) = maxWidth * (1/divisor); 

//Creating a cylinder step
module eachStep(maxStepsHeight, maxStepsWidth, currStepsHeight, stepNum){
        newHeight = height(maxHeight=maxStepsHeight, divisor=stepNum);
        newWidth = width(maxWidth=maxStepsWidth, divisor=stepNum);
        translate([0,0, currStepsHeight-overlapForPrinting()])
            cylinder(h=newHeight, r=newWidth);
}

//Recursively stacking the steps
module stackSteps(maxHeight, maxWidth, currHeight, currStep = 1, maxStep){
    if (currStep == maxStep) {
        echo("Complete");
    }
    else {
        eachStep(maxStepsHeight=maxHeight, maxStepsWidth=maxWidth, currStepsHeight=currHeight, stepNum=currStep);
        newCurrHeight = addHeight(currHeight=currHeight, addHeight=height(maxHeight, currStep));
        newCurrStep = currStep + 1;
        stackSteps(maxHeight=maxHeight, maxWidth=maxWidth, currHeight=newCurrHeight, currStep = newCurrStep, maxStep = maxStep);
    }     
}

//Creating a cylinder stair step pattern
stackSteps(maxHeight=20, maxWidth=20, currHeight=0, maxStep=15);