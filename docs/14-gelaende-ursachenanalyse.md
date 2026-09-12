# Ursachenanalyse Kettenroboter auf Steigung und Unebenheiten

Stand 2026-09-12. Diese Analyse prueft nur das vorhandene Gazebo-Physikmodell des Kettenkonzepts. Es wurden keine Fahrparameter, Massen, Reibwerte, Gelenklimits oder Controllerwerte geaendert, damit der Fehler nicht durch Tuning verdeckt wird. Die Browseransicht ist dabei nur Anzeige; Mess- und Kontaktwerte kommen direkt aus Gazebo Harmonic/DART.

## Ergebnis

Der alte 5-Grad-Fehler aus der Browser-Gelaendepruefung war kein belastbarer Nachweis fuer eine mechanische Rampenschwaeche: der Test brach nach rund 0,28 s Simulationszeit wegen fehlender bzw. veralteter Sensorbereitschaft ab. Der neue native Gazebo-Test beseitigt diesen Messpfad und zeigt ein anderes, reproduzierbares Problem: Das aktuelle Kettenmodell ist noch kein echtes Kettenlaufwerk, sondern ein Zweiradmodell mit vier starren Kugelstuetzpunkten. An Rampeneinfahrten und auf dem Unebenheitsprofil entstehen dadurch harte Mehrpunktkontakte ohne Federung, Raupenbandauflage oder Laufrollen. Die Raeder drehen weiter, der Koerper macht aber kaum Fortschritt.

Die Kontrolllaeufe auf einer durchgehenden geneigten Ebene sind der wichtigste Gegencheck: dasselbe Modell, dieselben 40 Nm Gelenklimits, dieselbe Masse und dieselben Reibwerte fahren 5 Grad und 15 Grad stabil. Die reine Hangkraft, Schwerpunktlage oder das Antriebsdrehmoment sind daher nicht die Hauptursache. Der Ausfall entsteht am diskreten Kontaktuebergang und am Ersatzkontaktmodell.

Zusaetzlich zeigt die native Kontaktaufzeichnung bei Rampen und Unebenheiten physikalisch unplausible Kontaktkraefte: In vielen Kontaktpunkten meldet Gazebo/DART tangentiale Kraefte bei praktisch null Normalkraft. Diese Werte verletzen selbst eine konservative aeussere Schranke der DART-Reibpyramide. Damit sind die aktuellen Kontaktkraefte in diesen Fehlerfaellen nicht als reale Zugkraft- oder Motorauslegungswerte verwendbar.

## Statischer Modellbefund

| Punkt | Befund |
| --- | --- |
| Gesamtmasse | 65,0 kg |
| Schwerpunkt | x=0, y=0, z=0,2875 m |
| Haupttraegheit um Schwerpunkt | diag(2,065; 3,495; 3,622) kg m2 |
| Kollisionsmodell | Basisbox, zwei Zylinderradkontakte, vier starre Kugelstuetzpunkte |
| Kettenvisuals | nur Anzeige, keine eigene Kollision, keine Masse, keine Raupenbandphysik |
| Radkontakt | Radius 0,12 m, Breite 0,09 m, Reibwert mu=mu2=0,6 |
| Stuetzelemente | Kugeln r=0,065 m, feste Verbindung zur Basis, Reibwert mu=mu2=0,015 |
| Gelenklimits | Radgelenke 40 Nm, 8 rad/s, keine expliziten Positionsgrenzen |
| Controller | Gazebo DiffDrive setzt Gelenkgeschwindigkeiten; DART verwendet dafuer ServoMotorConstraint mit Kraftlimit |

Die Traegheitstensoren sind positiv definit und verletzen die Dreiecksungleichung nicht. Auffaellig, aber nicht als Hauptursache belegt: Rad- und Kugeltraegheiten entsprechen nicht exakt den homogenen Standardkoerpern. Das sollte spaeter korrigiert werden, erklaert aber nicht, warum die kontinuierliche 15-Grad-Ebene funktioniert und die Rampeneinfahrt scheitert.

Die statische Kippreserve ist fuer diese Tests nicht der begrenzende Faktor. Aus dem Schwerpunkt ergeben sich grob 44,2 Grad Laengs- und 33,5 Grad Quer-Kippwinkel gegen den konservativen Stuetzrand. In den Fehlerlaeufen bleibt die gemessene Koerperneigung unter 0,21 Grad, weil das Modell schon vor dem eigentlichen Hang stehen bleibt.

## Reproduzierbarer Test

Der neue Pruefpfad liegt in:

- `config/terrain-audit.json`
- `scripts/terrain_audit.py`
- `simulation/terrain_audit/`
- `scripts/verify_terrain_logs.py`
- `scripts/inspect_tracked_physics.py`

Jeder Lauf startet einen eigenen nativen Gazebo-Server ohne Browser, ohne ROS-HTTP-Wartepfad und ohne externen ros_gz_bridge. Der Audit-Plugin sendet nur einen definierten Twist-Befehl an den unveraenderten DiffDrive-Controller: 2 s setzen, 20 s mit 0,15 m/s, 2 s Stopp. Aufgezeichnet wird bei 1 ms Simulationsschritt und standardmaessig 1000 Hz.

Primaerfaelle:

| Fall | Aufbau |
| --- | --- |
| `grade_0` | ebener Boden |
| `grade_5` | ebener Boden, dann definierte 5-Grad-Rampe mit planem Einlauf |
| `grade_10` | wie oben mit 10 Grad |
| `grade_15` | wie oben mit 15 Grad |
| `uneven` | altes definiertes Unebenheitsprofil, 24 Segmente, 0 bis 20 mm Hoehe |

Kontrollfaelle:

| Fall | Zweck |
| --- | --- |
| `plane_5` | durchgehende 5-Grad-Ebene ohne Rampeneinfahrt |
| `plane_15` | durchgehende 15-Grad-Ebene ohne Rampeneinfahrt |
| `legacy_5` | alter Rampenaufbau zur Abgrenzung gegen Geometrieaenderungen |

Reproduktion:

```bash
source /opt/ros/jazzy/setup.bash
cmake -S simulation/terrain_audit -B build/terrain-audit
cmake --build build/terrain-audit -j2
python3 scripts/terrain_audit.py --output results/terrain-audit-neu
python3 scripts/terrain_audit.py --cases plane_5 plane_15 --repeats 1 --output results/terrain-audit-kontrolle
python3 scripts/verify_terrain_logs.py results/terrain-audit-neu
python3 scripts/plot_terrain_audit.py results/terrain-audit-neu --output docs/validation/terrain-audit
```

`data_complete=true` bedeutet nur, dass die Messung vollstaendig ist. Ob der Roboter den Fall besteht, steht in `traversal_pass`.

## Messwerte

Alle drei Seeds lieferten identische Werte, weil das aktuelle Modell und Terrain deterministisch sind.

| Fall | Daten vollstaendig | Strecke in 20 s | bestanden | mittlere Koerpergeschw. | max. Pitch | Spitzenmoment |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| 0 Grad | ja | 2,981 m | ja | 0,150 m/s | 0,000 Grad | 2,70 Nm |
| 5 Grad Rampe | ja | 0,217 m | nein | 0,00002 m/s | 0,174 Grad | 37,15 Nm |
| 10 Grad Rampe | ja | 0,214 m | nein | 0,00013 m/s | 0,197 Grad | 37,17 Nm |
| 15 Grad Rampe | ja | 0,211 m | nein | 0,00028 m/s | 0,202 Grad | 37,12 Nm |
| Unebenheiten | ja | 0,205 m | nein | -0,00088 m/s | 0,165 Grad | 40,00 Nm |

Kontrolllaeufe auf durchgehenden Ebenen:

| Fall | Strecke in 20 s | bestanden | mittlere Koerpergeschw. | Pitch | mittleres Radmoment |
| --- | ---: | --- | ---: | ---: | ---: |
| `plane_5` | 2,981 m | ja | 0,150 m/s | 5,000 Grad | 3,59 Nm |
| `plane_15` | 2,977 m | ja | 0,150 m/s | 15,000 Grad | 10,15 Nm |

Das passt zur einfachen Hangrechnung: 65 kg auf 15 Grad brauchen ideal etwa 9,90 Nm pro Rad gegen die Schwerkraft, plus kleine Stuetzwiderstaende. Das gemessene 15-Grad-Moment von etwa 10,15 Nm ist plausibel und weit unter 40 Nm. Damit ist das globale Gelenklimit fuer glatte Haenge nicht das Problem.

## Kontaktbefund

Auf der Ebene ist die Kontaktbilanz plausibel. Das flache Modell traegt etwa 638 N Normalkraft, passend zu 65 kg Gewichtskraft. Die gemessenen Radmomente von rund 0,26 Nm im stationaeren Mittel passen zu den vier gleitenden Kugelstuetzen mit mu=0,015.

In den Rampen- und Unebenheitsfaellen kippt die Kontaktqualitaet. Beispiel aus `uneven_seed11`: Bei t=3,778 s meldet der linke Radkontakt 130,0 N tangentiale Kraft bei 0,0 N Normalkraft. Das ist mit Coulomb-Reibung nicht vereinbar. Der Pruefer verwendet sogar die lockere Schranke `sqrt(2) * mu * N`, weil DART eine zweiachsige Reibpyramide nutzt. Trotzdem treten Verletzungen auf:

| Fall | Anteil unplausibler Kontaktpunkte | Punkte mit Tangentialkraft >1 N bei N<0,01 N |
| --- | ---: | ---: |
| 0 Grad | 0,0 % | 0 |
| 5 Grad Rampe | 21,6 % | 4513 |
| 10 Grad Rampe | 27,3 % | 7669 |
| 15 Grad Rampe | 24,5 % | 18038 |
| Unebenheiten | 46,5 % | 57288 |

Ein Halbzeitschritt mit 0,5 ms beseitigt das Verhalten nicht: `grade_5` bleibt bei 0,217 m, `uneven` bei 0,205 m. Die genauen Kontaktkraefte aendern sich, der qualitative Fehler bleibt. Das spricht gegen einen einfachen Abtastfehler in der 1000-Hz-Aufzeichnung.

## Ursache, Status, Konsequenz

| Ursache | Status | Beleg | Konsequenz |
| --- | --- | --- | --- |
| Browser/HTTP/Sensor-Wartepfad im alten 5-Grad-Test | bestaetigt fuer alten Fehler | alter Lauf brach wegen `imu_stale`/Bereitschaft ab | alter Rampenfehler nicht als Mechaniknachweis verwenden |
| Zu wenig Antriebsmoment fuer glatten Hang | widerlegt fuer 5 bis 15 Grad | `plane_15` faehrt mit 10,15 Nm pro Rad | Drehmoment nicht blind erhoehen |
| Schwerpunkt/Kippen | widerlegt fuer aktuelle Fehlerlaeufe | Pitch/Roll bleiben sehr klein, kein Bodenkontakt der Basis | Schwerpunkt nicht als Erstes verschieben |
| Starres Rad-/Kugel-Ersatzmodell statt Raupenlaufwerk | bestaetigt als Modellgrenze | Raeder drehen, Koerper stoppt am diskreten Kontaktuebergang; Kontroll-Ebene funktioniert | echtes Ketten-/Laufrollenmodell mit Nachgiebigkeit entwickeln |
| Kontaktkraefte in Rampen/Unebenheiten | unplausibel gemessen | Tangentialkraft bei N nahe null, Verletzung der Reibpyramiden-Schranke | diese Kraefte nicht fuer Hardwareauslegung verwenden |
| Exakte Solver-Ursache in DART/Gazebo | noch nicht abschliessend isoliert | Quellen zeigen, dass Kontaktkraefte aus DART-Impulsen nach Gazebo exportiert werden | kleiner Minimalfall und alternatives Kontaktmodell als naechster Schritt |

## Quellen zum Physikpfad

Geprueft wurden die installierten bzw. passenden Quellversionen Gazebo Sim 8.11.0, gz-physics 7.6.0 und DART 6.13.2. Relevant sind:

- Gazebo DiffDrive setzt `JointVelocityCmd`: <https://github.com/gazebosim/gz-sim/blob/gz-sim8_8.11.0/src/systems/diff_drive/DiffDrive.cc>
- Gazebo Physics uebergibt Velocity-Commands an die Physik und loescht Commands nach dem Schritt: <https://github.com/gazebosim/gz-sim/blob/gz-sim8_8.11.0/src/systems/physics/Physics.cc>
- gz-physics/DART verwendet fuer Velocity-Commands Servo-Constraints: <https://github.com/gazebosim/gz-physics/blob/gz-physics7_7.6.0/dartsim/src/JointFeatures.cc>
- DART begrenzt Servo-Constraint-Impulse mit dem Kraftlimit mal Zeitschritt: <https://github.com/dartsim/dart/blob/v6.13.2/dart/constraint/ServoMotorConstraint.cpp>
- DART-Kontakte bauen Normalkraft und zwei Tangentialrichtungen auf: <https://github.com/dartsim/dart/blob/v6.13.2/dart/constraint/ContactConstraint.cpp>
- gz-physics exportiert DART-Kontaktkraft, Normale und Tiefe nach Gazebo: <https://github.com/gazebosim/gz-physics/blob/gz-physics7_7.6.0/dartsim/src/SimulationFeatures.cc>

## Artefakte

- Hauptserie: [fullrate-main-summary.json](validation/terrain-audit/fullrate-main-summary.json), [fullrate-main-channel-verification.json](validation/terrain-audit/fullrate-main-channel-verification.json)
- Kontrollserie: [fullrate-controls-summary.json](validation/terrain-audit/fullrate-controls-summary.json), [fullrate-controls-channel-verification.json](validation/terrain-audit/fullrate-controls-channel-verification.json)
- Halbzeitschritt: [halfstep-summary.json](validation/terrain-audit/halfstep-summary.json), [halfstep-channel-verification.json](validation/terrain-audit/halfstep-channel-verification.json)
- Statischer Modellbefund: [tracked-static-physics.json](validation/terrain-audit/tracked-static-physics.json)
- Plots: [terrain-overview.png](validation/terrain-audit/terrain-overview.png), [grade-5-diagnostics.png](validation/terrain-audit/grade-5-diagnostics.png)

Rohdaten mit CSV, Kontakt-JSONL, Weltdateien, Quellkopien und Manifesten liegen in `results/terrain-audit-fullrate-main-20260907/`, `results/terrain-audit-fullrate-controls-20260907/` und `results/terrain-audit-halfstep-20260907/`.

## Naechste technische Schritte

Als naechstes sollte nicht an Reibwert, Schwerpunkt oder Motorlimit gedreht werden. Zuerst brauchen wir ein mechanisch sinnvolleres Fahrwerksmodell: Raupenband- oder Mehrrollen-Ersatz mit realer Aufstandslaenge, nachgiebigen Laufrollen, definierter Bodenfreiheit, sauberem Kontakt ohne starre Kugelstuetzen und einer separaten Minimalpruefung fuer die Kontaktkraft-Plausibilitaet. Erst wenn diese Kontaktbilanz gruen ist, sind Zugkraft, Materialstaerke und Motor-/Hydraulikdimensionierung aus Gazebo-Daten sinnvoll ableitbar.
