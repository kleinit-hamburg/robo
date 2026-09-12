# FreeCAD-/Blender-Visual-Pipeline

Stand 2026-09-12. FreeCAD und Blender sind als lokale Modellierungswerkzeuge in das Repository eingebunden. Die Pipeline erzeugt Visual-Assets fuer eine bessere Browser- und Gazebo-Ansicht, ohne die physikalische Wahrheit zu verschieben.

## Werkzeuge

- Blender 4.0.2 erzeugt GLB-Visuals fuer Bodenoberflaeche mit Krume/Furchen, Kartoffeldamm, mehrere Kartoffelkraut-Varianten, Unkraut und eine erste Kettenroboter-Visualhuelle.
- FreeCAD 1.1.1 erzeugt parametrische CAD-Referenzen als STEP/STL.
- FreeCAD-GUI ist auf dieser Maschine wegen Display/Qt nicht nutzbar; `freecad.cmd` funktioniert im Skriptmodus.

## Ausfuehrung

```bash
./scripts/generate_visual_assets.sh
```

Das Skript erzeugt:

- `assets/visual/soil_patch_6x4.glb`
- `assets/visual/potato_ridge_340cm.glb`
- `assets/visual/potato_haulm.glb`
- `assets/visual/potato_haulm_b.glb`
- `assets/visual/potato_haulm_c.glb`
- `assets/visual/weed_broadleaf.glb`
- `assets/visual/tracked_robot_shell.glb`
- `assets/cad/TRK-BASE-001-visual-reference.step`
- `assets/cad/TRK-BASE-001-visual-reference.stl`

Der FreeCAD-Snap kann Skripte unter `/opt/...` nicht direkt ausfuehren. Der Wrapper kopiert deshalb das FreeCAD-Skript nach `~/snap/freecad/common/robo-assets/` und kopiert die erzeugten CAD-Dateien danach ins Repository.

## Einbindung in die Simulation

Das Profil `potato_ridge` referenziert die GLB-Dateien als SDF-Visual-Meshes. Die Collision-Geometrien bleiben einfache Zylinder, Boxen und Kugeln. Dadurch werden Boden, Dämme und Pflanzen sichtbarer, aber Gazebo rechnet weiterhin mit kontrollierten Proxy-Kontakten.

Der Browser laedt Meshes ueber Three.js `GLTFLoader`. `file://.../assets/...`-URIs aus der SDF werden im Frontend auf `/assets/...` abgebildet. Fuer das Kartoffeldammprofil wird der Roboter zusaetzlich mit einer visuellen Shell dargestellt; die einfache Kollisions- und Gelenkstruktur bleibt unveraendert.

## Grenzen

Diese Assets sind noch keine fertige CAD-Konstruktion und kein elastisches Pflanzenmodell. Sie verbessern Sichtpruefung und Kommunikation. Fuer Messer, Greifer, rotierende Zieher und nachgiebiges Kartoffelkraut brauchen wir als naechstes separate Werkzeug- und Pflanzen-Kraftmodelle.
