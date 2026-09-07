# Einsatzgebiet Kirchwerder

Stand 2026-09-07. Standort- und Nutzungsangaben stammen vom Nutzer; keine Vermessung, Bodenanalyse oder bestätigte Leistungsangabe. Maschinenlesbar: [Standortanforderungen](../config/site-kirchwerder.json).

## Flächen und Aufgabe

| Angabe | Umfang | Einordnung |
|---|---:|---|
| Gesamtfläche | ca. 4.000 m² | nicht automatisch vollständig vom Roboter zu bearbeiten |
| Ackerland | gut 2.000 m² | für die Überschlagsrechnung mit 2.000 m² angesetzt |
| Jährlich genutzter Ackeranteil | etwa ein Drittel, rechnerisch ca. 670 m² | wechselnde Kulturflächen; keine feste Parzellengeometrie bekannt |
| Brachliegender Ackeranteil | rechnerisch ca. 1.330 m² | Pflege durch den Nutzer mit Traktor oder anderer Landmaschine; kein Roboter-Pflegeauftrag |
| Übrige Grundstücksfläche | rechnerisch ca. 2.000 m² | Nutzung, Befahrbarkeit und Bearbeitungsauftrag unbekannt |

Hauptaufgabe ist regelmäßiges autonomes Entfernen von Unkraut zwischen Pflanzkulturen, ähnlich dem wiederkehrenden Pflegebetrieb eines Mähroboters. Der Roboter soll hierzu erkennen, anfahren, greifen/ziehen oder schneiden/abstechen und den Erfolg prüfen. Die Brache bearbeitet der Nutzer mit Traktor oder anderer Landmaschine; sie ist vom Unkraut-Pflegeauftrag des Roboters ausgeschlossen. Daraus folgt noch keine Festlegung, ob einzelne Wege darüber als Zufahrt dienen dürfen. Einsatzintervall, tägliches Zeitfenster und tolerierter Restbewuchs werden noch festgelegt.

## Reihen und Kettenlaufwerk

Kartoffeln stehen aktuell im Reihenabstand von **62 cm**; für Erdbeeren nennt der Nutzer in der Regel **75 cm**. Gewünscht ist ein Kettenlaufwerk mit mindestens **65 cm**, möglichst verstellbar bis **75 cm**. Der Nutzer hat bestätigt: **65–75 cm bezeichnet die Spurweite zwischen den Kettenmitten.** Kettenbreite und damit Innen-/Außenbreite sind noch offen.

Für zwei symmetrische, gleich breite Ketten gilt: Bei Kettenbreite `b` und Spurweite `s` ist die freie Innenbreite `s − b` und die Außenbreite `s + b`. Daher sind Reihenabstand, freie Durchfahrt und Spurweite verschiedene Größen. Aus 62 cm Reihenabstand folgt ohne Fahranordnung und Pflanzenkontur kein freier 65-cm-Fahrkorridor.

Die Mindestspurweite von 65 cm liegt 3 cm über dem genannten Kartoffelreihenabstand. Falls die Kettenmitten zwei um 62 cm getrennten Sollspuren folgen sollen, ergibt das bei symmetrischer Ausrichtung 1,5 cm Versatz pro Seite. Ob das passt, entscheidet der verfügbare Korridor; die größere Spurweite allein garantiert keine Pflanzenfreiheit.

Vor der Geometriefestlegung klären: Fährt der Roboter über einer Kulturreihe mit Ketten in benachbarten Gassen, über mehreren Reihen oder vollständig in einer Gasse? Dazu Pflanzen-/Dammkontur, Wuchshöhe, seitliche Abstände, Kettenbreite, Unterbodenfreiheit, Wendefläche und Zufahrt aufnehmen. Die Verstellung kann zunächst als konfigurierbare mechanische Einstellung geplant werden; ein motorisch während der Fahrt verstellbares Fahrwerk ist noch nicht gefordert.

Das heutige Kettenkonzept mit angenommener Gesamtbreite 0,60 m ist **keine nachgewiesene Lösung dieser neuen Anforderung**. Seine Maße und das Browsermodell bleiben vorläufig. Mit bestätigter Spurweite müssen nun Kettenbreite, Fahranordnung, Geometrie, Trägheit, Schwerpunkt, Stützfläche und Armreichweite gemeinsam bestimmt beziehungsweise neu geprüft werden. Die Reihen-/Nutzpflanzenkonturen gelten später für alle drei Roboterkonzepte gleichermaßen.

## Schwerer Marschboden als Testanforderung

Der Nutzer beschreibt schweren Marschboden in Kirchwerder. Daraus werden zunächst getrennte Testfälle für unterschiedliche Feuchte-/Befahrbarkeitszustände, Spurrillen, Unebenheiten und Kontaktverlust geplant. Haftreibung, Einsinken, Bodenwiderstand und Pflanzen-Auszugskräfte sind vor Ort noch nicht gemessen; aus Ortsname und Bodenbezeichnung werden keine Zahlenwerte abgeleitet.

Die bisherigen Reibwerte im Benchmark sind synthetische Testparameter, keine Marschboden-Kalibrierung. Ein reduzierter Reibwert bildet weder Einsinken noch Bodenverdichtung vollständig ab. Die erste Starrkörperwelt bleibt entsprechend gekennzeichnet. Für spätere Befahrbarkeitsbewertung sind Kontaktfläche, Lastverteilung, Schlupf, Spurbildung und zulässige Bodenbeanspruchung zusätzlich zu behandeln. Schwellen für eine Entscheidung „heute nicht befahren“ müssen begründet festgelegt werden.

## Ergänzungen für den virtuellen Funktionsumfang

- **M2:** Reihenfahrt und Wenden mit Kulturkonturen, Kartoffeldämmen nach späterer Maßaufnahme und den bestätigten Laufwerksbreiten; Nutzpflanzenkontakte, Spurtreue, Bodenfreiheit und Durchfahrtsreserve auswerten.
- **M3–M5:** Unkraut im später definierten Arbeitskorridor erreichen, ohne Kulturpflanzen zu berühren; Werkzeugkräfte getrennt von Fahrzugkraft prüfen. Der Marschboden legt noch keine Auszugskraftstufe fest.
- **M6:** Arbeitsflächen, Sperrflächen und Brache getrennt kartieren; Kulturflächen jährlich neu zuweisen. Wiederkehrende Aufträge mit bearbeitetem Abschnitt, Unterbrechung, Wiederaufnahme und Fortschrittskarte. Rückkehr zu einem definierten Start-/Servicepunkt als Funktion vorsehen; eine reale Ladestation ist damit nicht festgelegt.
- **Auswertung:** Fläche pro vollständigem Pflegedurchgang, tatsächlich bearbeiteter Anteil, Zeit und Energie pro Durchgang, Fahr-/Wende-/Werkzeugzeit, Kulturpflanzenschäden, verbleibendes Unkraut und Wiederaufwuchs über mehrere Durchgänge. Wachstum zunächst als explizites synthetisches Szenario, nicht als botanisch validierte Simulation.

Die ca. 670 m² aktive Kulturfläche bilden eine erste Größe für die spätere Einsatzplanung, keine zugesagte Tagesleistung. Arbeitszeit hängt unter anderem von Reihenlänge, erreichter Werkzeugbreite, Unkrautdichte und Eingriffsdauer ab. Die ca. 1.330 m² Brache werden nicht zum Pflegeauftrag oder zum erforderlichen Pflegedurchsatz des Roboters gerechnet. Für erste Funktionsprüfungen genügt ein repräsentativer kleiner Reihenausschnitt; die spätere Missionsplanung berücksichtigt anschließend die größeren Flächen.

## Stand

Anforderungen dokumentiert; keine Standort-Testwelt erzeugt, kein Fahrwerksmaß freigegeben und keine Hardware beschafft. Die M1-Neustartprobleme bleiben offen. Diese Standortanforderungen ergänzen [Funktions- und Prototypplanung](11-funktionen-und-prototyp.md) und [Versuchsplan](04-testplan.md).
