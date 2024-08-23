# Creating a scroll case

This is a WIP document which roughly describes the method for creating a scroll case.

## Requirements
- OpenSCAD [[link]](https://openscad.org/downloads.html)
  - At the time of this writing, the latest release is 2021.01, which does not run well 
    on Apple Silicon devices. Consider downloading one of the 
    [development snapshots](https://openscad.org/downloads.html#snapshots). 
- MeshMixer 3.5 [[link]](https://web.archive.org/web/20200220222607/http://www.meshmixer.com/download.html)
- MeshLab [[link]](https://www.meshlab.net/#download)

## Steps
- Scale mesh to mm units
- MeshLab
  - Make mesh manifold and watertight
  - Center mesh on origin
  - Orient mesh length along the Z axis, as axis-aligned as possible
  - Set bottom of mesh at Z = 0
- (Optional) Use ACVD to resample mesh to fewer faces
- Save mesh as an STL
- MeshMixer
  - Load model
  - Select all
  - Edit -> Offset... -> 2mm (inner buffer)
  - Edit -> Separate Shells
  - Select inner shell and delete
  - Use Sculpt tool to manually smooth parts of the lining
  - Edit -> Make Solid
  - Copy Lining in Object Browser
  - Select all
  - Edit -> Offset... -> 2mm (wall thickness)
  - Edit -> Separate Shells
  - Select inner shell and delete
  - Export both pieces as STL files
- OpenSCAD
  - Set `lining` path to appropriate STL
  - Set `liningWall` path to appropriate STL
  - Set `scrollHeight` to the height of the scroll in mm (note: usually the Z axis size if oriented as suggested)
  - Set `liningDiameter` to something
  - Set `liningOffset` and `wallThickness` to what was used in MeshMixer
  - Use `modelRotate` and `modelTranslate` to tweak the sample's orientation w.r.t. the case.
    Major adjustments should be applied to the original models in MeshLab.
  - Set the positions of the alignment nubs by setting `alignmentNubs` to an array of coordinate pairs: e.g. `[[-10, 5],[10, 4]]`.
    Each pair corresponds to an absolute position on the XZ plane.
- Set up and run the case generation script
