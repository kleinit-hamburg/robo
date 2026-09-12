# Fahrwerks-Testsystem und verbesserte Kettengeometrie

Stand 2026-09-12. Dieser Schritt richtet das Projekt staerker auf mechanische Entwicklung aus. Die Weboberflaeche bleibt Bedien- und Anzeigeebene; alle Fahraussagen stammen aus Gazebo Harmonic/DART. Es wurde keine autonome Navigation, Pflanzen-KI oder neue Gartenlogik eingebaut.

## Zentrale Roboterspezifikation

Die verstreuten Fahrwerkskonstanten sind in `config/robot-spec.json` gebuendelt. Daraus werden die SDF-Modelle und die vorbereitenden Xacro-Dateien erzeugt:

- `models/tracked/model.sdf`: Baseline des bisherigen starren Platzhalter-Fahrwerks.
- `models/tracked_improved/model.sdf`: Uebergangsvariante mit hoeherem Unterboden und groesseren vorderen angetriebenen Umlenkrollen. Diese Variante ist noch kein gutes Raupenmodell.
- `models/tracked_bogie/model.sdf`: erstes federndes Raupen-Pruefmodell mit sechs angetriebenen, vertikal gefuehrten Laufrollen pro Seite.
- `urdf/tracked*.urdf.xacro`: zentrale Robotikbeschreibung fuer den spaeteren URDF/Xacro-Pfad.

Jedes strukturelle Bauteil hat jetzt eine `part_id`, Materialnotiz, Masse-/Massreferenz und einen Platzhalter fuer spaetere CAD-Dateien. Visual- und Collision-Geometrien sind getrennt. Es gibt keine monolithische Gesamt-STL.

## Warum das bisherige Modell an Hindernissen scheitert

Die Baseline ist physikalisch kein Kettenlaufwerk. Sie besteht aus zwei mittigen Antriebsraedern und vier starr mit dem Chassis verbundenen, niedrig reibenden Kugelstuetzen. Die dekorativen Kettenbaender haben keine Kollision und keine Masse. Das war fuer fruehe Fahrbefehle ausreichend, aber fuer die mechanische Bewertung eines Raupenfahrwerks fachlich zu grob. Bei kleinen Stufen oder Rampeneinfahrten trifft der starre Stuetz-/Radverbund auf einen diskreten Kontaktuebergang. Die Raeder drehen fast mit Sollgeschwindigkeit, der Koerper bleibt aber stehen; der Schlupf liegt bei etwa 99 Prozent.

Wichtig: In den Stufenlaeufen setzt der Unterboden nicht auf. Der Fehler ist deshalb nicht primaer zu geringe Chassisfreiheit, sondern die Kombination aus schlechtem Anfahrwinkel, starren Stuetzpunkten, fehlender Raupenauflage und ungünstiger Lastuebertragung in der Platzhalterkinematik.

## Geometrieaenderung

| Parameter | Baseline `tracked` | Uebergang `tracked_improved` | Federrollen `tracked_bogie` |
| --- | ---: | ---: | ---: |
| Spurweite | 0,52 m | 0,70 m | 0,70 m |
| grobe Gesamtbreite | 0,65 m | 0,86 m | 0,86 m |
| Laenge Kettenhuelle | 0,54 m | 0,86 m | 0,92 m |
| wirksamer Rollendurchmesser | 0,24 m | 0,36 m | 0,17 m, sechs Rollen je Seite |
| nominelle Chassisfreiheit | 0,17 m | 0,25 m | 0,27 m |
| Federweg | keiner | keiner | ±70 mm je Laufrolle |
| Gelenkmomentlimit | 40 Nm | 80 Nm | 55 Nm je Rolle |
| Stuetzkonzept | vier starre Kugelstuetzen | zwei hintere Stuetzrollen-Platzhalter | 12 gefederte Laufrollen |

`tracked_improved` bleibt nur eine Uebergangsvariante. Das erste brauchbare Raupen-Pruefmodell ist `tracked_bogie`: Mehrpunktauflage, drehende Laufrollen und Feder-/Daempferfuehrung bilden das erwartete Kriechen ueber kleinere Hindernisse erstmals physikalisch ab.

## Gazebo-Testgelaende

Der neue Benchmark `scripts/chassis_benchmark.py` erzeugt pro Versuch eine eigene Gazebo-Welt. Testobjekte sind absichtlich technische Pruefkoerper statt dekorativer Gartenumgebung:

- Stufen/Steine: 30, 50, 80, 100, 150 mm
- Rampen: 10, 20, 30, 40 Grad
- Mulde/Graben
- diagonale Bodenwelle zur Verschränkung
- Seitenneigung
- schmale Durchfahrt

Messwerte pro Lauf: geschafft/nicht geschafft, Strecke, maximale Roll-/Pitchlage, Chassis-Kontakt, Schlupf, Spitzenmoment, Geschwindigkeit, Fahrzeuglage und Schwerpunktposition. Erfolg bedeutet hier: mindestens 1,25 m Vortrieb, kein Chassis-Kontakt und keine Neigung ueber 35 Grad.

Reproduktion:

```bash
source /opt/ros/jazzy/setup.bash
python3 scripts/build_preview_models.py
cmake -S simulation/terrain_audit -B build/terrain-audit
cmake --build build/terrain-audit -j2
python3 scripts/chassis_benchmark.py --variants tracked tracked_improved --output results/chassis-benchmark-neu
```

## Ergebnis der aktuellen Matrix

| Testfall | Baseline | Uebergang | Federrollen/Bogie |
| --- | --- | --- | --- |
| 30-mm-Stufe | nein, 0,30 m | ja, 2,06 m | ja, 2,08 m |
| 50-mm-Stufe | nein, 0,29 m | ja, 2,03 m | ja, 2,05 m |
| 80-mm-Stufe | nein, 0,29 m | nein, 0,32 m | ja, 2,01 m |
| 100-mm-Stufe | nein, 0,29 m | nein, 0,31 m | nein, 0,18 m |
| 150-mm-Stufe | nein, 0,29 m | nein, 0,29 m | nein, 0,18 m |
| 10-Grad-Rampe | nein, 0,26 m | ja, 2,07 m | ja, 2,07 m |
| 20-Grad-Rampe | nein, 0,26 m | ja, 2,02 m | ja, 2,01 m |
| 30-Grad-Rampe | nein, 0,25 m | nein, 0,88 m | ja, 1,92 m |
| 40-Grad-Rampe | nein, 0,25 m | nein, 0,85 m | nein, 0,90 m |
| Graben | ja | ja | ja |
| diagonale Bodenwelle | nein | nein | ja |
| Seitenneigung | nein | ja | ja |
| schmale Durchfahrt | ja | ja | ja |

Die neue Hindernisgrenze liegt mit dem federnden Bogie-Modell bei 80 mm Stufenhoehe und 30 Grad Rampe. 100 mm Stufen und 40 Grad Rampe bleiben offen. Die Verbesserung entsteht durch Federweg und Lastverteilung, nicht durch eine Browserdarstellung oder eine neue Autonomiefunktion.

## Dashboard

Die Weboberflaeche zeigt jetzt je Variante zentrale Fahrwerksparameter und die letzte Benchmarkserie an. Das Dashboard liest `config/robot-spec.json` und `docs/validation/chassis-benchmark-summary.json`. Es simuliert keine eigene Physik und berechnet keine eigenen Erfolgskriterien im Browser.

## Offene mechanische Entscheidungen

- echte Kettenmodellierung: Gazebo-Track-System, Mehrrollen-Ersatz oder spaeter detaillierte Laufwerksdynamik;
- Federung oder Pendelrollen fuer Marschboden, Bodenwellen und seitliche Verschränkung;
- endgueltige Spurweite 0,65 bis 0,75 m gegen Kartoffel-/Erdbeerreihen und Gesamtbreite;
- Motor-/Getriebegrenzen aus realistischen Kontaktkraeften statt aus dem aktuellen Platzhalter;
- Bodenmodell fuer schweren Kirchwerder Marschboden mit reduzierter Tragfaehigkeit und Schlupf;
- Bauteilmaterialien und Wandstaerken fuer 3D-Druck-Prototypen mit Metallachsen/Motoren.

Die Richtung ist damit klar: Die reine Blockade an kleinen Steinen ist erst mit der gefederten Mehrrollenauflage fachlich geloest. Fuer echte Gartenrobustheit brauchen wir als naechstes eine bessere Kettenfuehrung, ein validiertes Bodenmodell und eine Entscheidung, ob die reale Mechanik mit Bogies, Pendelrollen oder einem Gazebo-Track-System weitergefuehrt wird.
