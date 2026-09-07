# Funktionen zuerst, danach Referenzgröße und Prototypauslegung

Stand 2026-09-07. Nutzerentscheidung: Zuerst alle benötigten Roboterfunktionen virtuell entwickeln. Danach eine Referenzgröße für den ersten physischen Testaufbau festlegen und daraus gemeinsam mit den Lastfällen Antriebe, Tragstruktur und Standfestigkeit auslegen. Ein späterer Prototyp soll gedruckte Bauteile, reale Motoren, gegebenenfalls Hydraulik sowie LiDAR und Kamera enthalten. Das ist eine Entwicklungsrichtung, noch kein Hardwarekauf, Druckauftrag oder freigegebener Bauplan.

## Reihenfolge und Abgrenzung

1. **Virtuelle Funktionsentwicklung:** M1–M6 mit parametrierbaren Abmessungen, Massen und Antriebsgrenzen umsetzen. Die bisherigen Werte in `config/concepts.json` bleiben vorläufige Simulationsannahmen. Ohne solche Werte können Bewegungen und Kräfte nicht sinnvoll geprüft werden. Kein kosmetischer CAD-Ausbau als Ersatz für fehlende Mechanik.
2. **Referenzgröße festlegen:** Nach den Funktionstests Bauraum, Reichweite, Bodenfreiheit, Spur-/Stützbreite, Zielmasse, Werkzeug und Sensoranordnung des ersten Testprototyps festlegen. Alle drei Konzepte bleiben virtuelle Vergleichskandidaten; zunächst dient das Kettenkonzept als Entwicklungsreferenz. Ein physischer Prototyp aller drei ist nicht vorausgesetzt.
3. **Mechanisch auslegen und rückprüfen:** Gemessene Lastfälle auf den gewählten Aufbau übertragen; Material, Querschnitte, Lagerungen, Getriebe und Energieversorgung auslegen. Geänderte Masse, Trägheit, Schwerpunkt und Antriebsgrenzen in die Simulation zurückführen und die betroffenen Tests wiederholen.
4. **Späterer Funktionsprototyp:** Gedruckte Strukturteile nach ihrer nachgewiesenen Eignung mit Motoren, Lagern, Achsen, Verbindungselementen und Sensoren kombinieren. Zuerst einzelne Baugruppen prüfen, dann das Gesamtsystem. Teilefreigabe und Beschaffung folgen erst in dieser späteren Phase.

Die M1–M6-Nummerierung bleibt erhalten. Die aktuellen Neustartfehler aus [M1](10-m1-abnahme.md) sind weiterhin offen; diese Planung erklärt keine Funktion für fertig.

## Erforderlicher Funktionsumfang

| Bereich | Virtuell zu implementieren und nachzuweisen | Zuordnung |
|---|---|---|
| Basis und Bedienung | Roboter einzeln wechseln; vorwärts/rückwärts, links/rechts, wenden, halten; Befehlsabbruch, Daten- und Verbindungs-Watchdogs | M1 |
| Fortbewegungsmechanik | Ketten-/Bodenkontakt, Laufrollen, Federung und Anschläge; für Quadruped/Humanoid Gelenke, Stand, Gang und Balance | M1–M2 |
| Gelände | Unebenheiten, Steigung, Reibungsproxy und Hindernisse; Schlupf, Bodenfreiheit und Kontaktverlust erfassen | M2 |
| Sensorik und Zustand | simulierte LiDAR- und Kameradaten, IMU und Gelenkzustände; gemeinsame Zeitbasis, Koordinatensysteme, Zustandsschätzung und Ausfallbehandlung | schrittweise ab M1/M2, integriert bis M6 |
| Arm und Hände | Ausgangs-/Arbeitspose, Werkzeugpositionierung, Gelenkgrenzen, Selbstkollision, Rückzug; Humanoid mit beiden Armen/Händen | M3 |
| Werkzeugkräfte | 100/250/500/1000 N als angeforderte Lasten; Kraftübertragung, seitliche Kräfte, Grenzen und kontrollierte Abbrüche | M4 |
| Pflanzeninteraktion | Kontakt, greifen, halten, lösen, Schlupf, Stängelbruch, Wurzelwiderstand; herausziehen, schneiden und abstechen | Greifen M5; vollständige Methoden bis M6 |
| Autonomie | Pflanze erkennen, Nutzpflanze unterscheiden, Ziel anfahren, Arbeitsmethode wählen, stabilisieren, Werkzeug einsetzen und Ergebnis kontrollieren | M6 |
| Vergleich und Betrieb | gemeinsame Strecke, Aufgabenzeit, Erfolg/Schaden, Kräfte, Stabilität und begründetes Energieverbrauchsmodell; reproduzierbare Fehlerberichte | M1–M6 |

LiDAR und Kamera ergänzen sich im geplanten Aufbau: LiDAR für geometrische Umgebungserfassung und Hindernisse, Kamera für Pflanzenbeobachtung. Konkrete Sensortypen, Sichtfelder, Messraten und Erkennungsmodelle bleiben zunächst parametrierbar. Bekannte Pflanzenposen dürfen Mechaniktests vereinfachen, ersetzen aber nicht die Wahrnehmungsabnahme. Zusätzliche Gartenarbeiten erhalten später eigene Werkzeuge und Aufgabenabläufe.

## Auslegung nach Wahl der Testgröße

Die Größe allein bestimmt weder Wandstärke noch erreichbare Zugkraft. Für jeden Lastfall werden Kraftangriffspunkt, Richtung, Dauer, Dynamik, Bodenkontakt und Roboterpose festgehalten. Daraus entsteht eine Auslegungstabelle je Bauteil und Antrieb:

- erforderliche Werkzeugkraft, Fahrzugkraft und Gelenkmoment getrennt; Dauerlast, Spitzenlast und Blockierfall unterscheiden;
- Hebelarme, Lagerkräfte, Biegung, Torsion, Verformung, Verbindungen und Lastwechsel;
- Masse/Schwerpunkt, Stützfläche, Bodenreibung, Rutsch- und Kippgrenzen;
- Werkstoff, Herstellungsverfahren, zulässige Beanspruchung und begründete Reserven;
- Motor/Getriebe beziehungsweise Linearaktuator, Geschwindigkeit, Wirkungsgrad und Haltebedarf;
- elektrische Leistungsaufnahme, Energie je Aufgabe und Versorgung der Sensoren/Rechner.

Gazebo liefert Bewegungen und Lastverläufe. Daraus folgt keine automatische Material- oder Wandstärkenfreigabe: Festigkeitsrechnung, gegebenenfalls Strukturanalyse und später Bauteilversuche ergänzen die Starrkörpersimulation. Die Trennung von Physik, Sensoren und Darstellung beschreibt die [Gazebo-Architektur](https://gazebosim.org/docs/harmonic/architecture/).

Ein verkleinerter Prototyp bekommt eigene Kräfte, Massen und Antriebsgrenzen. Die Laststufen des großen virtuellen Prüfstands werden nicht unverändert als reale Lastanforderung übernommen. Die 1000-N-Stufe bleibt ein Grenzversuch und keine bestätigte Tragfähigkeit gedruckter Teile.

## Druckteile, Antriebe und Hardwareübergang

Gedruckte Gehäuse, Sensorhalter, Greifergeometrien und mechanische Versuchsteile sind vorgesehene Kandidaten. Tragende Teile werden erst nach Last- und Fertigungsbewertung ausgewählt. Druckorientierung und Geometrie beeinflussen die Festigkeit; eine pauschale Wandstärke oder Infill-Zahl wird jetzt nicht festgelegt. Siehe [Prusa: Konstruktion für den 3D-Druck](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135).

Elektromotoren mit Getriebe und elektrische Linearaktuatoren bilden zunächst die zu untersuchende Antriebsbasis. Hydraulik bleibt eine Alternative, die anhand Kraft, Hub, Geschwindigkeit, Masse, Energie und Regelbarkeit bewertet wird; sie ist noch nicht festgelegt. Falls gewählt, gehören Pumpe, Ventile, Zylinder und Druck-/Volumenstromgrenzen zum Modell. Eine ideal angesetzte Zylinderkraft allein ist kein validiertes Hydrauliksystem. Gedruckte Hydraulik-Druckgehäuse sind nicht Teil dieses Prototypkonzepts.

Aufgabenlogik, Wahrnehmung und Planung verwenden dieselben ROS-Schnittstellen in Simulation und späterem Prototyp. Gazebo-Sensoren werden durch Sensortreiber ersetzt, simulierte Antriebe durch Hardwareadapter. Antriebsnahe Grenzüberwachung und Geräte-Watchdogs werden für reale Hardware zusätzlich umgesetzt. Simulatorinterne Körperposen und verborgene Pflanzenparameter bleiben der Testauswertung vorbehalten.

## Konkretisierte Einsatzanforderungen

Die [Standortangaben Kirchwerder](12-einsatzgebiet-kirchwerder.md) geben inzwischen eine reale Randbedingung vor: gewünschte Ketten-Spurweite 65–75 cm zwischen den Kettenmitten, Kartoffelreihen 62 cm und Erdbeerreihen üblicherweise 75 cm. Dies begrenzt die spätere Referenzgeometrie; Kettenbreite, Fahranordnung und Prototypmaßstab sind damit noch nicht festgelegt. Die bisherigen Simulationsmaße sind daran noch nicht angepasst.
