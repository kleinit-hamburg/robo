# Umsetzungsstand und nächste Schritte

Das Projekt konzentriert sich auf **eine Feldraupe**. Die aktive Browseransicht nutzt `tracked_overrow_belt08` mit ROS 2 Jazzy, Gazebo Harmonic und einem Webviewer. Maße und Massen stehen in `config/robot-spec.json`; die Physik bleibt in Gazebo. Weitere Kettengeometrien sind nur als Entwicklungs- und Vergleichsdaten vorhanden.

## Repository

```text
config/robot-spec.json          # Geometrie und Massen
models/tracked_overrow_belt08/  # aktives Gazebo-Modell
urdf/                         # Xacro-Beschreibung für spätere CAD-/ROS-Anbindung
scripts/                      # Weltgenerator, Browser-Server, Prüfungen
simulation/                   # Gazebo-Server und ROS-Adapter
web/                          # Bedienung und 3D-Anzeige ohne eigene Physik
tests/                        # Unit- und Integrationsprüfungen
docs/                         # Physik, Einsatzgebiet und Prüfprotokolle
```

## Meilensteine

| Schritt | Ziel | Stand |
|---|---|---|
| M1 | Fahren, Drehen, Anhalten | im Gazebo-Proxy demonstriert; Belastbarkeit des echten Kettenantriebs offen |
| M2 | Gelände und Kartoffelreihe | Kartoffelspur nach Korrektur der starren Pflanzen-/Krümelkollision befahrbar; Feldboden nicht kalibriert |
| M3 | Arm bewegen | im separaten Werkzeugprofil mit bekanntem Ziel demonstriert |
| M4 | 100/250/500/1000 N Werkzeuglast | Prüffälle vorhanden; keine Tragfähigkeitsfreigabe |
| M5 | Pflanze greifen und ziehen | synthetischer Pflanzenzyklus mit bekanntem Ziel demonstriert |
| M6 | vollständige Unkrautstrecke | offen |

Die erste Priorität ist ein belastbares Fahrwerks- und Kontaktmodell: echte Kettenglieder beziehungsweise validierter Kettenkontakt, Laufrollen/Federung, Bodenverformung und nachgewiesene Antriebsleistung. Die aktuelle Feldfahrt trennt Kulturpflanzen als Visualisierung von der kollidierenden Erdgeometrie. Für Pflanzenschutz sind später eigene nachgiebige Pflanzen- und Schadensmodelle nötig. Die Korrektur und ihr A/B-Fahrversuch stehen in [Kartoffelreihe-Kontaktkorrektur](21-kartoffelreihe-kontaktkorrektur.md).

Für Werkzeug und späteren Prototyp bleiben Kraft/Weg-Limits, Standfestigkeit, Motor-/Hydraulikleistung, Energieversorgung, Sensoranordnung und Materialfestigkeit offene Auslegungsaufgaben. Der Browser zeigt nur Gazebo-Zustände. Ein realer Prototyp wird erst nach virtueller Prüfung ausgelegt und beschafft.
