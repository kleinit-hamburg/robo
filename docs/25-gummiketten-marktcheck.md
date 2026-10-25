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
