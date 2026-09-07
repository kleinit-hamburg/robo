# Gemeinsame Gazebo-Testumgebung

## Welt und faire Startbedingungen

Eine 12 × 8 m große Welt mit austauschbaren 3 × 2 m Testflächen, identischem Licht, Boden- und Pflanzenmodell. Je Lauf genau ein Roboter; Szene und Zufallszustand vor jedem Lauf vollständig neu laden. Gleiche Weltkoordinaten und Zielpflanzen für alle Plattformen. Die Startpose wird so gewählt, dass die vordere Kollisionshülle 1,0 m von der Zielpflanze entfernt ist, Blickrichtung zum Ziel. Gleiche Mindestdistanz der Hülle ist fairer als identische Basisposition trotz anderer Körperlänge. Zusätzlich 3 m Anfahrstrecke für Mobilitätstests.

Arbeitsbereich: Pflanzenhöhe 0,05/0,15/0,30 m, Stängeldurchmesser 0,003/0,008/0,015 m; nominal 0,15 m und 0,008 m. Eine Nutzpflanze 0,12 m neben der Zielpflanze, zusätzliche Ablagefläche 0,5 m seitlich. Schutzzone um die Nutzpflanze Radius 0,04 m plus 0,03 m Abstand für Werkzeugkörper. Ein 0,90 m breiter Korridor begrenzt die Plattformgeometrie; engerer 0,65-m-Korridor separat als Fähigkeitstest. Nicht passende Roboter erhalten `infeasible_geometry`, keinen übersprungenen Versuch.

Gemeinsame Sensoren zuerst ideale kalibrierte Messungen, anschließend identische Fehlermodelle: Tiefenrauschen σ = 5 mm, Posefehler σ = 10 mm, Kraftmessrauschen σ = 1 N, Sensorausfall 0,5 s und zusätzliche Verzögerung 50 ms. Konzeptspezifische Montage erlaubt, aber dokumentiert; keine versteckte Ground Truth in autonomen Läufen. Dieselbe Erkennungsimplementierung, Pflanzenverteilung und Aufgabenlogik; unterschiedliche Bewegungsregler und Posen sind Teil des jeweiligen Konzepts.

## Versuchsgruppen

Die Folge M1–M6 ist in [der Umsetzungsplanung](06-umsetzung.md) festgelegt. T01–T12 bleiben als Basis-/Charakterisierungstests erhalten; T13–T15 ergänzen Armbewegung, die neue Lastreihe und den gemeinsamen End-to-End-Kurs.

| ID | Test | Stufen und Ablauf | Auswertung |
|---|---|---|---|
| T01 | Ebene | μ 0,6, 3 m geradeaus und 90°-Wende | Spurfehler, Schlupf, Zeit, Energie |
| T02 | Unebenheiten | deterministische Höhenfelder Amplitude ±10/±25/±50 mm, Wellenlänge 0,20 m | Bodenkontakt, Rumpfbewegung, Passage |
| T03 | Steigung | 5/10/15°, aufwärts, abwärts und quer | Traktion, Kippreserve, Energie |
| T04 | Weicher Boden als Reibungsproxy | ebene Fläche μ 0,25; Robustheit μ 0,15 | Schlupf, Stillstand; kein Einsinknachweis |
| T05 | Hindernisse | Schwellen 20/50/100 mm hoch und 100 mm tief, Stein 100 mm hoch × 150 mm breit | Übersteigen/Umfahren, Kontakt, Nutzpflanzenschutz |
| T06 | Annäherung | 1 m Hüllenabstand; Ziel aus Pflanzenkarte | Werkzeugpose ≤10 mm und ≤10°, Basis im zulässigen Arbeitsbereich |
| T07 | Greifen | drei Durchmesser, μ_g 0,2/0,5/0,8, 2 s Halten | Schlupf, Klemmkraft, Beschädigung |
| T08 | Ausziehen | 25/75/150/300 N Peak; 60 mm Freigabeweg | Kraftkurve, vollständiges Lösen, Stängelbruch |
| T09 | Schneiden/Abstechen | Schere 50/150/300 N; Stechen 50/150/300 N mit anschließendem Ziehen | Weg, Arbeit, Methode, Wurzelstatus |
| T10 | Seitliche Werkzeugkräfte | ±vorwärts/±seitlich, 25/75/150 N, Werkzeughöhe 0,10 und 0,40 m | Gleiten, Kontaktverlust, Reserven |
| T11 | Stabilität im Werkzeugeinsatz | Ziehen/Stechen 150 und 300 N auf Ebene sowie 10° längs/quer, μ 0,6 und 0,25 | zulässige Wrench, Kippen, Sättigung, Abbruch |
| T12 | Energie/Aufgabenzeit | 10 Pflanzen, je 0,5 m auseinander, alle drei Methoden | Wh/Pflanze, Zykluszeit, 10-Pflanzen-Gesamtbilanz |
| T13 | M3: Armbewegung | Ausgangspose, Ziel-/Bodenpose und Rückzug; 2 kg Werkzeug; Humanoid beide Arme | Zielabweichung, Gelenkgrenzen, Kollision, Basisstabilität |
| T14 | M4: Werkzeuglast | 100/250/500/1000 N, ±x/±y/±z auf den Roboter, Höhen 0,10/0,40 m; 2 s Vorbereitung + 2 s Rampe + 3 s Halten + 2 s Entlasten | angeforderte/erreichte Kraft, Haltezeit, Moment, Reserve, Abbruch |
| T15 | M6: identische Unkraut-Teststrecke | zehn Pflanzen, gleiche Strecke und Seeds für alle; Baseline plus getrennte Wurzel-Peak-Varianten 100/250/500/1000 N | vollständige Aufgabenfolge, Erfolg/Schaden, Wh pro Erfolg, Zeit, Fähigkeitsgrenzen |

Alle Tests protokollieren Zeit und Energie. T14 ist ein zusätzlicher nicht brechender Werkzeug-Prüfkörpertest; genaue Kraftkonvention und Abnahme siehe [M4-Physikvertrag](03-physikmodell.md#m4--erweiterte-werkzeuglasten). T15 verwendet dieselbe Zehn-Pflanzen-Sequenz wie T12 und ergänzt Anfahrt, Geländeabschnitte und den kompletten autonomen Ablauf. Die spätere Streckendatei wird vor den Auswertungsläufen einmalig versioniert und für alle Konzepte unverändert geladen; die heutige 6 × 4 m Browserdemo ist diese Strecke noch nicht. Für T08/T10/T11 zunächst standardisierter Prüfkörper ohne Stängelbruch: Er isoliert Mechanik/Stabilität. Danach dieselben vorgesehenen Fälle mit Pflanzenmodell; T09 und T12 sind End-to-End-Tests. Methoden-Erfolg und vollständige Wurzelentfernung getrennt bewerten.

## Durchführung und Abbruch

1. **A: Physikprüfstände** gemäß Physikdokument, einschließlich gesperrter Basis zur isolierten Werkzeugcharakterisierung; diese Ergebnisse nie als autonome Leistungswerte führen.
2. **B: Mechanik mit Oracle-Zielpose**, alle T01–T11 auf nominellen Sensoren. Frei stehender Roboter, keine unsichtbaren Stützen.
3. **C: Wahrnehmung und Autonomie**, T06–T12 mit sichtbaren Pflanzen, ohne Wurzelparameterwissen. Identische Szenen-Seeds und eingefrorene Softwareparameter nach einer getrennten Tuningphase.
4. **D: Robustheit**, Rauschen, Latenz und Parameterunsicherheit jeweils einzeln, danach Kombination aus 10° Hang, μ 0,25 und 150 N Last.

Jede explizite Stufenkombination einer Tabellenzeile ist ein Fall; gemeinsame nominale Bedingungen für alle nicht variierten Parameter. T12 hat je einen Block pro Methode, die Pflanzen nutzen zyklisch 25/75/150 N, die zehnte 75 N. 300 N separat als Grenzblock. Kein vollständiges Kreuzprodukt aller Tests; T11 und D definieren die relevanten Kombinationen.

10 feste Entwicklungsseeds (0–9), danach 30 unabhängige, vorher festgelegte Auswertungsseeds (100–129) pro Fall und Konzept. Pro Seed: Zielposition ±20 mm, Wurzelpeak ±10 %, Startgier ±2° gleichverteilt; denselben realisierten Zustand für alle drei speichern. In reinen Kalibrierprüfständen keine Zufallsvariation. Auch die expliziten T14-Prüfkörperkräfte bleiben exakt 100/250/500/1000 N: Die Pflanzen-Wurzelvariation von ±10 % wird dort nicht angewandt. Für die zusätzlichen T15-Lastvarianten bleiben die namensgebenden Wurzel-Peaks ebenfalls exakt; Zielposition/Startgier können weiterhin anhand derselben Seeds variieren. Reihenfolge der Konzepte je Seed rotieren; gleiche CPU-/GPU-Budgets und Versionsstände verwenden. Zusätzliche Wiederholung desselben Seeds prüft technische Reproduzierbarkeit, ersetzt keine unabhängige Stichprobe.

Zeit beginnt mit Aufgabenannahme nach Szenenbereitschaft, umfasst Anfahrt, Erkennung, Planung, Stabilisierung, Werkzeugwechselzeit (vorläufig pauschal 15 s, keine freie Instantanumschaltung), Eingriff, Erfolgskontrolle und Ablage. Ende bei bestätigtem Resultat oder Abbruch. Timeout 120 s pro Pflanze, 1.200 s für T12, höchstens zwei Werkzeugversuche pro Pflanze. Laden und Simulatorstart nicht Teil der Aufgabenzeit; Wandzeit und Echtzeitfaktor separat erfassen.

Abbruch: Überschreiten eines Moment-/Kraftlimits, unzulässige Kontaktlösung, Roll/Pitch >30° relativ lokaler Bodenebene, Körper-Bodenkollision, Nutzpflanzenkontakt, Greifverlust, fehlender Fortschritt für 10 s oder Timeout. Bei Grenzreserve zunächst Werkzeug entlasten und sichere Pose anfordern; tatsächliche Stürze bleiben Fehler. Der Schätzer-Watchdog stoppt bei Datenalter >0,2 s; die geplanten 0,5-s-Ausfälle müssen diesen Pfad auslösen. Reales Not-Aus ist später getrennt zu entwickeln.

## Reproduzierbare Laufakte

Jeder Lauf speichert Konzept-/Szenariokonfiguration, Seed und tatsächlich gezogene Parameter, Git-Revision plus Dirty-Diff, Paketversionen, Engine, Solver, Schrittweite, Rechnerprofil, Controllerparameter, Simulations- und Wandzeiten. ROS-Bag für Sensordaten, TF, Aktionen und Zustände; separater Physiktakt-Export für Spitzenkräfte/Kontakte; kompakte Ergebnistabelle gemäß Messgrößendokument. Kein stilles Entfernen gescheiterter Läufe. Modell- oder Regleränderung erzeugt neue Batch-ID.

## Standortergänzung Kirchwerder

Die [Einsatzanforderungen](12-einsatzgebiet-kirchwerder.md) ergänzen M2–M6 um Kulturreihen mit 62/75 cm Abstand, ein Kettenlaufwerk mit 65–75 cm Spurweite zwischen den Kettenmitten (Kettenbreite/Fahranordnung noch offen) und wiederkehrende Flächenpflege. Standortbodenparameter sind noch nicht gemessen; bestehende Reibwerte bleiben synthetisch. Die heutigen Testwelten erfüllen diese Ergänzungen noch nicht.
