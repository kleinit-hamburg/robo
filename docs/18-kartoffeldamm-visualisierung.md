# Kartoffeldamm-Visualisierung

Stand 2026-09-12. Das Profil `potato_ridge` bildet die neue Einsatzannahme ab: Kartoffelreihen mit 62 cm Reihenabstand, etwa 15 cm hohen Dämmen, Kartoffelkraut als nachgiebig zu behandelndes Hindernis und Unkrautpositionen zwischen beziehungsweise neben den Kulturpflanzen.

Die Darstellung ist bewusst realistischer als die Collision-Physik. Gazebo bleibt die physikalische Wahrheit, aber die Visual-Geometrie darf mehr Details zeigen, solange sie nicht als eigener Physiksimulator benutzt wird.

## Enthalten

- zwei Kartoffeldämme mit 62 cm Reihenabstand,
- Dammkörper mit einfacher Kollisionsbox und mehreren braunen Visual-Flächen,
- Kartoffelpflanzen-Dummys mit Stängel und Blattkörpern,
- Unkraut-Dummys zwischen den Dämmen,
- kleine Erdkluten als sichtbare Bodenunregelmäßigkeiten.

## Noch nicht enthalten

- elastisches Kartoffelkraut mit echter Biegesteifigkeit,
- Abknickmodell mit Schadensgrenze,
- kalibrierter schwerer Marschboden,
- Einsinken und plastische Bodenverformung,
- Werkzeugmodell für rotierende Klinge, Hacke, Greifer oder rotierenden Zieher.

## Zweck

Dieses Profil dient als visuelle und geometrische Grundlage, bevor die Werkzeugentscheidung getroffen wird. Der nächste technische Schritt ist, Kartoffelkraut und Unkraut als Kraft-/Widerstandsmodelle zu definieren: erlaubte Berührkraft, Biegewinkel, Auszugskraft, Schnittkraft und Werkzeugabstand zur Kulturpflanze.
