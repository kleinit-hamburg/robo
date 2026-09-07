# Lokale Browseransicht

**Aktueller Stand:** Die Startansicht wurde auf austauschbare Roboter und Fahrbefehle umgestellt. Siehe [Roboterbedienung](09-roboterbedienung.md). Adresse und Start-/Stopp-Anleitung unten gelten weiterhin; die Beschreibung des Falltests dokumentiert die vorherige Ausbaustufe.

Die erste sichtbare Testszene ist unter **http://10.10.10.50:8088** im VM-Netz erreichbar. Dies wurde auf der VM mit Chromium geprüft; der Zugriff vom persönlichen Rechner hängt von dessen Netzwerkzugang zur VM ab.

## Bedienung

- Mit linker Maustaste ziehen: Kamera drehen; Mausrad: zoomen; rechte Maustaste ziehen: verschieben.
- Pause/Fortsetzen steuert die tatsächliche Gazebo-Simulation.
- „Falltest neu starten“ lädt die kleine Testwelt erneut: Würfel fällt, Kugel rollt über die Rampe.
- „Kamera zurücksetzen“ stellt die Ausgangsperspektive wieder her.
- Zeit und Objektpositionen stammen aus Gazebo; Verbindungsausfall wird angezeigt.

Die Szene enthält ein 6 × 4 m Testfeld, eine Rampe, eine Stufe, zwei bewegliche Prüfkörper und starre Pflanzenplatzhalter. Sie ist **keines der drei Roboterkonzepte** und noch nicht die gemeinsame Benchmarkwelt. Die Einfassung verhindert, dass die Kugel aus dem Testfeld rollt.

## Umsetzung

`worlds/browser-preview.sdf` enthält Physik, Primitive, Farben, Massen und PosePublisher. Gazebo Harmonic/DART läuft ohne Rendering auf der VM. `ros_gz_bridge` übersetzt `/clock` sowie die benannten Modellposen von `Pose_V` nach `TFMessage` auf zwei expliziten Topics. `scripts/browser_server.py` liest diese Daten mit rclpy und stellt eine kleine HTTP-API bereit. Der Browser rendert mit Three.js 0.180.0. Alle Browserassets werden lokal ausgeliefert; keine CDN-Abhängigkeit zur Laufzeit.

Diese Ansicht ist eine projektspezifische Alternative zum [offiziellen Gazebo-Webviewer](https://gazebosim.org/docs/harmonic/web_visualization/), dessen zusätzlicher `gz launch`-Websocket-Server in der installierten ROS-Vendor-Variante nicht vorhanden ist. Sie ist kein vollständiger SDF-Viewer: Der Geometrieimport unterstützt nur die hier verwendeten Modelle mit einem Link, einem Visual und Box/Sphere/Cylinder. Meshes, verschachtelte Modelle und Roboterkinematiken müssen später ergänzt werden. Statische Modellposen werden aus der SDF gelesen, dynamische aus ROS.

[PosePublisher](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html) wird mit 20 Hz verwendet. Das allgemeine SceneBroadcaster-Pose-Topic liefert in der getesteten Bridge leere TF-Frame-Namen; deshalb erhält jeder bewegliche Prüfkörper einen eigenen Publisher. Im getesteten Harmonic-Stand blieben nach `reset: {all: true}` neue Pose-Nachrichten aus. Der Neustart-Button beendet deshalb ausschließlich den Gazebo-Prozess dieser Demo und startet ihn neu, während HTTP-Server und ROS-Bridge weiterlaufen. Kurzzeitig unterbrochene Daten während dieses Neustarts werden sichtbar gemeldet.

Die Viewerdaten sind Simulator-Ground-Truth für die Anzeige und werden nicht an autonome Produkt-Nodes weitergegeben. Eigene Gazebo-Partition pro Serverprozess, ROS-Domain 174, DDS-Discovery auf localhost begrenzt. HTTP bindet standardmäßig nur localhost; die laufende Instanz wurde ausdrücklich an die interne VM-IP 10.10.10.50 gebunden. Kein Internet-Portforwarding eingerichtet. Die Demo hat keine Benutzeranmeldung und ist nur für das vertrauenswürdige Entwicklungsnetz vorgesehen. POST-Kommandos sind auf Pause, Fortsetzen und Neustart beschränkt und prüfen Same-Origin.

## Starten und stoppen

Einmalige lokale JavaScript-Abhängigkeit:

```bash
cd /opt/containers/codex-work/robo
npm ci --prefix web --ignore-scripts --no-audit --no-fund
```

Manuell im Vordergrund (Strg+C beendet auch die zugehörigen Simulationsprozesse):

```bash
bash scripts/start-browser.sh --host 10.10.10.50 --port 8088
```

Die aktuell laufende Instanz ist ein temporärer systemd-Benutzerdienst:

```bash
systemctl --user status garden-viewer
systemctl --user stop garden-viewer
systemctl --user restart garden-viewer
```

Nach einem VM-Neustart den temporären Dienst erneut anlegen:

```bash
systemd-run --user --unit=garden-viewer \
  --description='Gazebo Garten Browseransicht' \
  --property=WorkingDirectory=/opt/containers/codex-work/robo \
  /bin/bash /opt/containers/codex-work/robo/scripts/start-browser.sh \
  --host 10.10.10.50
```

Nicht gleichzeitig Vordergrund und Dienst auf demselben Port starten. Kein dauerhafter Autostart eingerichtet. Logs: `journalctl --user -u garden-viewer`, `/tmp/garden-viewer-gazebo.log`, `/tmp/garden-viewer-bridge.log`.

## Prüfung am 2026-09-07

- Chromium-Browsertest mit WebGL-Software-Rendering: Seite und 3D-Szene geladen, keine JavaScript-Ausnahmen.
- Echte Live-Positionen: Fallwürfel ruht nach Neustart bei z = 0,12499988 m; erwartet 0,125 m bei 25 cm Kantenlänge.
- Pause hält die Simulationszeit mindestens 3,5 s konstant; Verbindung bleibt als pausiert erkennbar.
- Fortsetzen lässt die Simulationszeit wieder steigen.
- Desktop 1440 × 980 und Mobilansicht 390 × 844 geprüft; kein horizontaler Seitenüberlauf; Screenshots visuell geprüft.
- Temporärer Test und Screenshots unter `/tmp/garden-browser-test/`; kein dauerhaftes Benchmark-Ergebnis.

Das beweist Browser-Rendering auf der Prüfmaschine, nicht GPU-Kamerasimulation in Gazebo. Darstellung auf dem persönlichen Browser und Netzwerkzugang sind dort noch zu bestätigen.
