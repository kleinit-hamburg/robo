# Installation des Simulationsstacks

Stand 2026-09-07: **Installation erfolgt und grundlegende Laufzeittests bestanden.** Der Benutzer hat die Installation nach lokaler sudo-Authentifizierung ausgeführt. Anschließend wurden die installierten Pakete und die unten beschriebenen Funktionen geprüft.

## Installationsweg

[Installationsskript](../scripts/install-simulation.sh) für Ubuntu 24.04 amd64/arm64. Die vorhandenen Ubuntu-Paketquellen enthalten Universe, noble-updates und noble-backports. Die VM hatte vor Installation rund 30 GiB frei; nach Installation sind rund 25 GiB frei (Systempartition zu 67 % belegt). Die gerundete Differenz beträgt etwa 5 GiB und ist keine paketgenaue Messung.

Das Skript installiert die offizielle ROS-Paketquelle `ros2-apt-source` 1.2.0 (Noble), prüft den SHA-256-Hash und installiert ROS 2 Jazzy Desktop einschließlich RViz, Gazebo Harmonic über `ros-jazzy-ros-gz`, gz_ros2_control, Controller, Xacro und Entwicklungswerkzeuge. Es installiert weder MoveIt/Nav2 noch ein Erkennungsmodell; diese kommen bei Bedarf in späteren Projektphasen hinzu. Keine zusätzliche OSRF-Quelle nötig.

Das heruntergeladene Quellenpaket wurde vorab geprüft: Paketname `ros2-apt-source`, Version `1.2.0~noble`, Architektur `all`, SHA-256 `0804d9b13db770eb87019be414cd78378835228ad5fa801fc88758596dd8f7e5`. Das Skript lädt es in ein eigenes temporäres Verzeichnis erneut und prüft denselben Hash.

Im eigenen Terminal starten:

```bash
sudo bash /opt/containers/codex-work/robo/scripts/install-simulation.sh
```

Danach als normaler Benutzer:

```bash
source /opt/ros/jazzy/setup.bash
rosdep update --rosdistro jazzy
```

Die Installation verändert die Systempakete und ROS-Paketquellen. Es erfolgt kein pauschales Systemupgrade, kein automatisches Entfernen bestehender Pakete und keine Änderung der Shell-Startdateien. Das Skript kann nach einem Fehler erneut gestartet werden; die Installation ist nicht transaktional. Ein Fehler kann bereits installierte Teilpakete zurücklassen.

## Prüfergebnis

| Komponente | Installierte Version |
|---|---|
| ROS Jazzy Desktop | 0.11.0-1noble.20260616.084553 |
| Gazebo Sim / Harmonic | 8.11.0 |
| ros_gz | 1.0.22-1noble.20260616.074726 |
| gz_ros2_control | 1.2.19-1noble.20260615.171757 |
| ros2_controllers | 4.40.1-1noble.20260616.074625 |
| ros-dev-tools | 1.0.1 |
| CMake | 3.28.3-1build7 |

- ROS-DDS-Kommunikation: separater C++-Talker und Listener, Empfang bestätigt.
- Gazebo ohne GUI: DART-Plugin laut Log geladen, Starrkörperwelt gestartet.
- ROS-Bridge: fortlaufende `/clock` von 0,002 bis 2,003 s beobachtet.
- Gravitation/Bodenkontakt: Würfel (Kantenlänge 0,10 m, Masse 1 kg) startet mit Mittelpunkt z = 1,0 m und ruht bei z = 0,049940 m; erwartet 0,05 m, Prüftoleranz ±0,005 m.
- `ros_gz_bridge` und `gz_ros2_control` über ROS-Paketauflösung gefunden.
- Rosdep-Systemkonfiguration und Benutzer-Quellencache vorhanden; keine vollständige Abhängigkeitsauflösung eines Roboterpakets durchgeführt.

Die temporäre Prüfung verwendete eine eigene Gazebo-Partition und ROS-Domain 173 mit lokaler Discovery. Alle gestarteten Testprozesse wurden danach beendet. Temporäre Welt, Prüfskript und Logs liegen unter `/tmp/garden-sim-check/` und sind keine dauerhaft versionierten Benchmark-Artefakte.

Noch offen: grafische Oberfläche, Kamera-/GPU-Rendering, tatsächlicher Controllerbetrieb an einem Robotermodell und alle Garten-Benchmarks. Die virtuelle Bochs-Grafik garantiert keine Hardwarebeschleunigung. Der erfolgreiche Installations-Smoke-Test validiert weder Pflanzenkräfte noch die drei Roboterkonzepte.

Quellen: [offizielle ROS-Jazzy-Installationsanleitung im Quellrepository](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Installation/Ubuntu-Install-Debs.rst), [ROS-Paketquellen-Release](https://github.com/ros-infrastructure/ros-apt-source/releases/tag/1.2.0), [Gazebo mit ROS installieren](https://gazebosim.org/docs/harmonic/ros_installation/).
