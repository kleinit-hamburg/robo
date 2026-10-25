# Kontaktfehler in der Kartoffelreihe

Stand 2026-10-25. Ein gerader Fahrversuch in Gazebo mit `tracked_overrow_belt08`, `potato_ridge` und Seed 0 stoppte bei x ≈ 0,325 m. Der Browser zeigte weiterhin den Vorwärtsbefehl, während die Gazebo-Pose stehen blieb. Der Fehler lag in der Testwelt: Unkraut und Kartoffelkraut waren als **statische, starre Zylinder** modelliert. Erdkrümel besaßen feste Kugelkollisionen. Einige dieser Körper standen direkt in den beiden Fahrfurchen und wurden dadurch zu unerwarteten Hindernissen.

Der kontrollierte Gegenversuch änderte nur diese kleinen Kontakte: Kraut, Unkraut und Erdkrümel blieben sichtbar, ihre starren Kollisionen wurden entfernt. Dammkollisionen, Robotermodell, Regler, Geschwindigkeit und Seed blieben gleich. Die Raupe fuhr daraufhin ohne den vorherigen Stopp über x = 1,4 m. Der Versuch belegt die Ursache der frühen Blockade in dieser Strecke; er belegt noch keine reale Fahrfähigkeit auf schwerem Marschboden.

Die Pflanzenvisuals in der Feldfahrt sind jetzt ausdrücklich **keine** physikalische Pflanzeninteraktion. Pflanzenkontakt, sanftes Wegdrücken, Schadensgrenzen und Unkrautauszug brauchen ein nachgiebiges, kalibriertes Kraftmodell. Die separate Werkzeugwelt behält ihr definiertes Pflanzenmodell. Feste Steine gehören nur in die technische Hindernisprüfung, wo sie absichtlich getestet werden.

Zur Wiederholung: `python3 -m unittest discover -s tests` prüft die Kontaktstruktur der generierten Kartoffelwelt. Ein manueller Fahrversuch benutzt die Browseransicht oder die Gazebo-API; als Erfolg wird Gazebo-Pose statt Browseranimation betrachtet.
