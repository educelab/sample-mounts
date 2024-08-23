# Sample Mounts

These are largely based on OpenSCAD scripts, but there are some operations easier done elsewhere.
One is to fatten a mesh by extruding a face along its normal.
This can be used to create a wall of consistent thickness around an irregularly shaped object, for example.
Simply scaling the object in this case would cause features near the ends to be translated as well as scaled.
The desired effect can be achieved in Blender using the Fatten operation.
This is also (I think, have not tested) available using a Blender Python script with [this function](https://docs.blender.org/api/blender_python_api_2_63_7/bpy.ops.mesh.html#bpy.ops.mesh.extrude_faces_move).

To be used in a Python script, Blender must be installed on the system.
The script must be run in Blender itself, there is no module that can be imported into a normal Python script.
To cheat and run it as if it were a normal script without opening a GUI, these equivalent commands can be used:

    blender --background --python myscript.py
    blender -b -p myscript.py
