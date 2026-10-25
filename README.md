# Gartenlabor: virtueller Raupenroboter

Dieses Repository entwickelt **eine** Raupe für die spätere Unkrautpflege in Kartoffelreihen. Entwicklungsplattform sind Ubuntu 24.04, ROS 2 Jazzy und Gazebo Harmonic. Gazebo berechnet die Bewegung und Kontakte; die Browserseite zeigt den Zustand und sendet manuelle Befehle. Es gibt noch keine autonome Pflanzenerkennung, Navigation oder reale Hardware.

## Aktueller Stand

- Aktive Browserkonfiguration: `tracked_overrow_belt08`, 62 cm Spurweite zwischen den Kettenmitten, 8 cm Kettenbreite und 48 cm nominelle Unterbodenfreiheit. Das Fahrwerk ist ein gefedertes Mehrrollen-Ersatzmodell; die sichtbare Kettenhülle hat noch keine eigenen physikalischen Kontakte.
- Die Kartoffelwelt zeigt fünf Reihen mit 62 cm Abstand und etwa 15 cm hohen Dämmen. Pflanzen und kleine Erdkrümel sind dort **nur Visuals**, bis ein nachgiebiges Kraft-/Schadensmodell existiert. Die Dämme behalten Kollisionsgeometrie. Feste Stufen und Rampen liegen ausschließlich in der separaten Hindernisprüfung.
- Die Bedienseite bietet Feldfahrt, Hindernisprüfung und Werkzeugprüfung. Arm und Greifer stehen im getrennten Werkzeugprofil zur Verfügung. Der Nutzer kann weder Roboter noch mechanische Parameter in der Browserseite wechseln.
- Zwei Bedienmodi: Arbeit mit 0,28 m/s und Fahrt mit 1,0 m/s vorwärts. Der schnelle Modus ist im Werkzeugprüfstand gesperrt. Der Bremsweg aus 1,0 m/s beträgt im aktuellen Feldtest etwa 0,43 m. Die kollidierende Feldfläche wurde dafür auf 20 × 6 m erweitert.
- Die hoch aufgesetzte Armattrappe ist aus der Feldraupe entfernt. Zwei bodennahe Werkzeugplätze vor den Ketten zeigen die geplante Arbeitszone; sie sind noch reine Visuals ohne Gelenk- oder Werkzeugkräfte. Der bisherige bewegliche Arm bleibt ausschließlich im isolierten Pflanzenprüfstand.
- Die Modelle und Berechnungen bleiben vorläufig. Die realen Kennwerte des schweren Marschbodens in Kirchwerder sind nicht kalibriert. Historische Raupenversuche sind keine Freigabe der aktuellen Feldraupe.

## Starten

```bash
scripts/start-browser.sh --host 10.10.10.50 --port 8088 --world-profile potato_ridge --ros-domain-id 174 --log-dir /tmp
```

Danach im Browser `http://10.10.10.50:8088` öffnen. Das Startskript erstellt den Gazebo-Adapter und startet genau eine lokale Web-/Gazebo-Instanz. Mit `Ctrl+C` stoppen. Die drei Ansichten wechseln die Gazebo-Testwelt, nicht die Roboterkonstruktion.

## Technische Unterlagen

- [Bedienung](docs/09-roboterbedienung.md)
- [Ursache des Hängenbleibens und Gegenversuch](docs/21-kartoffelreihe-kontaktkorrektur.md)
- [Zentrale Roboterspezifikation](config/robot-spec.json) und [Modellgenerator](scripts/build_preview_models.py)
- [Fahrwerks- und Hindernistests](docs/15-fahrwerk-testsystem.md)
- [Vorbemessung von Schwerpunkt, Antrieb, Werkzeug und Akku](docs/20-raupe-antrieb-werkzeug-energie.md)
- [Mechanische Spurverstellung und Werkzeuganordnung](docs/23-spur-und-werkzeuganordnung.md)
- [ROS-Architektur](docs/02-architektur.md) und [Physikmodell](docs/03-physikmodell.md)

Frühere Raupenvarianten und deren Messwerte bleiben als technische Offline-Vergleichsdaten erhalten; die aktive Anwendung verwendet eine einzige Raupe. Keine Hardwarebeschaffung und kein vollständiges CAD-Modell in diesem Schritt.
