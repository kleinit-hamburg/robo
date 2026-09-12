# Gewichtsklassen und mechanischer Variantenvergleich

Stand 2026-09-12. Ziel dieses Schrittes ist ein belastbarer virtueller Mechanikvergleich, keine fertige Autonomie. Gazebo bleibt die physikalische Wahrheit. Die Weboberflaeche zeigt nur die Gazebo-Zustaende an.

## Gewichtsklassen

| Klasse | Masse | Antriebsleistung | Zweck |
| --- | ---: | --- | --- |
| leicht (`light45`) | 45 kg | unveraendert gegenueber Modell | 45 kg Gesamtmasse bei gleicher Antriebsleistung; prueft Schlupf und Standfestigkeitsverlust. |
| mittel (`medium65`) | 65 kg | unveraendert gegenueber Modell | aktueller Referenzstand. |
| schwer (`heavy85`) | 85 kg | unveraendert gegenueber Modell | 85 kg Gesamtmasse bei gleicher Antriebsleistung; prueft Traktion, Energie und Bodendruckreserve. |

Die Gewichtsklassen werden im Benchmark durch Skalierung der Linkmassen und Traegheiten erzeugt. Die Motormomentlimits bleiben gleich. Damit sieht man, ob zusaetzliche Masse wirklich hilft oder nur Energie und Lasten erhoeht.

## Varianten im aktuellen Vergleich

`tracked_guided` ergaenzt das vorige `tracked_bogie` um groessere physikalische Kontaktrollen vorn/hinten, laengere Auflage und eine hoeher gefuehrte Kettenhuelle. Die Aenderung adressiert die konkrete Ursache des Scheiterns bei 100-mm-Stufen: Die vordere kleine Laufrolle prallte gegen die Kante, waehrend die sichtbare Umlenkrolle keine physikalische Kletterrolle war.

`quadruped_trot` ist der erste echte Hund-Pruefstand. Er besteht aus einem dynamischen Rumpf, vier Beinen, acht angetriebenen Hueft-/Kniegelenken, Fusskontakten und einem Gazebo-Systemplugin fuer einen einfachen Trot auf `/garden/cmd_vel`. Dieses Modell ist absichtlich noch kein fertiger Balancecontroller. Es ist aber kein reiner Anzeigeplatzhalter mehr: Die Gelenkmomente, Kontakte, Neigung und Energie kommen aus Gazebo.

## Gazebo-Ergebnisse der Schluesseltests

| Variante | Klasse | vollstaendige Matrix | max. geschaffte Stufe | 30° Rampe | mittlere mechanische Energie erfolgreicher Fahrten |
| --- | --- | ---: | ---: | --- | ---: |
| `tracked_bogie` | `light45` | nein, Schluesseltests | 80 mm | ja | 0.054 Wh/m |
| `tracked_bogie` | `medium65` | nein, Schluesseltests | 80 mm | ja | 0.083 Wh/m |
| `tracked_bogie` | `heavy85` | nein, Schluesseltests | 80 mm | ja | 0.114 Wh/m |
| `tracked_guided` | `light45` | ja, 14/14 Faelle | 100 mm | ja | 0.040 Wh/m |
| `tracked_guided` | `medium65` | ja, 14/14 Faelle | 100 mm | ja | 0.061 Wh/m |
| `tracked_guided` | `heavy85` | ja, 14/14 Faelle | 100 mm | ja | 0.084 Wh/m |
| `quadruped_trot` | `light45` | ja, 14/14 Faelle | keine | nein | nicht sinnvoll, keine erfolgreiche Fahrt |
| `quadruped_trot` | `medium65` | ja, 14/14 Faelle | keine | nein | nicht sinnvoll, keine erfolgreiche Fahrt |
| `quadruped_trot` | `heavy85` | ja, 14/14 Faelle | keine | nein | nicht sinnvoll, keine erfolgreiche Fahrt |

Direktes Ergebnis: `tracked_guided` schafft 100 mm in allen drei Gewichtsklassen, aber keine 120 mm. Der Hund ist jetzt im Vergleich enthalten, faellt in der aktuellen Auslegung aber bereits beim 30-mm-Stufentest aus: Der Rumpf kippt stark, Chassis-/Beinglieder bekommen Kontakt, und die Vorwaertsbewegung bleibt weit unter der Erfolgsschwelle. Das ist ein gemessener Gazebo-Befund und keine Browser-Einschaetzung.

## Ursache des aktuellen Hund-Ergebnisses

Das erste Beinmodell hat nur einen offenen sinusfoermigen Trot mit PD-Gelenkmomenten. Es regelt keinen Schwerpunkt, keine Fussplatzierung nach Lagefehler, keine Standphasenkraefte und keine aktive Koerperhoehe. Dadurch verliert es schon beim Anfahren die stabile Vierfuss-/Zweifuss-Abstuetzung, kippt auf Roll/Pitch und setzt mit Rumpf oder Schienenteilen auf. Die gemessene Gelenkenergie ist deshalb keine brauchbare Fahrenergie pro Meter, sondern vor allem Energie im Umfallen beziehungsweise Verkeilen.

## Standfestigkeit bei Werkzeugkraeften

Die folgenden Werte sind statische konservative Grenzen fuer horizontale Werkzeugkraefte in Arbeitshoehe. Sie dienen als erste Mechanikabschaetzung fuer seitliches Abstechen, verklemmtes Werkzeug oder Ziehen mit Queranteil. Reine vertikale Auszugskraft drueckt das Fahrzeug in diesem vereinfachten Modell eher zusaetzlich in den Boden; kritisch bleiben dann Arm, Greifer, Struktur und Bodentragfaehigkeit.

| Plattform | 45 kg | 65 kg | 85 kg | Gazebo-Bewegung bereit |
| --- | ---: | ---: | ---: | --- |
| `tracked_bogie` | 397 N | 574 N | 750 N | ja |
| `tracked_guided` | 404 N | 583 N | 763 N | ja |
| `quadruped_trot` | 331 N | 478 N | 625 N | ja, aber aktueller Gang nicht stabil |
| `quadruped` | 280 N | 404 N | 528 N | nein, nur statische Abschaetzung |
| `humanoid` | 99 N | 143 N | 188 N | nein, nur statische Abschaetzung |

## Mechanische Schlussfolgerung

- Beste aktuell gemessene Hindernisbewaeltigung: `tracked_guided`, aber nur bis 100 mm Stufe, nicht bis zum Ziel 120 mm.
- Der Hund-Vergleich ist eingebaut und wiederholt die identische Testmatrix, liefert aber derzeit 0 erfolgreiche Hindernisfaelle. Naechster sinnvoller Schritt ist kein Parameterdrehen, sondern ein stabiler Stand-/Schrittcontroller mit Koerperhoehenregelung, Fuss-Trajektorien, Kontaktphasen und Lage-Rueckfuehrung.
- Leichter 45 kg spart Energie, verliert aber Standfestigkeitsreserve fuer Werkzeugquerkraefte.
- Schwer 85 kg erhoeht Standfestigkeit und Traktion, kostet aber mehr Energie und Moment; es loest die 120-mm-Kante bei der Raupe nicht.
- Fuer 120 mm bei der Raupe brauchen wir als naechstes eine echte Klettergeometrie: groessere vordere Kontaktrolle, schraege oder aktive Kettennase, laengere Raupenauflage oder Pendel-/Rocker-Bogie mit definierter Frontanhebung.
