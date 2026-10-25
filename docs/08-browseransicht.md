# Browseransicht der Feldraupe

Die Oberfläche unter **http://10.10.10.50:8088** zeigt genau eine Raupe. Die drei Ansichten „Feldfahrt“, „Hindernisse“ und „Werkzeug“ laden jeweils eine Gazebo-Testwelt. Die Darstellung im Browser berechnet keine eigene Physik.

## Bedienung

- Fahrknopf oder Pfeiltaste/WASD gedrückt halten; Loslassen, Fokusverlust und Stopp halten die Raupe an.
- „Um 180° drehen“, „Pause“ und „Zum Start zurück“ wirken auf die Gazebo-Simulation.
- Mausziehen dreht die Kamera, das Mausrad zoomt; „Ansicht zurücksetzen“ stellt die Ausgangsperspektive wieder her.
- „Werkzeug“ zeigt den Arm sowie die Versuche mit bekannter Pflanzenpose und 100-N-Last.

Feldpflanzen und kleine Erdkrümel sind sichtbar, aber keine starren Hindernisse. Erdwall und Prüfhindernisse bleiben kollidierende Gazebo-Körper. Der getrennte Pflanzentest verwendet einen kraftbehafteten Prüfstängel. [Ursache und Korrektur](21-kartoffelreihe-kontaktkorrektur.md).

## Betrieb

```bash
cd /opt/containers/codex-work/robo
bash scripts/start-browser.sh --host 10.10.10.50 --port 8088 --world-profile potato_ridge --seed 0 --ros-domain-id 174 --log-dir /tmp
```

Strg+C beendet Server und zugehörige Gazebo-Prozesse. Vor einem Neustart die alte Instanz stoppen, damit nur ein Server auf Port 8088 läuft. Die tatsächliche Verfügbarkeit ist jeweils über `curl http://10.10.10.50:8088/api/state` zu prüfen.
