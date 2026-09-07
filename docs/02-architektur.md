# Gemeinsame ROS-Architektur

## Trennung von Aufgabe, Regelung und Umgebung

Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic ist der feste Zielstack; die bestätigten Integrationswege stehen in den [Quellennotizen](research/technische-grundlagen.md). Hier beschriebene Pakete und eigene Interfaces sind **geplant**, nicht implementiert.

Datenfluss:

```text
Sensoren → Wahrnehmung → Pflanzenkarte → Aufgabensteuerung
                 ↓                 ↓
           Zustandsschätzung → Anfahrt / Ganzkörperplanung
                                   ↓
                        Arm- und Werkzeugregelung
                                   ↓
                         ros2_control-Controller
                                   ↓
             gz_ros2_control ODER reale Hardware-Interfaces

Gazebo → eigener Pflanzen-/Lastmodell-Systemplugin → Benchmark-Auswertung
Sensorbrücke ros_gz_bridge → gemeinsame ROS-Sensortopics
```

`garden_perception` erkennt Pflanze, Klasse (Unkraut/Nutzpflanze/unbekannt), Pose, Ausdehnung und Unsicherheit. Unbekannte Pflanzen werden nicht bearbeitet. `garden_task_manager` wählt Schneiden, Abstechen oder Ziehen anhand konfigurierter Regeln, beobachtbarer Pose und gemessener Kraft. Er erhält niemals die verdeckte Wurzelstärke aus dem Simulator. Nach einem begrenzten Zugversuch kann er lösen und die Methode wechseln; maximal zwei Werkzeugversuche pro Pflanze.

`garden_state_estimation` fusioniert IMU, Gelenke und visuelle/Lidar-Odometrie; beinspezifische Kontaktinformationen über Adapter. `garden_navigation` gibt gemeinsame Zielposen vor. Kette verwendet eine mobile Basisregelung; Beine benötigen separate Fußschritt- und Ganzkörperregler. Nav2 kann Aufgaben und Anfahrt unterstützen, ersetzt aber keine Balance- oder Fußschrittplanung. MoveIt 2 ist eine Option für kollisionsfreie Armbewegungen, kein fertiger kraftgeregelter Unkrautlöser.

`garden_manipulation` nutzt freie Positionierung bis kurz vor Kontakt, anschließend begrenzte kartesische Impedanz/Admittanz mit Kraftüberwachung. `garden_tool_controller` begrenzt Klemmkraft, Schnittkraft und Stechhub. `garden_stability_monitor` prüft Kontakt-, Reib- und Gelenkreserven. `garden_safety_supervisor` stoppt bei Überlast, Verlust der Schätzung oder Kommunikationsausfall. Hardwareunabhängige Nodes hängen ausschließlich an ROS-Verträgen.

## Schnittstellenvertrag

| Zweck | Geplantes ROS-Interface | Vertrag |
|---|---|---|
| Kamera | `sensor_msgs/Image`, `CameraInfo`, optional `PointCloud2` | Zeitstempel, optische Frames, Kalibrierung; SensorDataQoS |
| Zustand | `sensor_msgs/Imu`, `JointState`, `nav_msgs/Odometry`, TF | SI-Einheiten; keine Simulator-Ground-Truth als reale Odometrie |
| Werkzeugwrench | `geometry_msgs/WrenchStamped` | im `tool_frame`, positive z-Achse nach Definition des Werkzeugs; für Auswertung nach Welt transformieren |
| Batterie | `sensor_msgs/BatteryState` | Quelle real/gemodelt kennzeichnen |
| Armbewegung | `control_msgs/action/FollowJointTrajectory` | konzeptspezifische Gelenkliste hinter gemeinsamem Aufgabenadapter |
| Greifer | `control_msgs/action/GripperCommand` | Öffnungsweg in m; Kraftkonvention des Adapters dokumentieren |
| Basisauftrag | eigener Action `MoveToWorkPose` | PoseStamped + Toleranz; Feedback Fortschritt/Stabilität; Ergebnis erreicht/unerreichbar/abgebrochen |
| Pflanzenerkennung | eigenes `PlantObservation` | UUID, PoseWithCovariance, Klasse, Konfidenz, Ausdehnung, Beobachtungszeit |
| Werkzeugauftrag | eigene Action `TreatPlant` | UUID, Methode, Kraft-/Weglimits; Feedback Phase/Kraft; Ergebnis und Abbruchgrund |
| Kontrollfreigabe | eigenes `OperationState` | bereit/anfahren/ausrichten/kontakt/arbeiten/pruefen/abbruch; monotone Zustandsfolge je Versuch |

Eigene Nachrichtendefinitionen werden in `garden_interfaces` konkretisiert. Goals sind abbrechbar und zeitlich begrenzt. Keine rohen Gazebo-Entity-IDs in produktiven Interfaces. Gemeinsamer TF-Vertrag `map → odom → base_link → ... → tool_frame`, Sensoren mit eigenen Frames; Basis x vorwärts, y links, z oben. Beim Humanoiden `left_tool_frame` und `right_tool_frame` mit expliziter Werkzeugzuordnung. Pflanzenkarten liegen in `map`.

Simulationszeit über genau eine `/clock`-Quelle, `use_sim_time=true` auf allen Sim-Nodes; real false. Sensoren best effort mit kleinen Queues, Befehle/Aktionsstatus reliable. Sicherheitsstopps benötigen zusätzlich einen unabhängigen Hardware-Watchdog im späteren Prototyp; DDS allein ersetzt ihn nicht.

## Controller und Simulator

`controller_manager` lädt `joint_state_broadcaster`, Trajektoriencontroller und passende Basis-/Effort-Controller. Nicht gleichzeitig Position und Effort auf demselben Gelenk kommandieren. Kraftregelung und Ganzkörperregelung werden gesondert implementiert und geprüft; bloßes Laden von `gz_ros2_control` liefert sie nicht.

Gazebo-Sensorik wird mit expliziter `ros_gz_bridge`-Konfiguration angebunden. Gelenkzustände/-befehle laufen über ros2_control, nicht zusätzlich über eine konkurrierende Topic-Brücke. Der Pflanzenplugin wirkt direkt im Physikschritt; ROS-Latenz darf seine Federkräfte nicht bestimmen.

Geplante Raten: Physik 1.000 Hz, Gelenk-/Ganzkörperregelung 500 Hz, Werkzeugadmittanz 250 Hz, Kraftausgabe 250 Hz, IMU 200 Hz, Kamera 15 Hz, Lidar 10 Hz, Planung 10 Hz. Der interne Benchmark erfasst Kraft-/Kontaktmaxima im Physiktakt, damit ROS-Ausgabe keine Spitzen verschluckt. Diese Raten sind Budgetziele und werden unter Last überprüft.

## Übergang zum realen Prototyp

URDF/Xacro beschreibt einfache Links, Gelenke, Trägheiten, Limits, TF und ros2_control. SDF beschreibt Welt, Kontakt und Simulationsplugins. Gemeinsame Parameterquelle vermeidet auseinanderlaufende Massen. Hardware wird durch `hardware_interface::SystemInterface`/Sensor-Interfaces angebunden; derselbe `controller_manager` und dieselben Aufgaben-/Wahrnehmungs-Nodes bleiben.

Austauschbar: Simulationssensoren gegen Treiber, Gazebo-Joint-System gegen Motorbus, simulierte Batterie gegen BMS-Messung. Neu zu kalibrieren: Trägheiten, Reibung, Kraftsensorbias, Kameras, Gelenk-Offsets, thermische Grenzen und Latenzen. Reglergewinne sind nicht ungeprüft übertragbar. Kettenplugin-Befehle dürfen nur hinter dem Basisadapter liegen, sonst entsteht eine simulatorgebundene Antriebsarchitektur.

Ground Truth erscheint ausschließlich unter `/benchmark/ground_truth/*`; die Auswertung konsumiert es, autonome Produkt-Nodes nicht. Ein ausdrücklich markierter Oracle-Modus isoliert Mechaniktests von Erkennungsfehlern; seine Ergebnisse werden nicht mit vollständiger Autonomie vermischt.
