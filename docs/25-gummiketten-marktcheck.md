# Marktcheck Gummiraupen (25.10.2026)

## Ergebnis

Schmale, durchgehende Gummiraupen werden für mobile Roboter angeboten. Ein Beispiel ist [Verco Track 76 × 12,7 × 60](https://vercotrack.com/robot-tracks/robot-rubber-track-76x12-7x60/): 76 mm Breite, 12,7 mm Teilung, 60 Glieder und 762 mm Umfang. Der Hersteller bietet andere Längen und passende Antriebsräder auf Anfrage an. Er nennt bis etwa 150 kg Fahrzeuggesamtmasse für diese Bauart; das ist eine Herstellerangabe, keine Freigabe für unseren Boden oder unsere Konstruktion. [Rubtrack](https://www.rubtrack.com/project/robot-tracks/) zeigt beispielsweise 76 mm breite Bänder mit 1524 mm und 75 mm breite Bänder mit 2440 mm Umfang. Auch dort sind Maße Beispiele, keine geprüfte Verfügbarkeit für unser Projekt.

## Abgleich mit der aktiven Feldraupe

Die aktive Spezifikation `tracked_overrow_belt08` setzt 80 mm Breite, 620 mm Kettenmittenabstand und 64 kg Fahrzeugmasse an. Die sichtbare Kettenform ist **nur Visualisierung**: Bodenkontakt und Vortrieb entstehen durch gefederte Rollen. Bandteilung, Zahneingriff, Bandspannung und reale Bandmasse sind noch nicht modelliert.

Die angegebenen vorderen und hinteren Visual-Mittelpunkte liegen 1,02 m auseinander, der Visual-Radius beträgt 0,17 m. Eine idealisierte Zweirad-Schleife hätte damit `2 × 1,02 + 2π × 0,17 ≈ 3,11 m` Umfang. Das ist nur eine Plausibilitätsrechnung: Laufweg, Umlenkung, Zahnprofil und Spannweg der späteren Konstruktion sind noch unbestimmt. Ein 762-mm-Band aus dem Beispiel passt folglich nicht ohne grundlegende Änderung der Fahrwerksgeometrie. Ein marktübliches Band muss vor der Detailkonstruktion gemeinsam mit Antriebsrad und Spanner ausgewählt werden. Die verstellbare Spurweite verschiebt die beiden kompletten Raupenmodule quer und ändert deren Bandlänge nicht.

## Auswahlkriterien für den nächsten Entwurf

- Bandbreite und effektive Aufstandsfläche auf feuchtem Marschboden; 80 mm ist bislang eine Reihenabstands-Annahme, keine Bodendruck-Freigabe.
- Umfang, Teilung, innere Führung und passendes Antriebsrad als zusammengehöriges System.
- Umlenkrollendurchmesser, Spannweg und Freigang bei vollem Federweg.
- Tragfähigkeit, Schmutz-/Wasserverhalten, verfügbare Zeichnungen und Ersatzteilversorgung.
- Messung von Einsinken, Schlupf und Zugkraft an Bodenproben, bevor die endgültige Breite festgelegt wird.

**Entscheidung:** Für die virtuelle Weiterentwicklung eine 75–80-mm-Kaufraupe als Beschaffungskandidat führen, das Fahrwerk aber noch nicht auf ein konkretes Fabrikat festlegen. Es wird nichts bestellt. Erst nach einer maßlich konsistenten Raupenschleife und Boden-/Lastprüfung kann ein Band ausgewählt werden.

## Kaufbare Fahrgestelle als möglicher Ausgangspunkt

Der Hersteller [KCM/Kymoon](https://www.kcm-hk.com/Rubber-Track-Chassis-with-All-terrain-Track-Drive-System-pd594652048.html) listet komplette KCM-70-Raupenfahrgestelle: 590 × 530 × 250 mm, 70-mm-Ketten, 17,85 kg Eigenmasse und 100 kg angegebene Nutzlast; eine längere Version misst 800 × 570 × 300 mm, wiegt 44 kg und hat 150 kg angegebene Nutzlast. Die genannten Außenbreiten ergeben bei symmetrischer Anordnung ungefähr 460 bzw. 500 mm Kettenmittenabstand. Beide liegen unter unseren 620 mm, und eine freie Durchfahrtshöhe zwischen den Ketten von 480 mm ist nicht angegeben. Die kurze Variante wäre nur ein verkleinerter Fahrwerksversuch, die längere könnte als Komponentenreferenz dienen. Nutzlast ist keine Aussage über die Tragfähigkeit bei seitlichem Werkzeugzug.

[FlySpark TK650](https://flyspark.in/japan/products/flyspark-tk650-lightweight-tracked-ugv-robot-chassis-30kg-payload) ist ein weiteres integriertes Beispiel: 650 × 480 × 200 mm, etwa 25 kg Eigenmasse, 30 kg Nutzlast, 80-mm-Gummiraupen, gefederte Rollen und 2 × 300 W Antrieb. Bei unserem 64-kg-Gesamtziel blieben nach 25 kg Chassis rund 39 kg Aufbauten; das überschreitet bereits die angegebene Nutzlast. Außerdem ist die Spurweite zu klein und die Überreihen-Freiheit nicht belegt.

Ein größeres [RC MI-100](https://www.robotchassis.com/product/tracked-robot-tank-chassis/) kann laut Hersteller in 550–900 mm Außenbreite gefertigt werden, hat aber 100-mm-Ketten und wiegt schon ohne Batterie mindestens 97,5 kg. Es überschreitet damit das derzeitige Gesamtmassenziel.

**Folgerung:** Ein fertiges Serien-Fahrgestell, um das wir lediglich Werkzeug und Sensorik bauen, ist bislang nicht passend nachgewiesen. Der naheliegende Integrationsweg sind zwei möglichst vollständige, getrennt montierbare Raupenmodule mit Rollen, Spannung, Antrieb und Band. Dazwischen käme unsere eigene hohe, auf 620–750 mm Spurweite rastbar verstellbare Brücke. Vor einem Kauf müssen Herstellerzeichnungen, Modulmasse, Aufstandsfläche, Befestigung, Bandspannung, Motor-/Controller-Schnittstelle und Lastfälle im Marschboden geprüft werden. Die genannten Produkte sind Recherchekandidaten, keine freigegebenen Bauteile und keine Bestellung.
