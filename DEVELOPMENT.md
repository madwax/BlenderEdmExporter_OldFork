**BLENDER EDM EXPORTER**
========================

This document outlines helpful stuff for anyone working on the codebase. 

Running the plugin from outside of the Blender plugin dir's
===========================================================

General Running
---------------

If you want to develope the plugin against different versions of blender and have the source code in a central location it's easy.
- On a commandline cd to the root of the source code. e.g. ( c:\devel\github\you\BlenderEdmExporter )
- Then start the version of Blender you want to use via the command line passing "--python devrun.py"
- Blender will open and the plugin will be active and usable.

For example 
for 2.80 - "d:\modeling\blender\blender2.80\blender.exe --python devrun.py"
for 2.82 - "d:\modeling\blender\blender2.82\blender.exe --python devrun.py"

Helpfull Blender CommandLine Argument - Window Position
-------------------------------------------------------

Normaly Blender will open in fullscreen mode which can be a pain.  If you want to set blenders position on screen then use "-p x y width height".  One thing to note is the origin of x and y is the bottom left of your main screen and NOT top left (don't ask)
You might need to experiment with your setup as multidisplays can be intresting.

For example 
"d:\modeling\blender\blender2.80\blender.exe -p 0 0 800 600 --python devrun.py"


Helpfull Blender CommandLine Argument - Background
--------------------------------------------------

If you just want to test if your Python code works or have automanted tests then passing --background is very useful. This will start blender but not create the UI, execute your script and exit.  While this is not that useful with the devrun.py script any future automanted tests will love this.

















