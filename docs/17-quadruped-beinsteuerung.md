# Quadruped-Trot-Pruefstand

Stand 2026-09-12. Dieses Dokument beschreibt den ersten dynamischen Hund-Vergleich fuer die Gartenroboter-Teststrecke. Gazebo ist die physikalische Wahrheit; die Browseransicht zeigt nur den Zustand und die Auswahl der Modelle.

## Modell

`quadruped_trot` ist ein dynamisches Vierbeinmodell mit einem Rumpf, vier Beinen, je einem Hueft- und Kniegelenk pro Bein und sphärischen Fusskontakten. Die acht Beinachsen werden in Gazebo mit Gelenkmomenten angesteuert. Die strukturellen Bauteile haben eigene IDs:

| ID | Bauteil | Zweck |
| --- | --- | --- |
| `QDP-BASE-001` | Quadruped-Rumpf | Massentraeger, IMU, spaetere CAD-Referenz |
| `QDP-LEG-001` | Beinmodul | Huefte, Oberschenkel, Knie, Unterschenkel, Fusskontakt |

Die Roboterspezifikation steht zentral in `config/robot-spec.json`. Daraus werden `models/quadruped_trot/model.sdf`, `urdf/quadruped_trot.urdf.xacro` und der Browserkatalog generiert.

## Beinsteuerung

Das Gazebo-Systemplugin `garden::QuadrupedTrot` abonniert `/garden/cmd_vel` und erzeugt einen einfachen Trot. Die diagonalen Beinpaare laufen gegenphasig. Huefte und Knie werden ueber PD-Regelung mit Momentgrenzen geregelt. Das ist bewusst nur ein mechanischer Pruefstand fuer die Vergleichsmatrix, noch kein robuster Laufroboter-Regler.

Aktuell nicht enthalten:

- keine Schwerpunkt- oder ZMP-Regelung,
- keine adaptive Fussplatzierung nach Roll/Pitch,
- keine Kontaktkraftregelung,
- keine aktive Koerperhoehenregelung,
- keine Pfadplanung oder KI.

## Messung

Die identische Chassis-Matrix wurde fuer `light45`, `medium65` und `heavy85` wiederholt. Der Terrain-Audit loggt fuer den Hund zusaetzlich:

- maximale Beinachs-Momente,
- mechanische Beinleistung aus Gelenkmoment mal Gelenkgeschwindigkeit,
- Roll/Pitch,
- Rumpfkontakt,
- Fuss-/Beingliedkontakte,
- Fortschritt und Erfolg je Hindernis.

## Ergebnis

Alle 42 Hund-Runs sind fehlgeschlagen. Der Hund kippt bereits bei der 30-mm-Stufe beziehungsweise beim Anfahren in der Teststrecke stark genug, dass Rumpf oder Beinglieder Kontakt bekommen. Die Vorwaertsbewegung bleibt deutlich unter der Erfolgsschwelle. Energie pro Meter wird deshalb nicht als brauchbare Fahrenergie bewertet.

Die Ursache ist nicht die Webvisualisierung. Das Gazebo-Modell faellt wegen unzureichender Beinregelung und nicht ausgereifter Mechanikabstuetzung durch. Damit ist der Hund jetzt fair im Vergleich enthalten, aber aktuell mechanisch/reglerisch noch nicht konkurrenzfaehig zur verbesserten Raupe.

## Naechste mechanische Entscheidungen

- Soll der Hund zuerst als langsam schreitender Statisch-Gang laufen statt als Trot?
- Welche Arbeitshoehe und welcher Werkzeugkraftvektor sollen fuer den Hund gelten?
- Soll jeder Fuss eine groessere Sohle/Klaue fuer Marschboden bekommen?
- Braucht der Rumpf eine niedrigere Schwerpunktlage oder breitere Standspur?
- Wie viel Gelenkmoment ist fuer 45/65/85 kg realistisch mit 3D-gedruckten Strukturteilen und gekauften Aktuatoren?
