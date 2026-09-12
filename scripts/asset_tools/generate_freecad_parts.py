#!/usr/bin/env python3
"""Generate first parametric CAD reference parts with FreeCAD.

FreeCAD is installed as a confined snap here, so scripts/generate_visual_assets.sh
copies this file into ~/snap/freecad/common before execution. The generated files
are copied back into assets/cad by the shell wrapper.
"""
from pathlib import Path
import FreeCAD as App
import Part

OUT = Path('/home/michael/snap/freecad/common/robo-assets/out')
OUT.mkdir(parents=True, exist_ok=True)

doc = App.newDocument('garden_robot_visual_reference')
body = Part.makeBox(0.72, 0.38, 0.20, App.Vector(-0.36, -0.19, 0.0))
for x in (-0.27, 0.27):
    cyl = Part.makeCylinder(0.055, 0.44, App.Vector(x, -0.22, 0.04), App.Vector(0, 1, 0))
    body = body.fuse(cyl)
shape = doc.addObject('Part::Feature', 'TRK_BASE_001_visual_reference')
shape.Shape = body
step = OUT / 'TRK-BASE-001-visual-reference.step'
stl = OUT / 'TRK-BASE-001-visual-reference.stl'
Part.export([shape], str(step))
shape.Shape.exportStl(str(stl))
print('Generated CAD assets:', step, stl)
