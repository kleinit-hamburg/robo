# Garten-Arbeitsroboter: virtuelles Konzeptprojekt

Drei alternative Plattformen für autonome Unkrautbekämpfung: Kettenfahrzeug mit Arm, Quadruped mit Arm und humanoider Zweibeiner mit zwei Greifhänden. Zielplattform ist **Ubuntu 24.04, ROS 2 Jazzy und Gazebo Harmonic**. Andere Gartenarbeiten werden über wechselbare Werkzeuge und zusätzliche Aufgabenprogramme vorbereitet.

**Status: Architektur und Versuchsplanung; Simulationsstack installiert und grundlegender Physik-/ROS-Test bestanden. Erste manuelle Fahrvorschau des Kettenkonzepts verfügbar; noch keine autonome Gartenarbeit oder Benchmarkfreigabe.** Es gibt grobe SDF-Vorschaumodelle und eine manuelle ROS-Fahranbindung, aber noch keine detaillierte CAD-Ausarbeitung, eigenen ROS-Pakete, trainierte Erkennung oder Benchmark-Messergebnisse. Keine Hardwarebeschaffung und keine Veröffentlichung auf einem Remote-Host. Zahlen sind prüfbare Entwurfsannahmen, keine bestätigten Pflanzenkennwerte oder Leistungsversprechen.

## Lesen

1. [Drei Roboterkonzepte](docs/01-konzepte.md): Abmessungen, Kräfte, Antriebe, Sensoren, Energie, Bau- und Prototyprisiken.
2. [ROS-Architektur und Hardwareübergang](docs/02-architektur.md).
3. [Physik, Pflanzen und Werkzeuglasten](docs/03-physikmodell.md).
4. [Gemeinsame Testwelt und Testplan](docs/04-testplan.md).
5. [Messgrößen und Entscheidungsverfahren](docs/05-messgroessen.md).
6. [Repository-Struktur und Umsetzungsschritte](docs/06-umsetzung.md).
7. [Technische Primärquellen](docs/research/technische-grundlagen.md).
8. [Installation und aktueller Status](docs/07-installation.md).
9. [Live-Browseransicht](docs/08-browseransicht.md): http://10.10.10.50:8088.
10. [Roboterauswahl und Fahrbefehle](docs/09-roboterbedienung.md).
11. [M1-Prüfung: Ergebnisse und offene Neustartfehler](docs/10-m1-abnahme.md).

Die maschinenlesbaren [Konzeptparameter](config/concepts.json) und [Versuchsparameter](config/benchmark.json) sind Eingaben für die spätere Implementierung, noch keine direkt von Gazebo ladbaren Dateien. Alle numerischen Größen verwenden SI-Einheiten; Gradwerte sind ausdrücklich mit `_deg` benannt.

## Meilensteine

**M1:** Bewegen → **M2:** Gelände bewältigen → **M3:** Arm bewegen → **M4:** 100/250/500/1000 N Werkzeuglast → **M5:** virtuelle Pflanze greifen → **M6:** identische Unkraut-Teststrecke für alle drei.

M1 ist beim Ketten-Ersatzmodell teilweise umgesetzt; die Serienabnahme ist wegen unzuverlässiger Simulator-Neustarts noch offen. [Prüfbericht](docs/10-m1-abnahme.md). Gangregler, Gelände-Abnahme, Armbewegung, Werkzeuglasten, Pflanzengriff und Vergleichsstrecke sind offen. Abnahmekriterien und Status je Konzept stehen in [der Meilensteinplanung](docs/06-umsetzung.md) und [milestones.json](config/milestones.json). Die 1000-N-Stufe ist ein Grenzversuch, keine bestätigte Tragfähigkeit.

## Entwicklungsreihenfolge

Zuerst virtuelle Funktionen M1–M6, danach Referenzgröße und mechanische Auslegung, anschließend ein möglicher Druckprototyp mit Motoren, optionaler Hydraulik, LiDAR und Kamera. Vorläufige Simulationsmaße bleiben parametrierbar; Materialstärken und reale Lastgrenzen sind noch nicht festgelegt. [Funktionsumfang und Prototypplanung](docs/11-funktionen-und-prototyp.md).

## Vorläufige Entscheidung

Mit dem Kettenkonzept als Referenz beginnen: Es vereinfacht das frühe Prüfen von Pflanzeninteraktion und gemeinsamen ROS-Nodes. Quadruped und Humanoid bleiben vollwertige Vergleichskandidaten. Ihre zusätzlichen Bewegungsmöglichkeiten müssen den Aufwand für Balance, Regelung und Energie im gemeinsamen Test rechtfertigen. Das ist eine Entwicklungshypothese, kein bereits gemessenes Ranking.

Zuerst Modellannahmen einfrieren, dann einfache Kollisionskörper und Kraftprüfstände implementieren. Erst nach numerisch belastbaren Vergleichsläufen eine Plattform vertiefen. Ein verkleinerter Druckprototyp ist eine spätere Option und kein Beschaffungsauftrag.

## Konkretes Einsatzgebiet

Kirchwerder, schwerer Marschboden, ca. 4.000 m² Grundstück mit gut 2.000 m² Ackerland; davon jährlich etwa ein Drittel in Kultur. Der Roboter pflegt diese Kulturflächen; die Brache übernimmt der Nutzer mit Traktor oder anderer Landmaschine. Kartoffelreihen 62 cm, Erdbeerreihen üblicherweise 75 cm. Gewünschte verstellbare Spurweite zwischen den Kettenmitten: 65–75 cm; Kettenbreite und Fahranordnung bleiben offen. [Standortanforderungen](docs/12-einsatzgebiet-kirchwerder.md).
