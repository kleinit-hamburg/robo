# Gewichtsklassen und mechanischer Variantenvergleich

Stand 2026-09-12. Ziel dieses Schrittes ist ein belastbarer virtueller Mechanikvergleich, keine fertige Autonomie. Gazebo bleibt die physikalische Wahrheit fuer die fahrfaehigen Raupenvarianten. Quadruped und Humanoid sind weiterhin sichtbar und als Konzepte enthalten, haben aber noch keinen echten Gang- und Balanceregler; ihre Hindernisfaehigkeit wird deshalb nicht als gemessen ausgegeben.

## Gewichtsklassen

| Klasse | Masse | Antriebsleistung | Zweck |
| --- | ---: | --- | --- |
| leicht (`light45`) | 45 kg | unveraendert gegenueber Modell | 45 kg Gesamtmasse bei gleicher Antriebsleistung; prüft Schlupf und Standfestigkeitsverlust. |
| mittel (`medium65`) | 65 kg | unveraendert gegenueber Modell | aktueller Referenzstand. |
| schwer (`heavy85`) | 85 kg | unveraendert gegenueber Modell | 85 kg Gesamtmasse bei gleicher Antriebsleistung; prüft Traktion, Energie und Bodendruckreserve. |

Die Gewichtsklassen werden im Benchmark durch Skalierung der Linkmassen und Traegheiten erzeugt. Die Motormomentlimits bleiben gleich. Damit sieht man, ob zusaetzliche Masse wirklich hilft oder nur Energie und Lasten erhoeht.

## Neue Raupenvariante

`tracked_guided` ergaenzt das vorige `tracked_bogie` um groessere physikalische Kontaktrollen vorn/hinten, laengere Auflage und eine hoeher gefuehrte Kettenhuelle. Die Aenderung adressiert die konkrete Ursache des Scheiterns bei 100-mm-Stufen: Die vordere kleine Laufrolle prallte gegen die Kante, waehrend die sichtbare Umlenkrolle keine physikalische Kletterrolle war.

## Gazebo-Ergebnisse der Schluesseltests

| Variante | Klasse | max. geschaffte Stufe | 30° Rampe | mittlere mechanische Energie |
| --- | --- | ---: | --- | ---: |
| `tracked_bogie` | `light45` | 80 mm | ja | 0.054 Wh/m |
| `tracked_bogie` | `medium65` | 80 mm | ja | 0.083 Wh/m |
| `tracked_bogie` | `heavy85` | 80 mm | ja | 0.114 Wh/m |
| `tracked_guided` | `light45` | 100 mm | ja | 0.053 Wh/m |
| `tracked_guided` | `medium65` | 100 mm | ja | 0.082 Wh/m |
| `tracked_guided` | `heavy85` | 100 mm | ja | 0.112 Wh/m |

Direktes Ergebnis: `tracked_guided` schafft 100 mm in allen drei Gewichtsklassen, `tracked_bogie` nur 80 mm. Keine der beiden Raupenvarianten schafft aktuell 120 mm. Beim 120-mm-Test ist nicht der Unterboden die Grenze, sondern Schlupf bzw. fehlendes Hochklettern an der Stufenkante.

## Standfestigkeit bei Werkzeugkraeften

Die folgenden Werte sind statische konservative Grenzen fuer horizontale Werkzeugkraefte in Arbeitshoehe. Sie dienen als erste Mechanikabschaetzung fuer seitliches Abstechen, verklemmtes Werkzeug oder Ziehen mit Queranteil. Reine vertikale Auszugskraft drueckt das Fahrzeug in diesem vereinfachten Modell eher zusaetzlich in den Boden; kritisch bleiben dann Arm, Greifer, Struktur und Bodentragfaehigkeit.

| Plattform | 45 kg | 65 kg | 85 kg | Gazebo-Fahrt bereit |
| --- | ---: | ---: | ---: | --- |
| `tracked_bogie` | 397 N | 574 N | 750 N | ja |
| `tracked_guided` | 404 N | 583 N | 763 N | ja |
| `quadruped` | 280 N | 404 N | 528 N | nein, nur statische Abschaetzung |
| `humanoid` | 99 N | 143 N | 188 N | nein, nur statische Abschaetzung |

## Mechanische Schlussfolgerung

- Beste aktuell gemessene Hindernisbewaeltigung: `tracked_guided`, aber nur bis 100 mm Stufe, nicht bis zum Ziel 120 mm.
- Leichter 45 kg spart deutlich Energie, verliert aber Standfestigkeitsreserve fuer Werkzeugquerkraefte.
- Schwer 85 kg erhoeht Standfestigkeit und Traktion, kostet aber mehr Energie und Moment; es loest die 120-mm-Kante nicht.
- Fuer 120 mm brauchen wir als naechstes eine echte Klettergeometrie: groessere vordere Kontaktrolle, schräge/aktive Kettennase, laengere Raupenauflage oder Pendel-/Rocker-Bogie mit definierter Frontanhebung.
- Quadruped und Humanoid duerfen erst nach einem echten Gang-/Balancecontroller in dieselbe Gazebo-Hindernismatrix aufgenommen werden. Bis dahin sind ihre Hinderniswerte nicht vergleichbar.
