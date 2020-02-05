//Optimal settings
$fa = 1;
$fs = 0.4;

function overlapForPrinting() = 0.001;

//Height and Width functions to choose from
function inverseHeight(maxHeight, step) = maxHeight/step;
function inverseWidth(maxWidth, step) = maxWidth/step;
function logisticHeight(maxHeight, step) = maxHeight * (1/(3+exp(step/3)));
function logisticWidth(maxWidth, step) = maxWidth * (1/(3+exp(step/3))); 

//Assigning the equations used to determine height and width
function height(maxHeight, step) = logisticHeight(maxHeight, step);
function width(maxWidth, step) = logisticWidth(maxWidth, step); 
function addHeight(currHeight, addHeight) = currHeight+addHeight;

//Creating a cylinder step
module eachStep(maxStepsHeight, maxStepsWidth, currStepsHeight, stepNum){
        newHeight = height(maxHeight=maxStepsHeight, step=stepNum);
        newWidth = width(maxWidth=maxStepsWidth, step=stepNum);
        translate([0,0, currStepsHeight-overlapForPrinting()])
            cylinder(h=newHeight, r=newWidth);
}

//Recursively stacking the steps
module stackSteps(maxHeight, maxWidth, currHeight, currStep = 1){
    nextStep = height(maxHeight, currStep);
    if (currHeight+nextStep >= maxHeight) {
        echo("Complete");
    }
    else {
        eachStep(maxStepsHeight=maxHeight, maxStepsWidth=maxWidth, currStepsHeight=currHeight, stepNum=currStep);
        newCurrHeight = addHeight(currHeight=currHeight, addHeight=nextStep);
        newCurrStep = currStep + 1;
        stackSteps(maxHeight=maxHeight, maxWidth=maxWidth, currHeight=newCurrHeight, currStep = newCurrStep);
    }     
}

//Creating a cylinder stair step pattern
stackSteps(maxHeight=10, maxWidth=100, currHeight=0);