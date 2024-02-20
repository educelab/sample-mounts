#!/bin/bash

### IMPORTANT ###
# This must be set to the absolute path of the educelab/sample-mounts clone directory
#################
UTILS_DIR="/Users/seth/source/sample-mounts"

outputPrefix="Generic Scroll Case"
version=3

liningPath=""
liningWallPath=""

previewLiningWall=false
previewModel=false

modelRotate='[0,0,0]'
modelTranslate='[0,0,0]'
liningDiameter=80
liningHeight=155
wallThickness=2

generateOuterCylinder=false
honeycomb=true;
honeycombHoleEdges=6
honeycombNumCols=12
honeycombSpacing=1.5

alignmentNubs='[]'
alignmentNubSize=3
alignmentNubDepth=1.5
alignmentNubMargin=0.5

overhangRemoval=false
overhangStepSize=0.5

escapeHoles=true
escapeOffset=0
escapeDiameter=4
escapeAngle=45

labelLine1="GEN CYL"
labelLine2="V${version}"
labelLineHeight=5

bottomBuffer=10;
topBuffer=3;
internalGap=4;

(echo $(date) ":: Rendering left side..."
openscad \
    -o "${outputPrefix}-v${version}-L.stl" \
    -D "side=\"l\"" \
    -D "lining=\"${liningPath}\"" \
    -D "liningWall=\"${liningWallPath}\"" \
    -D "previewLiningWall=${previewLiningWall}" \
    -D "previewModel=${previewModel}" \
    -D "modelRotate=${modelRotate}" \
    -D "modelTranslate=${modelTranslate}" \
    -D liningDiameter=${liningDiameter} \
    -D liningHeight=${liningHeight} \
    -D wallThickness=${wallThickness} \
    -D generateOuterCylinder=${generateOuterCylinder} \
    -D overhangRemoval=${overhangRemoval} \
    -D overhangStepSize=${overhangStepSize} \
    -D escapeHoles=${escapeHoles} \
    -D escapeOffset=${escapeOffset} \
    -D escapeDiameter=${escapeDiameter} \
    -D escapeAngle=${escapeAngle} \
    -D "labelLine1=\"${labelLine1}\"" \
    -D "labelLine2=\"${labelLine2}\"" \
    -D labelLineHeight=${labelLineHeight} \
    -D bottomBuffer=${bottomBuffer} \
    -D topBuffer=${topBuffer} \
    -D internalGap=${internalGap} \
    -D honeycomb=${honeycomb} \
    -D honeycombHoleEdges=${honeycombHoleEdges} \
    -D honeycombNumCols=${honeycombNumCols} \
    -D honeycombSpacing=${honeycombSpacing} \
    -D "alignmentNubs=${alignmentNubs}" \
    -D alignmentNubSize=${alignmentNubSize} \
    -D alignmentNubDepth=${alignmentNubDepth} \
    -D alignmentNubMargin=${alignmentNubMargin} \
    "${UTILS_DIR}/OpenSCAD/Scroll Case Generator.scad" && \
echo $(date) ":: Left side rendered."
echo) &

(echo $(date) ":: Rendering right side..."
openscad \
    -o "${outputPrefix}-v${version}-R.stl" \
    -D "side=\"r\"" \
    -D "lining=\"${liningPath}\"" \
    -D "liningWall=\"${liningWallPath}\"" \
    -D "previewLiningWall=${previewLiningWall}" \
    -D "previewModel=${previewModel}" \
    -D "modelRotate=${modelRotate}" \
    -D "modelTranslate=${modelTranslate}" \
    -D liningDiameter=${liningDiameter} \
    -D liningHeight=${liningHeight} \
    -D wallThickness=${wallThickness} \
    -D generateOuterCylinder=${generateOuterCylinder} \
    -D overhangRemoval=${overhangRemoval} \
    -D overhangStepSize=${overhangStepSize} \
    -D escapeHoles=${escapeHoles} \
    -D escapeOffset=${escapeOffset} \
    -D escapeDiameter=${escapeDiameter} \
    -D escapeAngle=${escapeAngle} \
    -D "labelLine1=\"${labelLine1}\"" \
    -D "labelLine2=\"${labelLine2}\"" \
    -D labelLineHeight=${labelLineHeight} \
    -D bottomBuffer=${bottomBuffer} \
    -D topBuffer=${topBuffer} \
    -D internalGap=${internalGap} \
    -D honeycomb=${honeycomb} \
    -D honeycombHoleEdges=${honeycombHoleEdges} \
    -D honeycombNumCols=${honeycombNumCols} \
    -D honeycombSpacing=${honeycombSpacing} \
    -D "alignmentNubs=${alignmentNubs}" \
    -D alignmentNubSize=${alignmentNubSize} \
    -D alignmentNubDepth=${alignmentNubDepth} \
    -D alignmentNubMargin=${alignmentNubMargin} \
    "${UTILS_DIR}/OpenSCAD/Scroll Case Generator.scad" && \
echo $(date) ":: Right side rendered."
echo) &

(echo $(date) ":: Rendering stand..."
openscad \
    -o "${outputPrefix}-v${version}-Stand.stl" \
    -D "side=\"s\"" \
    -D "lining=\"${liningPath}\"" \
    -D "liningWall=\"${liningWallPath}\"" \
    -D "previewLiningWall=${previewLiningWall}" \
    -D "previewModel=${previewModel}" \
    -D "modelRotate=${modelRotate}" \
    -D "modelTranslate=${modelTranslate}" \
    -D liningDiameter=${liningDiameter} \
    -D liningHeight=${liningHeight} \
    -D wallThickness=${wallThickness} \
    -D generateOuterCylinder=${generateOuterCylinder} \
    -D overhangRemoval=${overhangRemoval} \
    -D overhangStepSize=${overhangStepSize} \
    -D escapeHoles=${escapeHoles} \
    -D escapeOffset=${escapeOffset} \
    -D escapeDiameter=${escapeDiameter} \
    -D escapeAngle=${escapeAngle} \
    -D "labelLine1=\"${labelLine1}\"" \
    -D "labelLine2=\"${labelLine2}\"" \
    -D labelLineHeight=${labelLineHeight} \
    -D bottomBuffer=${bottomBuffer} \
    -D topBuffer=${topBuffer} \
    -D internalGap=${internalGap} \
    -D honeycomb=${honeycomb} \
    -D honeycombHoleEdges=${honeycombHoleEdges} \
    -D honeycombNumCols=${honeycombNumCols} \
    -D honeycombSpacing=${honeycombSpacing} \
    -D "alignmentNubs=${alignmentNubs}" \
    -D alignmentNubSize=${alignmentNubSize} \
    -D alignmentNubDepth=${alignmentNubDepth} \
    -D alignmentNubMargin=${alignmentNubMargin} \
    "${UTILS_DIR}/OpenSCAD/Scroll Case Generator.scad" && \
echo $(date) ":: Stand rendered."
echo)
