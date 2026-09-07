# Austauschbare Roboter und Bewegungsbefehle

Stand 2026-09-07: Die Browseransicht startet mit dem Kettenkonzept und bietet drei einzeln auswählbare Modelle. Bei jedem Wechsel wird dieselbe Testwelt neu geladen und genau ein Modell namens `robot` eingesetzt. Es bleiben keine alten Roboter zurück. Fallwürfel und Rollkugel sind nicht mehr Teil der Startansicht.

## Bedienung

| Befehl | Browser | Tastatur | Verhalten |
|---|---|---|---|
| Vorwärts / später vorwärts gehen | Vorwärts gedrückt halten | ↑ / W halten | 0,15 m/s in Körper-x-Richtung |
| Rückwärts | Rückwärts gedrückt halten | ↓ / S halten | −0,15 m/s |
| Links drehen | Links drehen gedrückt halten | ← / A halten | positive Giergeschwindigkeit, 0,5 rad/s |
| Rechts drehen | Rechts drehen gedrückt halten | → / D halten | negative Giergeschwindigkeit, −0,5 rad/s |
| Umdrehen | Umdrehen einmal anklicken | U | etwa 180° nach links, anschließend anhalten |
| Anhalten | rote Schaltfläche | Leertaste | Fahrt/Drehung abbrechen; Simulation läuft weiter |
| Simulation pausieren | eigene Schaltfläche | — | gesamte Physik pausieren, Bewegung wird abgebrochen |
| Zur Startposition | eigene Schaltfläche | — | Testwelt mit demselben Roboter neu laden |

Links/rechts bedeutet Drehen, kein seitliches Versetzen. Bei Pfeiltasten/WASD sowie den Richtungsschaltflächen stoppt die Bewegung beim Loslassen. Umdrehen ist ein begrenzter Einzelauftrag; Leertaste oder Anhalten bricht ihn ab. Beim Verlassen des Browserfensters oder Verbergen des Tabs wird ein Stopp gesendet. Zusätzlich stoppt der Regler nach spätestens 0,65 s ohne Bedien-Heartbeat, zuzüglich Reglerzyklus und physikalischer Bremszeit. Die Simulation setzt die Geschwindigkeit nicht per Teleportation auf null.

Bei mehreren Browserfenstern gilt der zuletzt akzeptierte Fahrbefehl. Heartbeats dürfen nur dessen Besitzer verlängern. Szenenrevision und fortlaufende Client-Sequenz verhindern, dass verspätete Befehle nach einem Roboterwechsel oder Stopp wieder Fahrt auslösen.

## Tatsächlicher Entwicklungsstand

| Konzept | Jetzt möglich | Noch offen |
|---|---|---|
| Kette mit Manipulator | Physikalisches Fahren, Drehen und Anhalten auf der Ebene; IMU-geführtes Umdrehen | echtes Kettenkontakt-/Antriebsmodell, beweglicher Arm, Greifen, Kraftregelung |
| Quadruped mit Manipulator | Einwechseln und Betrachten des groben Modells | Gelenkmodell, Gang-, Stand- und Balanceregler, Armregelung |
| Humanoid mit zwei Händen | Einwechseln und Betrachten des groben Modells | Gelenkmodell, Gang-/Balanceregelung und Hand-/Armregelung |

Die beiden Beinkonzepte sind ausdrücklich **statische Geometrievorschauen**. Sie sind nicht frei balanciert und ihre Bewegungskommandos werden auch serverseitig abgelehnt. Für sie werden keine versteckten Räder oder über den Boden geschobenen Körper als funktionierendes Gehen ausgegeben. Ihre spätere Implementierung erhält dieselben semantischen Befehle, aber eigene Gangregler.

Das Kettenkonzept ist aktuell ein **Zweirad-Differentialantrieb mit vier passiven Kontaktstützen**, um die gemeinsame Bedienung und Anfahrt zu entwickeln. Sichtbare Kettenbänder und Manipulator sind starre Visuals. Es gibt noch keine physikalische Kette und keine Arm-/Greifergelenke. Die Stützen sind reibungsarme Kugelkontakte, keine detaillierten Lenkrollen. Die Gesamtmasse beträgt 65 kg (60,6 kg Basis, 2 × 2 kg Antriebsräder, 4 × 0,1 kg Stützen). Basis-Trägheit und Schwerpunkt sind grobe Annahmen.

`DiffDrive` regelt Radgeschwindigkeit; eingetragene Gelenk-Effortgrenzen allein machen daraus keinen validierten drehmomentbegrenzten Antrieb. Skid-Steering, Bodenarbeit, Tool-Stabilität und elektrische Energie dürfen daraus noch nicht verglichen werden. Damit bleibt die Freigabesperre aus dem Physikdokument bestehen. Arm-/Handvisuals sind noch keine vollständigen Kollisionsmodelle. Die derzeitige Demo ist keine autonome Hindernis- oder Nutzpflanzenvermeidung.

## Schnittstellen und Wiederverwendung

- `scripts/motion_core.py`: reine, ROS-/Gazebo-unabhängige Befehlslogik; Eingänge sind Befehl, monotone Zeit und gemessene Orientierung.
- Browser → HTTP-Auftrag → `garden_browser_teleop` → `/garden/cmd_vel` (`geometry_msgs/Twist`) → ROS-Gazebo-Bridge → Gazebo-Differentialantrieb.
- `/garden/imu` (`sensor_msgs/Imu`, 50 Hz): Orientierung für die Drehregelung. Die erste Prüfung verwendet eine ideale simulierte IMU ohne Rauschen; reale Drift und Kalibrierung sind später zu berücksichtigen.
- Gazebo `/world/garden_preview/clock` → ROS `/clock`: eindeutig zugeordnete Simulationsuhr, auch nach Weltwechsel.
- `/garden/odom` (`nav_msgs/Odometry`, 30 Hz): Radodometrie als Grundlage für spätere Zustandsschätzung. Reine Radodometrie wich beim Drehversuch deutlich von der tatsächlichen Körperausrichtung ab; deshalb wurde die IMU-Rückführung ergänzt.
- Model-/Linkposen aus `/model/robot/pose` dienen ausschließlich der Ansicht und der unabhängigen Testauswertung. Die Drehregelung liest keine Gazebo-Ground-Truth-Posen.
- Gemeinsame Fahrbefehle werden mit 20 Hz publiziert. IMU-Zeitstempel werden gegen die Simulationsuhr geprüft; alte, unplausibel zukünftige oder ungültige Orientierungen werden verworfen. Beim Fehlen frischer Orientierung für mehr als 0,5 s wird angehalten. Umdrehen hat zusätzlich 20 s Zeitlimit.

Eine spätere reale Basis ersetzt den Gazebo-Adapter durch ros2_control/Motortreiber und einen unabhängigen Geräte-Watchdog. Die Befehlslogik und ROS-Typen bleiben verwendbar. Für Quadruped/Humanoid wird `/garden/cmd_vel` als gewünschte Körperbewegung an den jeweiligen Gangregler übergeben, nicht direkt an einzelne Gelenke. Diese Adapter und autonomen Nodes sind noch nicht implementiert.

## Dateien und Prüfungen

- `config/preview-concepts.json`: Auswahl und ausdrücklich freigegebene Fähigkeiten.
- `models/{tracked,quadruped,humanoid}/model.sdf`: grobe Robotermodelle.
- `scripts/build_preview_models.py`: reproduzierbare Erzeugung dieser Primitive.
- `scripts/browser_server.py`, `web/`: Auswahl, Live-Darstellung und Teleoperation.
- `tests/test_motion_core.py`: acht Unit-Tests für Befehls-/Sensorausfall, Winkelüberlauf, Drehzeitlimit, Stop-Abbruch und ROS-Zahlentypen.
- `tests/accept_m1_tracked.py`: zehn aufgezeichnete M1-Läufe in einer eigenen ebenen Welt, einschließlich Verbindungs- und Sensorausfall.
- `tests/check_live_drive.py`: manuell gestarteter Integrationstest gegen laufende Demo; setzt die Szene zurück.
- `tests/check_browser.cjs`: Playwright-Test für Maus/Tastatur, Roboterwechsel, Fokusverlust, Pause und Mobilansicht. Benötigt separat Playwright und Chromium.

Bestanden: alle drei SDF-Prüfungen, acht Unit-Tests und Fahrtest gegen echte Gazebo-Positionen. Vorwärtsfahrt ergab etwa 0,384 m, Rückwärtsfahrt endete etwa 0,002 m vor dem Ausgangspunkt. IMU-geführtes Umdrehen erreichte im Test 3,123 rad (ca. 178,9°). Ausbleibende Heartbeats führten zum Stopp; der danach geprüfte Restweg blieb unter 3 cm. Das sind einzelne Funktionsprüfungen auf ebener Fläche, keine statistischen Benchmark-Ergebnisse.

Der Chromium-Browsertest bestätigte echte Bewegung beim Halten von Schaltflächen/Tasten, Stopp beim Loslassen und Fokusverlust, genau ein gewähltes Modell, gesperrte Bewegung bei fehlendem Gangregler sowie gesperrte Fahrt während Simulationspause. Desktop/Mobilansicht ohne JavaScript-Ausnahmen geprüft, alle drei Roboterdarstellungen visuell geprüft.

```bash
python3 -m unittest discover -s tests -v
# Eigene Testinstanz: localhost:8089, ROS-Domain 175, ebener Boden.
# Ausgabeordner muss neu sein; die laufende Browseransicht bleibt getrennt.
source /opt/ros/jazzy/setup.bash
python3 tests/accept_m1_tracked.py --runs 10 --output results/m1-neuer-lauf
python3 tests/check_live_drive.py --url http://10.10.10.50:8088
# Browser-Test mit bereits separat installiertem Playwright/Chromium:
NODE_PATH=/tmp/garden-browser-test/node_modules \
  CHROMIUM_EXECUTABLE=/home/michael/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome \
  VIEWER_URL=http://10.10.10.50:8088 node tests/check_browser.cjs
```

Quelle für den Antriebsadapter: [Gazebo Harmonic DiffDrive](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1DiffDrive.html).

Die spätere aufgezeichnete M1-Serienprüfung blieb wegen unzuverlässiger Weltstarts offen. Einzelner Fahrtest und korrigierte Sensorfehlerinjektion bestanden; abschließender Browserstart nicht bereit. Maßgeblich für die Freigabe ist der [M1-Prüfbericht](10-m1-abnahme.md), nicht die früheren einzelnen Funktionsprüfungen.

## Fahrbereitschaft und Startdiagnose

Der aktuelle Backendstand meldet `control_ready` getrennt von `connected` und der grundsätzlichen Modellfähigkeit `drive_ready`. Ein neuer Fahrbefehl benötigt laufende Simulator-/Bridge-Prozesse, eine höchstens 3 s alte Uhr, eine höchstens 0,5 s alte gültige Orientierung und vollständige, endliche Radgelenkdaten mit höchstens 1 s Alter. Weltwechsel, Pause und fehlende Gangregler sperren die Freigabe ebenfalls. Stop bleibt ohne diese Messvoraussetzungen möglich. Diese Prüfung ergänzt die vorhandenen Bewegungs-Watchdogs; sie ist keine neue Freigabe eines realen Sicherheitscontrollers.

`/api/state` enthält dazu `readiness_issues`, `clock_age_s`, `imu_age_s`, `joint_age_s` und `process_exit_codes`. Der Browser nennt fehlende oder veraltete Daten ausdrücklich. Die bisher laufende ältere Backendinstanz bleibt bis zum Neustart mit der neuen Webseite kompatibel; dort gelten noch die bisherigen Freigaberegeln. Elf Unit-Tests prüfen jetzt auch unvollständige Bereitschaft, abgelaufene Daten und die Prozess-/Pausensperren. Native Gazebo-Start-/Abbauprobleme bleiben offen.

Ein isolierter Gazebo-Fahrdurchlauf mit diesem Backendstand sowie die korrigierte Sensorfehlerinjektion bestanden am 2026-09-07: [Ergebnis](validation/m1-readiness-summary.json), [Quellmanifest](validation/m1-readiness-manifest.json). Dies ersetzt nicht die weiterhin offene Zehner-Abnahme. Die Browseränderung wurde auf JavaScript-Syntax geprüft; eine erneute vollständige Browserabnahme ist damit nicht behauptet.
