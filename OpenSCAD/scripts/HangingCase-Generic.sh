#!/bin/bash

### IMPORTANT ###
# This must be set to the absolute path of the 3d-utilities directory
#################
UTILS_DIR="/Users/seth/source/3d-utilities"

outputPrefix="CBL-PMA5"
version=1

for part in l r cl cr cap clip; do
  echo $(date) ":: Rendering part ${part}..."
  openscad \
      -o "${outputPrefix}-v${version}-${part}.stl" \
      -D "part=\"${part}\"" \
      "${UTILS_DIR}/OpenSCAD/Hanging Frame Case.scad"
done

echo $(date) ":: Rendering complete."
