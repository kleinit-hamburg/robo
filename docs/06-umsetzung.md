# Repository-Struktur und nächste Schritte

## Vorhanden

```text
README.md
config/
  concepts.json                # Entwurfsannahmen
  preview-concepts.json        # aktuelle Browserfähigkeiten
  benchmark.json               # geplante Versuche, einschließlich M4-Laststufen
  milestones.json              # M1–M6 mit Status je Konzept
models/{tracked,quadruped,humanoid}/model.sdf
worlds/browser-preview.sdf      # sichtbare Demo, noch keine Benchmarkstrecke
scripts/                       # Installation, Modellgenerator, Browser und Fahrlogik
web/                           # lokale 3D-Ansicht und Bedienung
tests/                         # Fahrlogik- und Live-Funktionsprüfungen
docs/                          # Konzepte, Architektur, Physik, Versuchsplan, Bedienung
ros2_ws/src/README.md           # noch keine eigenen ROS-Pakete
results/README.md              # Laufakten der M1-Prüfung
```

## Geplante ROS-Pakete

| Paket | Verantwortung |
|---|---|
| `garden_interfaces` | Pflanzenbeobachtung, Arbeitsaufträge, Ergebnis-/Fehlerzustände |
| `garden_description` | Xacro, einfache Trägheits-/Kollisionskörper, drei Kinematiken |
| `garden_gazebo` | SDF-Welt, Sensoren, Bridge-Konfiguration, Spawning |
| `garden_plant_physics` | Gazebo-Systemplugin für Wurzel, Griff, Schnitt und Stechwiderstand |
| `garden_control` | Controllerkonfigurationen und Adapter; nach Plattform getrennte Regler |
| `garden_perception` | gemeinsame kamerabasierte Pflanzenbeobachtung |
| `garden_state_estimation` | Sensorfusion und Zustandsschätzung |
| `garden_navigation` | Zielanfahrten und Basis-/Schrittplanungsadapter |
| `garden_manipulation` | Armplanung und kraftbegrenzte Kontaktregelung |
| `garden_tool_controller` | Werkzeug-Aktuierung und Werkzeugzustand |
| `garden_task_manager` | autonome Methodenauswahl und Aufgabenablauf |
| `garden_stability_monitor` | Kontakt- und Kippreserven |
| `garden_safety_supervisor` | Abbruch, Watchdogs und Freigabe |
| `garden_benchmark` | Szenen, Seeds, Rosbag, Metriken und Berichte |
| `garden_bringup` | spätere Launch-Einstiege `sim` und `real`, Parametersätze |
| `garden_hardware` | erst später reale Treiber; kein Beschaffungsumfang |

Python für Orchestrierung/Auswertung, C++ für Physikplugin und zeitkritische Regler. Eigene Simulationslogik bleibt aus den produktiven ROS-Nodes heraus. Keine Paketgerüste anlegen, die einen bereits funktionierenden Stack vortäuschen.

## Verbindliche Meilensteine M1–M6

Diese vom Nutzer ergänzte Folge ersetzt die bisherige M0–M5-Nummerierung. Konzeptbasis, Installation und Browseransicht sind Vorarbeiten. Meilensteine werden **pro Konzept** freigegeben: Die Kette kann weiterentwickelt werden, während Gang-/Balanceregler der beiden Beinkonzepte noch entstehen. Ein Erfolg der Kette schließt keinen Meilenstein für alle drei ab. Maschinenlesbarer Stand: [milestones.json](../config/milestones.json).

| Meilenstein | Ergebnis | Stand Kette / Quadruped / Humanoid |
|---|---|---|
| **M1 – Bewegen** | vorwärts/rückwärts, links/rechts drehen, umdrehen, anhalten | teilweise / offen / offen |
| **M2 – Gelände bewältigen** | Ebene, Unebenheiten, Steigung, Reibungsproxy und Hindernisse | offen / offen / offen |
| **M3 – Arm bewegen** | geregelte Gelenke und gezieltes Positionieren des Werkzeugs | offen / offen / offen |
| **M4 – 100/250/500/1000 N Werkzeuglast** | reproduzierbarer Lastprüfstand und dokumentierte Belastungsgrenzen | offen / offen / offen |
| **M5 – Virtuelle Pflanze greifen** | greifen, halten, lösen; Schlupf und Bruch nachvollziehbar | offen / offen / offen |
| **M6 – Identische Unkraut-Teststrecke für alle drei** | gemeinsamer End-to-End-Vergleich mit Zeit, Energie und Erfolg | offen / offen / offen |

### M1 – Bewegen

Gemeinsame Befehle und ROS-Schnittstelle aus [der Roboterbedienung](09-roboterbedienung.md) weiterverwenden. Kettenfahrzeug fährt physikalisch mit einem vereinfachten Rad-/Stützmodell; die beiden Beinkonzepte benötigen echte Gelenk-, Stand-, Gang- und Balanceregler. Keine statisch fixierten Körper oder verschobenen Vorschauen als bestandener Gehversuch.

Abnahme je Konzept: zehn wiederholbare Läufe auf ebenem Boden (μ = 0,6), jeweils 1 m vorwärts/rückwärts (Streckenfehler ≤0,10 m), 90° links/rechts und 180° wenden (Endfehler ≤5°), geregeltes Anhalten aus 0,15 m/s (Nachlauf ≤0,10 m). Loslassen, Fokus-/Verbindungsverlust und veraltete Sensordaten müssen stoppen. Keine Stürze oder unerlaubten Gelenkzustände. Die aufgezeichneten Serien erfüllen die vollständige M1-Abnahme noch nicht: Wiederholte Weltstarts liefern nicht zuverlässig alle Messdaten. Fahrfunktionen sind teilweise nachgewiesen; [Prüfbericht und offene Fehler](10-m1-abnahme.md).

### M2 – Gelände bewältigen

Nach M1 pro Konzept die Fälle T01–T05 aus [dem Testplan](04-testplan.md) durchführen. Erfasst werden bewältigte Steigungen/Hindernisse, Schlupf, Körperkontakt, Kippreserve und Abbrüche. Mindestens die einfache Stufe (±10 mm Unebenheit, 5° Steigung, μ = 0,25 auf Ebene, 20-mm-Schwelle) muss ohne Sturz durchfahren werden. Höhere Stufen werden bis zur Fähigkeitsgrenze bewertet; gescheiterte Fälle werden nicht entfernt.

Die aktuell sichtbare Rampe ist noch kein Gelände-Nachweis. Kontakt-/Antriebsmodell vor quantitativen Vergleichen validieren; insbesondere den Ketten-Radersatz kennzeichnen oder ersetzen. Reduzierte Reibung bleibt ein Proxy ohne Einsinkphysik.

### M3 – Arm bewegen

Die starren Arm-/Handvisuals durch Gelenke mit Masse, Trägheit, Kollision und tatsächlich wirksamen Positions-, Geschwindigkeits- und Momentengrenzen ersetzen. Kette/Quadruped: jeweils ein Arm; Humanoid: beide Arme einzeln und koordiniert. `ros2_control`-Anbindung und gemeinsame Aufgabenbefehle verwenden.

T13: sichere Ausgangspose, Zielanfahrt, bodennahe Arbeitspose und Rückzug. Ziele liegen in einem vor dem Test festgelegten gemeinsamen Arbeitsbereich; unerreichbare Ziele werden ausdrücklich zurückgemeldet. Zielabweichung ≤10 mm und ≤10° bei 2 s Halten mit 2 kg Werkzeugmasse, zunächst ohne zusätzliche Prozesskraft. Keine Fixierung der Basis im Integrationslauf; keine Körper-/Selbstkollision, Sättigung oder Balanceverluste. Gelenkgrenzen und Stop/Rückzug separat prüfen. Greifen gehört erst zu M5.

### M4 – 100/250/500/1000 N Werkzeuglast

Nach M3 einen Starrkörper-Prüfkörper am Werkzeuganschluss verwenden; eine greifbare Pflanze ist dafür noch nicht erforderlich. Die vier Stufen sind **angeforderte externe Lasten**, keine Zusage, dass jede Konstruktion 1000 N trägt. Alle drei erhalten denselben Lastverlauf, dieselben Vorzeichen-/Hebelarmdefinitionen und dieselbe Auswertung. Ausführung und Abnahme sind in T14 und im [Physikmodell](03-physikmodell.md#m4--erweiterte-werkzeuglasten) festgelegt.

M4 ist pro Konzept bearbeitet, wenn alle vier Stufen in allen definierten Richtungen entweder gültig gemessen oder mit nachvollziehbarer Grenzverletzung kontrolliert abgebrochen wurden. Ein Abbruch ist **kein bestandener Lastfall**, sondern Teil der dokumentierten Fähigkeitsgrenze. Ein nicht implementierter Regler oder unvalidierter Kraftplugin darf nicht als mechanische Unfähigkeit verbucht werden. Keine automatische Erhöhung von Gelenkgrenzen, Masse oder Haftreibung, um einen Test grün zu machen.

### M5 – Virtuelle Pflanze greifen

Nach M3 und validierter Kraftübertragung aus M4 ein kollisionsfähiges Pflanzen-/Greifermodell mit Kontaktprüfung, begrenzter Klemmkraft, Schlupf, Stängelbruch und Freigabe implementieren. T07 prüft drei Stängeldurchmesser, drei Greifreibwerte und 2 s Halten. Baseline: fünf erfolgreiche Greif-/Halte-/Lösezyklen bei 8 mm Stängeldurchmesser, μ_g = 0,5 und 25 N Widerstand; keine Nutzpflanzenverletzung. Weitere Stufen charakterisieren Fehlgriffe und Belastungsgrenzen.

Zuerst eine ausdrücklich markierte bekannte Zielpose verwenden, danach erkannte Pflanzen. Ein optisch geschlossenes Maul oder unbegrenzt steife Bindung ohne Kraft-/Schlupfgrenze gilt nicht als Erfolg. Das Wurzelwiderstandsmodell bleibt getrennt von den M4-Prüfkörperlasten.

### M6 – Identische Unkraut-Teststrecke für alle drei

M1–M5 je Konzept zusammenführen und T15 ausführen. Eine gemeinsame versionierte Strecke mit zehn Pflanzen wird für Kette, Quadruped und Humanoid jeweils aus demselben Zustand neu geladen. Pflanzen, Boden, Hindernisse, Reihenfolge, Seeds und Werkzeuglastkennlinien bleiben identisch. Unterschiedliche zulässige Fahr-/Fußschrittplanung ist Teil des Konzeptvergleichs.

Umfang: anfahren, erkennen, stabilisieren, greifen, ziehen oder schneiden/abstechen, Resultat prüfen und Pflanzenrest ablegen. Bekannte Zielposen bilden einen getrennten Mechaniklauf; die eigentliche Autonomie-Abnahme verwendet gemeinsame Wahrnehmung ohne Zugriff auf verdeckte Wurzelparameter. Schneiden/Abstechen und Methodenauswahl müssen bis M6 zusätzlich zu M5 implementiert sein.

Die bestehende Strecke aus zehn nominalen Wurzelwiderständen bleibt der Baseline-Vergleich. Zusätzlich vier getrennte, für alle Konzepte identische Lastvarianten mit 100/250/500/1000 N Wurzel-Peak planen. Stängelbruch und Methodenwechsel bleiben aktiv; ein nomineller 1000-N-Wurzelpeak bedeutet deshalb nicht automatisch, dass 1000 N am Werkzeug erreicht werden. Diese Varianten sind synthetische Belastungsfälle, keine behaupteten botanischen Kennwerte.

Abnahme: Auswertungsseeds 100–129, Erfolgs-/Schadensquote, Wh pro Erfolg, Zeit pro Aufgabe, Durchsatz, Spitzenkräfte und Stabilitätsreserven gemäß [Messvertrag](05-messgroessen.md). Baseline-Ziele daraus bleiben bestehen. Kontrollierte Ablehnungen und Ausfälle zählen mit; unfertige Software wird gesondert als nicht geprüft markiert. Keine Gesamtrangliste aus den heutigen Vorschaumodellen.

## Funktionen vor endgültiger Prototypauslegung

Zuerst den vollständigen virtuellen Funktionsumfang entwickeln, danach Referenzgröße und mechanische Auslegung des ersten Testprototyps festlegen. Die bestehenden Maße bleiben vorläufige, veränderbare Simulationsannahmen. Gedruckte Bauteile mit Motoren, optionaler Hydraulik, LiDAR und Kamera sind für den späteren Aufbau vorgesehen. Umfang und Übergang stehen in [Funktionen und Prototyp](11-funktionen-und-prototyp.md). Die endgültige Auslegung wird anschließend in der Simulation rückgeprüft.

## Geltungsbereich

Alles bleibt virtuelle Entwicklung unter Ubuntu 24.04, ROS 2 Jazzy und Gazebo Harmonic. Kein Hardwarekauf und kein detailliertes CAD. Ein späterer verkleinerter Druckprototyp folgt erst nach dem virtuellen Vergleich und einer eigenen Auslegung. Die existierenden Funktionsprüfungen stehen in [Installation](07-installation.md) und [Roboterbedienung](09-roboterbedienung.md); M2–M6 sind geplant, nicht ausgeführt.
