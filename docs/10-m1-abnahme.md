# M1-Prüfung: Fahrfunktionen nachgewiesen, Serienabnahme offen

> Historischer Fehlbericht vor dem direkten ROS-Adapter. Eine spätere Serie bestand 10/10 Durchläufe einschließlich Sensorfehlerprüfung: [aktueller Nachweis](13-grundfunktionen.md). Die folgenden Befunde bleiben unverändert erhalten.

Stand: 2026-09-07. **M1 ist noch nicht freigegeben.** Fahrfunktionen des Ketten-Ersatzmodells haben mehrfach die Grenzwerte eingehalten; keine der vier angeforderten Zehnerserien wurde vollständig bestanden. Wiederholte Simulator-/Bridge-Neustarts liefern nicht zuverlässig alle Messdaten. Quadruped/Humanoid haben weiterhin keine Gangregler; M2–M6 sind nicht abgenommen.

## Durchgeführte Serien

| Serie | Bestandene Fahrdurchläufe | Weitere Ergebnisse | Abnahme |
|---|---:|---|---|
| 1 | 9 von 10 angeforderten | zehnter Start nach 20 s nicht bereit | nein |
| 2 | 5 von 10 angeforderten | ein Fahrfehler durch `heading_timeout`, ein Startfehler, drei ungeprüft | nein |
| 3 | 8 von 10 angeforderten | neunter Start ohne IMU, zehnter ungeprüft | nein |
| 4 | 1 von 10 angeforderten | zweiter Start ohne Daten, acht ungeprüft | nein |

Die Serien werden weder zusammengerechnet noch erfolglose Läufe entfernt. Daten: [Serie 1](validation/m1-attempt-1-summary.json), [Serie 2](validation/m1-attempt-2-summary.json), [Serie 3](validation/m1-attempt-3-summary.json), [Serie 4](validation/m1-attempt-4-summary.json). Die erste Zusammenfassung wurde nach dem ungefangenen Startfehler aus den erhaltenen Einzelresultaten und dem Terminal-Traceback rekonstruiert; dies ist dort vermerkt. Spätere Teststände exportieren auch Startfehler.

## Bedingungen und Messverfahren

Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic 8.11.0. Ebene Welt ohne Rampe, Pflanzen oder Hindernisse, Boden μ = μ₂ = 0,6. 65-kg-Modell mit zwei angetriebenen Rädern und vier passiven Stützpunkten. Ideale simulierte IMU ohne Rauschen. Seed steigt je frisch geladener Welt ab null; bei diesem rauschfreien Modell verändert er keine Geländeparameter. Testinstanz: localhost:8089, ROS-Domain 175, eigene Gazebo-Partition. Die Benutzeransicht bleibt auf Port 8088 / Domain 174 getrennt.

Pro Fahrdurchlauf: 1 m vorwärts/rückwärts (Fehler ≤0,10 m), 90° links/rechts und 180° wenden (Fehler ≤5°), Stopp aus 0,15 ±0,02 m/s (Nachlauf ≤0,10 m), ausbleibender Heartbeat (erkannter Stopp ≤0,8 s Wandzeit), Körperlage und Radgeschwindigkeiten. Ground-Truth-Körperposen werden nur zur Ergebnismessung genutzt. Die 1-m-Aufträge sind zeitlich begrenzte Geschwindigkeitsbefehle, keine autonome Navigation. Für 90° beendet das Skript die simulierte Bedienung IMU-geführt; 180° verwendet den eingebauten Drehregler. Messungen sind diskret und keine Vorhersage realer Millimetergenauigkeit.

## Befunde und Änderungen

Die IMU-Prüfung verwirft alte Zeitstempel, ungültige Quaternionen und nicht verfügbare Orientierung. Neue Radgelenk-Telemetrie erfasst Geschwindigkeiten; eine Momenten-/Energievalidierung folgt daraus nicht. Acht Unit-Tests bestanden.

Serie 2 zeigte frische Körper-/Gelenkdaten, aber Simulationszeit null und 866 verworfene IMUs. Die Bridge wurde daher auf Gazebo `/world/garden_preview/clock` mit ROS-Remapping nach `/clock` umgestellt. Der allgemeine Gazebo-Kanal kann unter bestimmten Startbedingungen entfallen, wie die [offizielle Jazzy-Bridge-Dokumentation](https://docs.ros.org/en/ros2_packages/jazzy/api/ros_gz_bridge/index.html) beschreibt. Das erklärt einen möglichen Mechanismus, beweist jedoch nicht alle internen Ursachen dieser Versuche. Die Uhrkorrektur beseitigte nicht die gesamte Neustartinstabilität: Serie 3 fehlte später die IMU trotz laufender Uhr.

Bridge und Simulator werden beim Weltwechsel gemeinsam erneuert. Der zusätzliche Versuch mit einer neuen Gazebo-Partition pro Weltstart (Serie 4) war ebenfalls erfolglos und wurde zurückgenommen. Die endgültige Partition bleibt pro Browserprozess getrennt. Die Logs von Serie 3 und 4 enthalten native Segmentation Faults, unter anderem beim Gazebo-Abbau und in der Transport-Discovery. Ihre zeitliche/kausale Zuordnung zu den fehlenden Kanälen ist noch nicht vollständig geklärt. Während eines Sensor-Stopps in Serie 2 lief außerdem der separate Browser-Test; ein Lastzusammenhang ist nicht bewiesen. Watchdog-Grenzen wurden nicht gelockert.

## Abschließende Funktionsprüfung

Nach Rücknahme der erfolglosen Partitionserneuerung wurde ein einzelner Fahrdurchlauf plus Sensorfehler-Test ausgeführt: **1 von 1 Fahrdurchläufen bestanden**, Sensorfehler-Prüfung **True**. Das ist ausdrücklich keine Wiederholung oder Freigabe der Zehner-Abnahme. [Ergebnis](validation/m1-final-function-summary.json), [Quellmanifest](validation/m1-final-function-manifest.json).

Sensorfehler-Test: Physik direkt pausieren, um frische IMU-Nachrichten zu unterbrechen; dann veraltete IMUs bei weiterlaufendem Bedien-Heartbeat einspeisen. Gemeldeter Stoppgrund: `heading_timeout`, Latenz: 0.5165627889800817 s, verworfene Nachrichten: 51. Nach Fortsetzen wird geprüft, dass die Fahrt nicht selbsttätig wieder anläuft. Der erste Fehlerinjektionsversuch stoppte bereits mit `command_timeout` und war kein gültiger Sensornachweis ([erhaltenes Ergebnis](validation/m1-fault-first-summary.json)). Das Testskript wartet jetzt auf einen bestätigten IMU-Abonnenten in der explizit gewählten ROS-Domain und hält den Bedien-Heartbeat auch während des blockierenden Pause-Aufrufs aufrecht. Die Stopplatenz wird ab dem letzten beobachteten Fortschritt der Simulationsuhr gemessen; die Abfrageauflösung beträgt ungefähr 25 ms zuzüglich HTTP-Zeit. Der obige Ergebnisdatensatz stammt aus dieser korrigierten Prüfung.

Die Browserprüfung nach der ersten Bridge-Änderung bestand Halten/Loslassen, Fokusverlust, Modellwechsel, Gang-Sperre, Pause und Mobilansicht. Die abschließende Wiederholung am finalen Backend erreichte jedoch schon die Fahrbereitschaft nach 20 s nicht und ist **fehlgeschlagen**: [Testausgabe](validation/m1-browser.txt). Eine Browserfreigabe des finalen Backendstands wird daher nicht behauptet. Die laufende Benutzerinstanz wurde während der Tests nicht auf den geänderten Backendstand neu gestartet; dieser wird beim nächsten Dienststart geladen.

## Offene Arbeit vor Freigabe

Den fehlenden Datenkanal beim Weltwechsel auf Gazebo- und ROS-Seite getrennt erfassen, native Start-/Abbaufehler reproduzieren und beheben. Danach zehn vollständige Läufe des finalen Stands mit unveränderten Kriterien ausführen. Bis dahin bleibt M1 beim Ketten-Ersatzmodell teilweise umgesetzt; M2 erhält keine vorgezogene Freigabe.

Sichtbare Ketten und Arme sind starre Geometrie. Keine validierten Kettenkontakte, Antriebsmomente, Werkzeugkräfte, Gelände-/Greifversuche oder Energiekennwerte. Beinkonzepte sind statische Vorschauen. Keine Hardwarebeschaffung.

## Reproduzieren

```bash
source /opt/ros/jazzy/setup.bash
python3 -m unittest discover -s tests -v
python3 tests/accept_m1_tracked.py --runs 10 --output results/m1-neuer-lauf
```

Ausgabeordner neu, Port 8089 und ROS-Domain 175 frei halten. Das Skript startet und beendet die eigene Testinstanz. Lokale Laufakten unter `results/` enthalten JSONL-Zeitreihen, Einzelmetriken, Quellkopien und Logs. Kleine Ergebnisse, Quellmanifeste und SHA-256-Dateilisten stehen unter `docs/validation/`. Es gab zum Testzeitpunkt noch keinen Git-Commit; die gesicherten Quellkopien und Prüfsummen identifizieren den Stand. Die Planung wurde danach um diesen Prüfstatus ergänzt.
