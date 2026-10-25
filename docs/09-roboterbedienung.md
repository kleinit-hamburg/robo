# Raupe bedienen

Die Browserseite steuert **eine** Raupe. Die große 3D-Ansicht zeigt die Gazebo-Position. Sie berechnet keine eigene Bewegung.

## Ansichten

- **Feldfahrt:** fünf Kartoffelreihen mit 62 cm Abstand. Kleine Erdkrümel, Unkraut und Kartoffelkraut sind sichtbar, aber nicht als starre Fahrhindernisse wirksam. Die Dämme sind feste Kollisionskörper.
- **Hindernisse:** technische Stufen und Rampen mit festen Kollisionskörpern. Diese Ansicht prüft das Fahrwerk unabhängig von Pflanzenvisuals.
- **Werkzeug:** bekannter Pflanzenprüfstand für Arm, Greifer, 100-N-Lastprobe und Prüfzyklus. Dies ist noch keine autonome Erkennung.

## Fahren

Vorwärts, rückwärts und drehen: die entsprechende Taste gedrückt halten oder Pfeiltasten/WASD nutzen. Stopp oder Leertaste hält an. `Um 180° drehen` führt einen begrenzten Drehauftrag aus. Bei Fokusverlust oder ausbleibendem Bedien-Heartbeat stoppt der Befehl. `Pause` hält Gazebo an; `Zum Start zurück` lädt dieselbe Welt erneut.

Die Statusanzeige meldet die Gazebo-Verbindung. Simulationszeit, Richtung und Neigung stammen aus der Gazebo-Telemetrie. Die Kamera lässt sich mit der Maus drehen und zurücksetzen; `Kamera folgt der Raupe` kann abgewählt werden.

## Grenzen

Die Raupe ist noch ein Mehrrollen-Ersatzmodell. Die Kettenhülle ist visuell. Die Kartoffelpflanzen haben in der Feldfahrt noch kein Biege- oder Schadensmodell. Der separate Werkzeugprüfstand besitzt ein definiertes Pflanzen-/Widerstandsmodell. Für reale Hardware bleiben Motortreiber, Sensoradapter, Watchdog und Kalibrierung offen.
