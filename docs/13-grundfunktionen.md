# Ausbau der Grundfunktionen

Stand 2026-09-07. Umsetzung erfolgt schrittweise; „alle Grundfunktionen“ ist weiterhin das Entwicklungsziel und keine bereits erfüllte Zusage.

## M1: erster vollständiger Fahrnachweis am Radersatzmodell

Mit direktem C++-Gazebo-Server und ROS-Adapter im Simulatorprozess sind **10/10 Fahrdurchläufe samt Sensorfehlerprüfung bestanden**. Größter Streckenfehler 5.15 mm, größter Winkelfehler 2.51°, größter Stop-Nachlauf 2.14 cm. Kriterien blieben unverändert. [Ergebnisse](validation/m1-direct-ros-summary.json), [Quellmanifest](validation/m1-direct-ros-manifest.json). Die Rohdaten und Quellkopien liegen in `results/m1-direct-ros-20260907/`.

Die zunächst alleinige Ablösung des CLI-Starts bestand zwar die Startprüfung, aber nur 8/10 Fahrdurchläufe; zweimal fehlte die Wirkung der Fahrbefehle. [Erhaltene Fehlserie](validation/m1-native-cli-replacement-summary.json). Die vorherigen Fehlversuche aus [M1-Prüfung](10-m1-abnahme.md) bleiben historische Nachweise. Der neue Adapter vermeidet die externe ROS-Gazebo-Bridge für die hier genutzten Befehle und Messdaten; das ist keine nachgewiesene allgemeine Fehlerbehebung in Gazebo.

Freigabe ausschließlich für Bewegung des bestehenden 65-kg-Zweirad-/Stützmodells auf ebenem Boden. Kein echter Kettenantrieb, kein Gangnachweis der Beinkonzepte, keine mechanische Tragfähigkeitsfreigabe. Neue Arm-/Pflanzenprofile sind separat zu prüfen. Die Browserprüfung bestätigt Maus-/Tastaturfahrt, Stopp beim Loslassen/Fokusverlust, Pause, exklusiven Modellwechsel, Desktop/Mobilansicht und den Pflanzenzyklus über die Bedienoberfläche ohne JavaScript-Ausnahmen.

## Anbindung

`simulation/server.cc` startet Gazebo direkt über die installierte Server-API. `simulation/ros_adapter.cc` publiziert Uhr, Gelenkzustände und Darstellungsposen mit 50 Hz direkt als ROS-Nachrichten. Die Orientierung ist eine ausdrücklich ideale synthetische IMU aus der simulierten Körperorientierung; Winkelgeschwindigkeit und Beschleunigung sind als nicht verfügbar markiert. Das ist kein Sensorrausch-, Drift- oder Hardwaremodell. Ground-Truth-Darstellungsposen bleiben auf die Auswertung und Ansicht beschränkt.

Die bisherigen ROS-Befehlsnamen bleiben bestehen. Fahr- und Armkommandos werden innerhalb des Simulatorprozesses an die Gazebo-Controller weitergegeben. Radodometrie wird mit 50 Hz aus den Radgeschwindigkeiten integriert (Radius 0,12 m, Abstand 0,52 m, passend zum bestehenden Ersatzmodell). Sie ist keine schlupffreie Positionsmessung und noch keine validierte Zustandsschätzung. Die gewünschte spätere Spurweite 0,65–0,75 m ist damit noch nicht umgesetzt. Eine spätere reale Plattform ersetzt den Simulatoradapter durch Hardwaretreiber. Native Implementierung und Quellmanifest gehören zum jeweiligen Messstand.

## Neue, getrennte Prüfprofile

- `flat`: unveränderte ebene Fahrprüfung.
- `garden`: bisherige manuelle Gartenansicht.
- `uneven`, `slope`, `slippery`, `obstacle`: synthetische Unebenheiten, 5°-Rampe, μ=0,25 und 20-mm-Schwelle. Keine Marschboden-Kalibrierung und noch keine vollständige M2-Abnahme.
- `manipulation`: sechs bewegliche Armgelenke, zwei Greiferbacken und begrenzte Positionsregler; Gesamtmasse weiterhin 65 kg durch entsprechende Reduktion der Basis-Masse. Ausgangs-, Reich- und Arbeitspose, Öffnen, Schließen und Halten werden per ROS-Gelenktrajektorie angefahren.
- `plant`: zusätzlicher 8-mm-Stängel als starrer Kollisionskörper mit synthetischem Wurzelwiderstand und Fingerkontakt-Sensoren. Implementierung und physikalischer Griffnachweis werden getrennt bewertet.

Armbefehle sind noch keine vollständige M3-Abnahme: kartesische Genauigkeit, Selbstkollision, ros2_control-Integration und allgemeine Planung bleiben offen. Der Lastprüfstand verwendet 100/250/500/1000 N in ±x/±y/±z am definierten Werkzeugpunkt, mit 2 s Vorbereitung, 2 s Rampe, 3 s Halten und 2 s Entlastung. Abbruch bei Arm-/Greifer-Bodenkontakt, fehlenden Messdaten, mehr als 10° Körperneigung oder 0,18 rad/m Gelenkabweichung; eine abgeschlossene Sequenz ist noch keine vollständige M4-Freigabe einschließlich aller Höhen und Stabilitätsreserven. Gemeldete „applied force“ ist die in die Physik eingebrachte externe Kraft, kein gemessener Gelenk-Kraftsensor.

Das Pflanzenmodell ist ein bekannter Zielprüfkörper, noch keine autonome Erkennung. Der starre Prüf-Stängel ist 220 mm lang, 8 mm dick und hat zur numerischen Stabilisierung 0,2 kg Masse. Die vertikale Wurzelkraft steigt bis 25 N bei 60 mm Auslenkung und fällt bis 80 mm auf null ab. Bei 80 mm räumlicher Entfernung vom Anker wird die Wurzel dauerhaft gelöst; seitliche Bewegung kann sie daher ebenfalls lösen. Kraftkomponenten sind auf ±40 N, Rückstellmomente auf ±0,05 Nm begrenzt. Diese bewusst synthetischen Werte sind keine validierte Pflanzenmasse oder Gewebefestigkeit. Seitliche Feder-/Dämpferkräfte halten die unverformte Wurzelzone im vereinfachten Modell. Kein Boden-Einsinken, kein botanischer Kennwert. Ein Griff darf nur aus echten Kontakten beider Backen und einem Halte-/Ausziehversuch bewertet werden, nicht aus dem Schließen des Greifers allein.

## Aufgezeichnete Funktionsprüfungen

- 18 Python-Tests für Bewegung, Bereitschaft, inverse Kinematik und Aufgabenablauf bestanden.
- Automatischer Pflanzenzyklus **5/5 bestanden**, je 24,72–24,82 Simulationssekunden. Fester Zielpunkt, gleiche 25-N-Prüfpflanze, Neustart vor jedem Durchlauf. Beide Fingerkontakte müssen vor dem Ausziehen zwei Sekunden durchgängig vorliegen; nach dem Ausziehen müssen Wurzellösung und Kontakte bestätigt sein. Nach dem Öffnen dürfen keine Fingerkontakte mehr vorliegen. Das ist noch keine M5-Matrix verschiedener Stängel und Reibwerte. [Serie](validation/weed-cycle-series-summary.json), [Quellmanifest](validation/weed-cycle-series-manifest.json).
- Laststufen −z bei niedriger Arbeitspose: 100/250/500/1000 N angefordert, jeweils **Abbruch wegen Bodenkontakt** bei etwa 65/75/85/110 N gemeldeter Spitze. Unterschiedliche Rampengeschwindigkeiten erklären unterschiedliche Abschaltspitzen. **Keine Laststufe hat damit ihre Tragfähigkeit bewiesen.** [Abschaltprüfung](validation/tool-ground-guard-summary.json). Die davor ohne Bodenkontakt-Sperre abgeschlossenen Sequenzen werden nicht als Tragfähigkeitsnachweis verwendet.
- Gelände-Einzelprüfungen: geringe Reibung bestanden (2,26 m Vortrieb); Unebenheiten (0,205 m) und Schwelle (0,533 m) nicht bewältigt. Rampenlauf wegen fehlender Sensorbereitschaft früh abgebrochen, daher kein Rampen-Fahrnachweis. [Laufakte](validation/terrain-summary.json). Der einfache Rad-/Stützersatz taugt damit noch nicht als geländegängiges Kettenmodell. Die nachfolgende native Gazebo-Ursachenanalyse trennt diesen alten Bereitschaftsfehler vom eigentlichen Kontaktproblem des Ersatzfahrwerks: [Ursachenanalyse Kettenroboter](14-gelaende-ursachenanalyse.md).
- Frühere Startzeitüberschreitungen während erstmaliger C++-Kompilierung sind in `results/terrain-20260907/` und `results/weed-cycle-series-20260907/` erhalten. Tests erlauben nun längere Erstkompilierung; parallele Builds werden mit einer Dateisperre serialisiert.

## Reproduzieren

```bash
# ROS-Umgebung und nativer Build werden vom Startskript geladen.
bash scripts/start-browser.sh --world-profile plant
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/check_workbench.py --kind cycle --repeats 5 --output results/neue-pflanzenserie
python3 tests/check_workbench.py --kind loads --output results/neue-lastpruefung
python3 tests/check_terrain.py --output results/neue-gelaendepruefung
```

Ausgabeordner müssen neu sein. Die Prüfer verwenden eigene Ports und ROS-Domains. Für vergleichbare Echtzeitmessungen Prüfungen nacheinander ausführen; Funktionsdauern beziehen sich auf Simulationszeit. CPU-Last durch mehrere Simulatoren und Software-Rendering kann Echtzeit deutlich verlangsamen. Die Browser-Fahrprüfung startet nun reproduzierbar in `flat`. Nach einem fehlerhaften asynchronen Wartevergleich wird die Simulationszeit explizit über die Zustands-API abgefragt. Der Browser-Fahrtest verwendet Simulationszeit für die gehaltenen Fahrdauern; seine Weg- und Stoppgrenzen bleiben unverändert.

Der C++-Adapter benötigt die Entwicklungspakete für Gazebo Sim 8 sowie rclcpp, geometry_msgs, trajectory_msgs, sensor_msgs, rosgraph_msgs, tf2_msgs, std_msgs und nav_msgs aus Jazzy. CMake findet sie nach `source /opt/ros/jazzy/setup.bash`. Basis: [Gazebo Server API](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1Server.html), [Link-Kräfte](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1Link.html), [Gelenktrajektorien](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1JointTrajectoryController.html).

## Weiterhin offen

Gang-/Balanceregler von Quadruped und Humanoid, validierter Ketten-/Federungsaufbau, vollständige M2–M6-Abnahmen, Schneiden/Abstechen, autonome Wahrnehmung/Navigation, Energieversorgung und identische vollständige Unkrautstrecke. Kein Hardwarekauf.

## Abgrenzung zur späteren Hardware

`motion_core.py` und `task_core.py` enthalten die von Gazebo unabhängige Befehls- und Ablaufentscheidung. ROS-Nachrichtentypen bleiben beim Hardwarewechsel bestehen. Armtrajektorien nutzen derzeit den Gazebo-JointTrajectoryController; für ein reales System fehlen ros2_control-Hardwaretreiber, unabhängige Not-Halt-/Watchdog-Ketten und echte Kraft-/Kontaktmessung. Browser und Simulator dürfen diese Funktionen nicht ersetzen. Die feste Pflanzenposition und der JSON-Zustand sind explizite Prüfvorrichtungs-Eingänge; sie werden später durch Wahrnehmung und Sensoradapter ersetzt.

Zeit pro Aufgabe, Weg, Neigung, Kontakte und eingebrachte Werkzeugkraft werden in den JSONL-Laufakten erfasst. Ein elektrischer Energiebedarf wird derzeit **nicht** ausgegeben: Der geschwindigkeitsgeregelte Radersatz liefert keine belastbare Motorleistung, und Batterie-, Wirkungsgrad- und Hydraulikmodelle fehlen. Eine fiktive Energiezahl würde die Konzepte nicht objektiv vergleichbar machen.
