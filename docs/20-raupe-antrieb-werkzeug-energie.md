# Vorbemessung: Raupe, Werkzeug und Energie

Stand 2026-10-25. Die Raupe ist die **Arbeitsrichtung für die nächste mechanische Untersuchung**, noch keine abschließend gewählte Hardware. Ziel ist ein tiefer Gesamtschwerpunkt bei ausreichendem Freiraum über einem etwa 15 cm hohen Kartoffeldamm. Alle Zahlen unten sind Rechenbeispiele aus [mechanical-sizing.json](../config/mechanical-sizing.json) und [robot-spec.json](../config/robot-spec.json), keine Messwerte für Kirchwerder. Reproduzieren mit `python3 scripts/size_mechanics.py`.

## Geometrie und Schwerpunkt

Für die derzeitige 8-cm-Überreihenvariante gelten 64 kg Betriebsmasse, 62 cm Abstand der Kettenmitten, 70 cm Außenbreite, etwa 98 cm angenommene Auflagelänge und 48 cm nominelle Unterbodenfreiheit. Der Rumpf-Link hat im aktuellen Ersatzmodell seinen Schwerpunkt bei z = 47 cm. **Das ist nicht die Höhe des Gesamtschwerpunkts** mit Batterie, Arm, Werkzeug und einzelnen Laufrollen. Außerdem ist die derzeitige Kettenhülle nur sichtbar; die physikalischen Kontakte kommen überwiegend von Rollen. Die hohe Unterbodenfreiheit und ein tiefer Gesamtschwerpunkt sind erst durch ein Brückenchassis mit tiefen Massen an den Seiten technisch zu vereinen. Batterie, Fahrmotoren und gegebenenfalls Pumpe gehören so tief wie möglich in seitliche Module, nicht mitten in den freien Pflanzenraum. Arm und voller Werkzeughub verändern die Schwerpunktlage; sie müssen in jeder Arbeitsstellung gemessen werden.

Aus `2 × Kettenbreite × Auflagelänge` entstehen bei **vollflächig** tragender Kette 0,157 m² und rechnerisch 4,0 kPa mittlerer Bodendruck für die 8-cm-Variante. Die 6-cm-Variante ergibt 5,0 kPa, die 12-cm-Variante 2,9 kPa. Das sind optimistische Geometrie-Proxys, **keine** Gazebo-Kontaktmessungen und keine Aussage über Einsinken oder Verdichtung des Marschbodens. Der wirkliche Druck kann wegen einzelner Kontaktrollen erheblich höher sein. Die 12-cm-Variante ist zugleich für die aktuelle 62-cm-Reihendarstellung zu breit; Bodendruck allein entscheidet nicht.

## Fahrantrieb: erster Lastfall

Für Geradeausfahrt ohne Beschleunigung gilt im einfachen Modell

`F = m g (sin(α) + c_rr cos(α))`, `T_je_Seite = F r / 2`, `P_mech = F v`.

Annahmen: 64 kg, `c_rr = 0,10` als **frei gewählter Sensitivitätswert**, effektiver Radius 0,12 m und 0,35 m/s. Der Roll-/Bodenwiderstand ist in Kirchwerder nicht gemessen; Rangieren auf der Stelle, weicher Boden und Blockieren sind in dieser Formel nicht enthalten.

| Steigung | Vortriebskraft | Moment je Seite | mechanische Fahrleistung | Reibgrenze bei μ = 0,25 |
| --- | ---: | ---: | ---: | ---: |
| 0° | 63 N | 3,8 Nm | 22 W | 157 N |
| 5° | 117 N | 7,0 Nm | 41 W | 156 N |
| 10° | 171 N | 10,3 Nm | 60 W | 155 N |

Bei μ = 0,25 wäre die 10°-Fahrt in diesem Beispiel schon durch Traktion begrenzt, auch wenn ein Motor mehr Moment liefern kann. Das derzeitige 48-Nm-Limit pro Seite ist ein Simulationslimit, **kein** belegtes Dauermoment eines auswählbaren Motors. Ein Motor-/Getriebeentwurf benötigt zusätzlich Anfahr-, Wend-, Blockier- und Temperaturfälle sowie die tatsächlich gemessene Raupenreibung. Die elektrische Fahrleistung liegt wegen Motor-, Getriebe- und Kettenverlusten über den Tabellenwerten.

## Standfestigkeit bei der Werkzeugbenutzung

Eine erste, bewusst optimistische Rollabschätzung ist `M_rest = m g ((Spurweite + Kettenbreite)/2 − seitlicher_Schwerpunktversatz) − F_seitlich × Werkzeughöhe`. Bei 64 kg, 8-cm-Kette, 55 cm Werkzeughöhe und mittigem Schwerpunkt ergeben sich für 150/300/500 N Seitenkraft rund **137/55/−55 Nm** Restmoment. Schon 10 cm Schwerpunktversatz zur belasteten Seite ändern dies auf **74/−8/−118 Nm**. Negative Werte bedeuten Kippgefahr in dieser Idealisierung. Tatsächliche Rollenauflage, Längslage, Hang, Federweg, Armstellung und Schlupf können die Reserve weiter reduzieren.

Das 500-N- und 1000-N-Werkzeuglastprogramm ist somit ein **Prüfprogramm mit sicherem Abbruch**, keine Zielvorgabe, die jeder Arm frei seitlich aufbringen muss. Greifer und Schere können große **interne** Kräfte haben, ohne dieselbe äußere Kraft auf das Chassis zu übertragen. Beim vertikalen Ausziehen wirkt am Werkzeug eine Reaktion nach unten; beim Abstechen kann der Boden den Roboter nach oben entlasten. Auch diese Kraftlinien und Hebelarme gehören in den Gazebo-Wrench-Test. Ein bodennaher, kurzer Werkzeugweg und bei Bedarf eine separate Bodenstütze sind zu untersuchen.

## Elektromechanik und Hydraulik fair vergleichen

Die Fahrketten bleiben in der ersten Auslegung elektrisch angetrieben und unabhängig regelbar. Für Arm und Werkzeuge vergleichen wir zwei **alternative** Aktorketten bei gleicher Ausgangskraft, Geschwindigkeit und Haltezeit:

1. Elektrischer Motor mit Getriebe/Spindel, Kraftmessung und gegebenenfalls Haltebremse.
2. Elektrisch betriebene, bedarfsgeregelte Hydraulikpumpe mit Ventil, Zylinder, Druck- und Wegmessung. Pumpe, Tank, Leitungen, Ventile, Öl und Kühlung zählen vollständig zur Masse und Energiebilanz.

Hydraulik erzeugt keine Energie: Batterie → Elektromotor → Pumpe → Ventil/Leitung → Zylinder. Pumpenleistung ist näherungsweise `p[bar] × Q[L/min] / 600` in kW, vor Wirkungsgradverlusten. Der Zylinder liefert näherungsweise `F = p A η_Zylinder`. Diese Beziehungen stehen auch in den technischen Formelsammlungen von [Parker](https://www.parker.com/content/dam/Parker-com/Literature/PMDE/Service_Manuals/Fixed_Motors/F11_F12/MSG30-5511-M1-UK.pdf) und [Bosch Rexroth](https://apps.boschrexroth.com/products/compact-hydraulics/ch-catalog/pdf/RE18306-02_gruppo%201_nlo.pdf). Die [US-Energiebehörde](https://betterbuildingssolutioncenter.energy.gov/better-plants/pumps) empfiehlt bei Pumpensystemen unter anderem Abschalten bei Nichtbedarf und variable Drehzahl statt unnötiger Drosselung.

**Rechenbeispiel, keine Komponentenwahl:** 16-mm-Zylinderbohrung, 50 bar, angenommener Zylinderwirkungsgrad 0,75 und Werkzeuggeschwindigkeit 0,02 m/s. Kolbenfläche 201 mm²; bei 50 bar etwa 754 N Ausgangskraft. Benötigter Volumenstrom 0,24 L/min; hydraulische Leistung bei vollen 50 bar etwa 20 W. Bei angenommenen 60 % Wirkungsgrad von Pumpenmotor plus Pumpe sind das rund 34 W aus dem Akku **während dieses Hubs**, zuzüglich Ventil-, Leitungs-, Standby- und Steuerverlusten. Für 500 N wären rechnerisch etwa 33 bar erforderlich. **1000 N erfordern bei dieser Bohrung etwa 66 bar und sind am angenommenen 50-bar-System nicht erreichbar.** Elektromechanisch sind 500 N bei 0,02 m/s ebenfalls nur 10 W Nutzleistung; bei angenommenen 60 % Gesamtwirkungsgrad rund 17 W aus dem Akku während der Bewegung. Halten, Beschleunigung und Leerlauf fehlen in beiden Kurzrechnungen.

Die Wahl hängt daher vom vollständigen Lastzyklus ab. Eine ständig laufende Pumpe kann bei den kurzen, seltenen Unkrauteingriffen mehr Energie verbrauchen als einzelne elektrische Aktoren; eine abgeschaltete oder drehzahlgeregelte Pumpe kann diesen Nachteil verringern. Hydraulik kann besonders für einen sehr kraftvollen kurzen Hub interessant sein. Ihre Druck-, Wärme-, Leckage- und Gewichtsfolgen müssen im Maßstab dieses Roboters eigens belegt werden. **Vorläufige Architektur:** elektrische Fahrmotoren, elektrische Armachsen mit Bremsen als Referenz, hydraulisches Stech-/Zugmodul als gesonderte Vergleichsvariante. Eine zentrale Hydraulik für alle Anbauteile wird erst gewählt, falls sie im gemessenen Zyklus bei gleicher Masse und Präzision einen Vorteil zeigt. Es wird noch keine Hardware beschafft.

## Akku und Sensorik

Das bisherige Batteriebeispiel ist 48 V × 20 Ah = 960 Wh nominal; bei 80 % nutzbarem Anteil 768 Wh. Bei **angenommenen mittleren Batterie-Leistungen** von 200/350/500 W ergeben sich idealisiert 3,84/2,19/1,54 Stunden. Für ein Ziel von zwei Stunden darf der Mittelwert höchstens 384 W betragen, bevor Reserve für Alterung, Kälte und Rückfahrt berücksichtigt wird. Eine hypothetisch permanent 40 W aufnehmende Pumpe würde in zwei Stunden allein 80 Wh verbrauchen. Ob sie im Stillstand wirklich Strom braucht, hängt vom konkreten Hydraulikkreis ab. Diese Zahlen sind keine Laufzeitprognose aus den bisherigen Gazebo-Ergebnissen: Dort ist bislang vor allem **mechanische** Gelenkenergie erfasst.

Sensorentwurf: Umgebungssensor für Hindernisse und Fahrkorridor, nach unten blickender Tiefensensor für Dammkante/kleine Hindernisse, RGB-Kamera für Kulturpflanze/Unkraut, Werkzeugkamera für den Nahbereich, IMU, Gelenk-/Kettenencoder, Werkzeugkraft/-weg sowie Akku-Strom und -Spannung. Eine einzelne Frontkamera kann verdeckte Furchen, Überhänge oder den Greifpunkt nicht in allen Posen sicher erfassen. Für die virtuelle Phase werden Reichweite, Sichtfeld, Abschattung, Wetter-/Lichtausfälle und Leistungsaufnahme als Sensorparameter geführt; konkrete Geräte werden erst später ausgewählt. Das ist eine Architektur für Hinderniserkennung, noch keine neue autonome Navigation oder Pflanzen-KI.

## Nächste Freigabemessungen

- Gesamtschwerpunkt und Kippreserve in Gazebo für Batterie-, Arm- und Werkzeugstellungen loggen; keine Entscheidung aus dem Rumpf-Link-Schwerpunkt allein.
- 6-/8-/12-cm-Ketten bei gleicher Gesamtmasse und gleicher Antriebsgrenze auf dem 62-cm-Profil prüfen. Damm-/Krautkontakt, Schlupf, reale Kontaktflächen und Aufsetzen trennen.
- Bodenparameter für trockenen/feuchten Marschboden als Sensitivitätsfälle führen; vor realem Leistungsversprechen vor Ort kalibrieren.
- Für Zug, Schnitt und Abstechen identische Wrench-Zeitreihen verwenden. 100/250/500/1000 N als Lastfälle mit `erreicht`, `sicher abgebrochen` und `nicht ausführbar` auswerten.
- Elektrisch und hydraulisch gegen denselben Zyklus rechnen: Pumpe an/aus, Ventil- und Leckverluste, Halten, Wärme, Zusatzmasse, Werkzeugzeit und Wh pro erfolgreich entfernter Pflanze. Akku- und Sensorsysteme bleiben für beide gleich.

Die aktuelle Browserseite zeigt weiterhin nur die Gazebo-Szene; diese Vorbemessung verändert die Gazebo-Physik noch nicht.
