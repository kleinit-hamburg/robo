# Spurverstellung und Werkzeuganordnung der Feldraupe

Stand 2026-10-25. Dies ist eine **Anordnungshypothese**, keine fertige Mechanik oder CAD-Freigabe.

## Spur mechanisch einstellen

Der Nutzer hält eine manuelle Verstellung mit mechanischer Rastung für ausreichend. Wir prüfen zwei spiegelbildlich verschiebbare Kettenmodule an steifen Querträgern. Die Stellung wird auf beiden Seiten gleich eingestellt und mit formschlüssigen Bolzen beziehungsweise Raststiften plus gesicherter Klemmung verriegelt. Ein elektrischer oder hydraulischer Stellantrieb für den Spurwechsel ist nicht vorgesehen.

Vorgeschlagene, vor Ort zu bestätigende Rasterung der **Kettenmitten**: 62, 65, 70 und 75 cm. Bei 8 cm Kettenbreite ergeben sich 70, 73, 78 und 83 cm Außenbreite. Die aktive Gazebo-Raupe hat bisher **nur 62 cm als feste Geometrie**. Der Mechanismus, sein Gewicht, Spiel und die Verriegelung sind weder modelliert noch geprüft. Für Kartoffeldämme ist 62/65 cm zu vermessen; 75 cm gehört zunächst zur Erdbeeranforderung. In jeder Stellung müssen Querträger, Antriebsleitungen, Kettenlage, Nutzpflanzenfreiraum und Kippreserve nachgewiesen werden.

## Warum der obere Arm kein Feldkonzept ist

Der alte obere Arm in der Feldansicht war ein unbeweglicher Platzhalter. Der bewegliche Achtgelenk-Arm in der separaten Werkzeugwelt ist ein **isolierter Prüfstand** für bekannte Zielposen, Greifkontakte und synthetische Pflanzenkräfte. Sein erfolgreicher Prüfzyklus belegt weder, dass er Unkraut in beiden Furchen erreicht, noch dass er Kartoffelkraut schont.

Für die Feldarbeit sitzen die Ziele zunächst in den Gassen beidseits der überfahrenen Kulturreihe. Ein einzelner, hoch montierter Ausleger müsste weit nach unten und seitlich greifen. Seine Masse liegt hoch, und Werkzeugkräfte greifen mit großem Hebel am Rumpf an. Ein einzelner quer über die mittlere Kulturreihe fahrender Schlitten kann das Kraut kreuzen. Beide Anordnungen bleiben Vergleichsideen, aber keine aktuelle Bauvorgabe.

## Vorläufiges Feldlayout

Zwei **bodennahe Werkzeugstationen**, je eine vor der linken und rechten Kette, sind als Visuals in die Feldansicht gesetzt. Ihre Stationsmitten folgen der halben Kettenmitten-Spurweite; die angedeuteten Werkzeugspitzen liegen im Modell bei x = 0,78 m und z = 0,10 m relativ zur Roboterbasis. Das ist ein räumlicher Platzhalter. Die Stationen haben derzeit **keine Gelenke, Kollisionen, Masse, Motoren oder Werkzeugkräfte**. Ihr gemeinsamer Bauteilbezug ist `TRK7-FRONT-TOOL-STATIONS-001` in `config/robot-spec.json`.

Die erste zu prüfende Kinematik ist pro Seite ein kurzer seitlicher Zustellweg und ein vertikaler Hub, gegebenenfalls mit kurzem Vor-/Rückhub. Ein wechselbarer Kopf kann schneiden, flach lockern oder greifen und ziehen. Eine weiche Krautabweisung wäre eine eigene kraftbegrenzte Baugruppe; sie darf nicht als starre Pflanzensperre simuliert werden. Das Werkzeug soll **vor** der Kette arbeiten, bevor diese das Unkraut niederdrückt. Während eines Greif-/Zugvorgangs hält die Basis an.

Offen sind Reichweite bis zum Unkraut am Damm, Kollisionsfreiheit zum Kartoffelkraut, Kraft- und Weggrenzen, Bodenstütze beim Ziehen, Kamerablick, Masse der beiden Module, Energiebedarf und Wartbarkeit. Bei 100 N Werkzeugkraft und 0,78 m Längsabstand zur Rumpfmitte entsteht bereits eine nominelle Momentengröße von 78 Nm; die tatsächliche Kippreserve hängt von Kraftvektor, Kontaktpunkten, Schwerpunkt und Boden ab. Wir dimensionieren daraus noch keinen Arm.

## Nächste physikalische Prüfung

1. Arbeitszonen für 62/65/70/75 cm Spur gegen Damm, Pflanzenkontur und Kettenhüllen festlegen.
2. Pro Seite 2–3 aktive Achsen mit Masse, Trägheit, Gelenkgrenzen und Kollision in Xacro/SDF modellieren; Visual und Collision getrennt halten.
3. Werkzeugspitzen in beiden Furchen unter identischen Gazebo-Kräften positionieren; Rumpfkontakt, Roll/Pitch, Schlupf und Stabilitätsreserve erfassen.
4. Griff/Zug, Schnitt und flaches Lockern getrennt prüfen. Das bestehende Pflanzenprüfmodell darf nur als synthetischer Lastfall dienen, nicht als Nachweis für Kartoffelkraut-Schonung.
5. Erst danach elektrischen Linearaktuator und bedarfsgeregelte Hydraulik für denselben Kraft-/Hubzyklus vergleichen.

Für einen späteren gedruckten Prototypen sind Rahmen, Lagerstellen, Rastung und Werkzeugträger gesondert nachzuweisen. Die [vorläufige Druckteil-Festigkeitsrechnung](24-3d-druck-prototyp-festigkeit.md) zeigt, warum die Visuals noch keine Kunststoffkonstruktion freigeben.
