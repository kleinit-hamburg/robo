# FreeCAD-/Blender-Visual-Pipeline

Stand 2026-09-12. FreeCAD und Blender sind als lokale Modellierungswerkzeuge in das Repository eingebunden. Die Pipeline erzeugt Visual-Assets fuer eine bessere Browser- und Gazebo-Ansicht, ohne die physikalische Wahrheit zu verschieben.

## Werkzeuge

- Blender 4.0.2 erzeugt GLB-Visuals fuer Damm, Kartoffelkraut und Unkraut.
- FreeCAD 1.1.1 erzeugt parametrische CAD-Referenzen als STEP/STL.
- FreeCAD-GUI ist auf dieser Maschine wegen Display/Qt nicht nutzbar; `freecad.cmd` funktioniert im Skriptmodus.

## Ausfuehrung

```bash
./scripts/generate_visual_assets.sh
```

Das Skript erzeugt:

- `assets/visual/potato_ridge_340cm.glb`
- `assets/visual/potato_haulm.glb`
- `assets/visual/weed_broadleaf.glb`
- `assets/cad/TRK-BASE-001-visual-reference.step`
- `assets/cad/TRK-BASE-001-visual-reference.stl`

Der FreeCAD-Snap kann Skripte unter `/opt/...` nicht direkt ausfuehren. Der Wrapper kopiert deshalb das FreeCAD-Skript nach `~/snap/freecad/common/robo-assets/` und kopiert die erzeugten CAD-Dateien danach ins Repository.

## Einbindung in die Simulation

Das Profil `potato_ridge` referenziert die GLB-Dateien als SDF-Visual-Meshes. Die Collision-Geometrien bleiben einfache Zylinder, Boxen und Kugeln. Dadurch sind die sichtbaren Modelle deutlich besser, aber Gazebo rechnet weiterhin mit kontrollierten Proxy-Kontakten.

Der Browser laedt Meshes ueber Three.js `GLTFLoader`. `file://.../assets/...`-URIs aus der SDF werden serverseitig nicht direkt im Browser verwendet, sondern im Frontend auf `/assets/...` abgebildet.

## Grenzen

Diese Assets sind keine fertige CAD-Konstruktion und kein elastisches Pflanzenmodell. Sie verbessern die Sichtpruefung und Kommunikation. Fuer Messer, Greifer, rotierende Zieher und nachgiebiges Kartoffelkraut brauchen wir als naechstes separate Werkzeug- und Pflanzen-Kraftmodelle.
