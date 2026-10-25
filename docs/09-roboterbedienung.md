# Raupe bedienen

Die Browserseite steuert **eine** Raupe. Die große 3D-Ansicht zeigt die Gazebo-Position. Sie berechnet keine eigene Bewegung.

## Ansichten

- **Feldfahrt:** fünf Kartoffelreihen mit 62 cm Abstand. Kleine Erdkrümel, Unkraut und Kartoffelkraut sind sichtbar, aber nicht als starre Fahrhindernisse wirksam. Die Dämme sind feste Kollisionskörper.
- **Hindernisse:** technische Stufen und Rampen mit festen Kollisionskörpern. Diese Ansicht prüft das Fahrwerk unabhängig von Pflanzenvisuals.
- **Werkzeug:** bekannter Pflanzenprüfstand für Arm, Greifer, 100-N-Lastprobe und Prüfzyklus. Dies ist noch keine autonome Erkennung.

## Fahren

Vorwärts, rückwärts und drehen: die entsprechende Taste gedrückt halten oder Pfeiltasten/WASD nutzen. Stopp oder Leertaste hält an. `Um 180° drehen` führt einen begrenzten Drehauftrag aus. Bei Fokusverlust oder ausbleibendem Bedien-Heartbeat stoppt der Befehl. `Pause` hält Gazebo an; `Zum Start zurück` lädt dieselbe Welt erneut.

**Arbeit** fährt vorwärts mit 0,28 m/s und rückwärts mit 0,22 m/s. **Fahrt** fährt vorwärts mit 1,0 m/s (3,6 km/h) und rückwärts mit 0,6 m/s. Der Modus lässt sich nur bei stehendem Fahrbefehl umschalten. Im Werkzeugprüfstand ist Fahrt gesperrt; während eines Werkzeugzyklus ist jede Fahrt gesperrt. Ein Szenenwechsel setzt den Modus auf Arbeit zurück. Die Werte sind Sollgeschwindigkeiten für Gazebo und noch keine Auslegung eines realen Antriebs.

Beim Stopp aus 1,0 m/s braucht das aktuelle Gazebo-Modell auf der ebenen Kartoffel-Testfläche etwa **0,43 m Nachlauf**. „Stopp“ setzt den Sollbefehl sofort auf null, nicht die physikalische Geschwindigkeit. Die Feldwelt hat nun einen 20 × 6 m großen kollidierenden Boden; der bepflanzte Prüfabschnitt ist kürzer. Die gemessenen Geschwindigkeiten und der Nachlauf lassen sich mit `python3 tests/check_speed_modes.py --url http://127.0.0.1:8088` erneut prüfen. Die Messung ist keine Freigabe für Fahrt in Pflanzennähe.

Die Statusanzeige meldet die Gazebo-Verbindung. Simulationszeit, Richtung und Neigung stammen aus der Gazebo-Telemetrie. Die Kamera lässt sich mit der Maus drehen und zurücksetzen; `Kamera folgt der Raupe` kann abgewählt werden.

## Grenzen

Die Raupe ist noch ein Mehrrollen-Ersatzmodell. Die Kettenhülle ist visuell. Die Kartoffelpflanzen haben in der Feldfahrt noch kein Biege- oder Schadensmodell. Der separate Werkzeugprüfstand besitzt ein definiertes Pflanzen-/Widerstandsmodell. Für reale Hardware bleiben Motortreiber, Sensoradapter, Watchdog und Kalibrierung offen.
