# Kartoffeldamm-Visualisierung

Stand 2026-09-12. Das Profil `potato_ridge` bildet die aktuelle Einsatzannahme ab: Kartoffelreihen mit 62 cm Reihenabstand, etwa 15 cm hohen Dämmen, Kartoffelkraut als nachgiebig zu behandelndes Hindernis und Unkrautpositionen in den Fahrgassen beziehungsweise neben den Kulturpflanzen.

Die Darstellung ist realistischer als die Collision-Physik. Gazebo bleibt die physikalische Wahrheit, aber die Visual-Geometrie darf mehr Details zeigen, solange sie nicht als eigener Physiksimulator benutzt wird.

## Enthalten

- fünf Kartoffeldämme mit 62 cm Reihenabstand auf einer größeren Bodenfläche,
- Dammkörper mit einfacher Kollisionsbox und unregelmäßigem GLB-Visual,
- Kartoffelpflanzen-Dummys mit mehreren Blattvarianten,
- Unkraut-Dummys in den Furchen zwischen den Dämmen,
- kleine Erdkluten und Bodenkrümel als sichtbare Orientierungspunkte,
- zwei Raupenannahmen für die weitere Mechanikprüfung:
  - `tracked_overrow_high_clearance`: hohe Bodenfreiheit mit 12 cm Ketten als bisherige Breitenannahme,
  - `tracked_overrow_belt08`: gleiche Überreihen-Idee mit 8 cm Ketten als neuer Standard für 62-cm-Reihen,
  - `tracked_overrow_belt06`: sehr schmale 6-cm-Grenzvariante für Bodendruck-/Traktionsvergleiche,
  - `tracked_inrow_narrow`: schmale Fahrgassenvariante für Wege zwischen 62-cm-Reihen.

## Mechanische Interpretation

Die hohe 12-cm-Variante ist kein fertiger Entwurf, sondern die bisherige Prüfhypothese. Sie ist in der Browseransicht für 62-cm-Reihen sichtbar zu breit. Deshalb gibt es jetzt zusätzlich 8-cm- und 6-cm-Überreihenvarianten mit 62 cm Spurweite zwischen den Kettenmitten und 48 cm nominaler Unterbodenfreiheit. Damit können wir prüfen, ob ein Roboter eine Kartoffelreihe überbrücken kann, ohne den Damm oder das Kraut ständig zu berühren, und wie stark die schmalere Kette später Schlupf und Bodendruck verschlechtert.

Die schmale Variante ist die Gegenhypothese: etwa 34 cm Spurweite und rund 42 cm Gesamtbreite. Sie ist für Fahrgassen gedacht und verzichtet bewusst auf sehr hohe Bodenfreiheit, weil sie nicht über Kartoffelkraut fahren soll.

## Noch nicht enthalten

- elastisches Kartoffelkraut mit echter Biegesteifigkeit,
- Abknickmodell mit Schadensgrenze,
- kalibrierter schwerer Marschboden,
- Einsinken und plastische Bodenverformung,
- Werkzeugmodell für rotierende Klinge, Hacke, Greifer oder rotierenden Zieher.

## Zweck

Dieses Profil dient als visuelle und geometrische Grundlage für die Werkzeug- und Fahrwerksentscheidung. Der nächste technische Schritt ist, Kartoffelkraut und Unkraut als Kraft-/Widerstandsmodelle zu definieren: erlaubte Berührkraft, Biegewinkel, Auszugskraft, Schnittkraft und Werkzeugabstand zur Kulturpflanze.
