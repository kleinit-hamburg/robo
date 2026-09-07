# Drei alternative Konstruktionen

## Gemeinsame Auslegungsbasis

Alle Angaben sind vorläufige Entwurfswerte für erwachsene, bodennahe Unkräuter im Garten. Es liegen keine empirischen Pflanzen-/Bodendaten zugrunde. Die Lastklassen sollen zuerst die Konzepte unterscheiden; später werden sie kalibriert. Betriebsmasse umfasst Batterie, Rechner, Arm und aktives Werkzeug. Werkzeugmasse 2 kg, Pflanzen-/Erdzuladung maximal 1 kg. Keine der folgenden Lasten gilt gleichzeitig mit allen anderen am Maximum.

Bisherige Pflanzen-/Werkzeug-Basislastfälle: vertikales Herausziehen 25/75/150/300 N, Abstechen nach unten 50/150/300 N, seitliche Last 25/75/150 N. 300 N ist bereits ein Grenzversuch dieser Basisreihe und darf kontrolliert abgebrochen werden. **M4 erweitert den gemeinsamen Starrkörper-Prüfstand auf 100/250/500/1000 N**; diese Stufen sind zusätzliche Belastungstests und keine bestätigte Tragfähigkeit der hier dimensionierten Entwürfe (siehe [Physikmodell](03-physikmodell.md#m4--erweiterte-werkzeuglasten)). Schneidkraft bis 300 N zwischen den Schneiden; sie ist nicht automatisch eine äußere Kraft von 300 N auf den gesamten Roboter. Bodennahe Arbeit im Stand, Fahr-/Gehgeschwindigkeit nominal 0,15 m/s, Werkzeuggeschwindigkeit maximal 0,02 m/s. Starke Lasten nur nahe am Körper und nach Freigabe durch die Stabilitätsüberwachung.

| Parameter | Kette | Quadruped | Humanoid |
|---|---|---|---|
| Grundabmessungen L × B × H ohne ausgestreckten Arm | 0,80 × 0,60 × 0,50 m | 0,90 × 0,65 × 0,65 m im Stand | 0,45 × 0,55 × 1,20 m |
| Betriebsmasse nominal (Entwurfsbereich) | 65 kg (55–80) | 55 kg (45–70) | 65 kg (55–85) |
| Vorläufiges Massenbudget | Fahrwerk 30, Arm/Werkzeug 14, Batterie 12, Elektronik/Rest 9 kg | Beine/Rumpf 29, Arm/Werkzeug 12, Batterie 8, Rest 6 kg | Beine/Rumpf 30, Arme/Hände 18, Batterie 10, Rest 7 kg |
| Schwerpunkt-Zielhöhe bei Arbeit | 0,25 m | 0,40 m, abgesenkt | 0,55 m in Hocke; ca. 0,70 m im Stand |
| Stützfläche auf ebenem Boden | 0,65 × 0,52 m Kettenkontakt | ca. 0,75 × 0,60 m Fußpolygon | zwei Füße je 0,25 × 0,12 m; Mittelpunkte 0,34 m auseinander |
| Bodenfreiheit | 0,10 m | 0,18 m, verstellbar | 0,10 m Schrittfreiraum als Ziel |
| Armreichweite ab Schulter | 0,65 m | 0,60 m | 0,55 m je Arm |
| Aktive Freiheitsgrade des Grundroboters | 9 | 19 | 30 |
| Batterieannahme | 48 V, 20 Ah = 960 Wh | 48 V, 15 Ah = 720 Wh | 48 V, 20 Ah = 960 Wh |

Die freie Basis hat zusätzlich sechs nicht direkt aktuiert gezählte räumliche Freiheitsgrade. Ein Schneid-/Stechmodul kann einen zusätzlichen Aktuator benötigen; das zählt separat. Gelenkgrenzen und Bodenreichweite sind in der nächsten Phase mit vereinfachter Kinematik zu prüfen.

## 1. Kettenfahrzeug mit Manipulator

**Freiheitsgrade und Antrieb:** Zwei unabhängig angetriebene Ketten, ein sechsgelenkiger Arm und ein gekoppelter Parallelgreifer: 2 + 6 + 1 = 9. Elektrische BLDC-Antriebe mit Untersetzung, Drehgebern und Strommessung; Haltebremse an lasttragenden Armachsen. Ketten zunächst durch ein dokumentiertes Ersatzmodell simulieren, nicht durch hunderte Kettenglieder. Arm vorne mittig; Batterie tief und eher hinten.

**Auslegung am Gelenkausgang:** Fahrantrieb je Seite vorläufig 15 Nm kontinuierlich, 40 Nm kurzzeitig bei effektivem Radius 0,08 m. Überschlag für 15° Steigung: F = mg sin(15°) + 0,05 mg cos(15°) ≈ 196 N; je Seite 7,9 Nm ideal, ca. 10,5 Nm bei 75 % Wirkungsgrad. Kurvenfahrt im Stand kann wesentlich höhere Momente erfordern; das Ersatzmodell unterschätzt Bodenarbeit beim Skid-Steering.

Arm: Schulter 120/200 Nm, Ellbogen 80/140 Nm, Handgelenk 25/50 Nm (kontinuierlich/kurzzeitig). Bei 150 N Werkzeuglast und 0,45 m Hebel entstehen allein 67,5 Nm; Eigengewicht kommt hinzu. Bei 300 N entstehen 135 Nm. Deshalb Grenzlast nur mit kürzerem Hebel oder Abbruch. Diese Werte sind Zielgrenzen für Aktuator-Sweeps, keine Motorauswahl.

**Werkzeug:** Wurzelgreifer mit zwei konkaven, austauschbaren Backen, 0–60 mm Öffnung; Greifen nahe am Boden. Gemeinsame mechanische Werkzeugaufnahme für geschützte Bypass-Schere und schmale Stechklinge mit begrenztem Hub 80 mm. Optionaler Bodenstützfuß erst als getrennte Variante, da er die Stabilität erheblich verändert.

**Sensorik:** Gemeinsamer Satz aus Front-RGB-D, Handgelenkkamera, IMU, Gelenkgebern, Sechsachsen-Kraft-/Momentensensor am Handgelenk, Werkzeugweg/-kraft sowie Umfeld-Lidar. Zusätzlich Kettendrehzahl und Schlupfschätzung aus externer Odometrie. Reale Näherungs-/Kontaktüberwachung später ergänzen.

**Energie:** 80 % nutzbare Batterie = 768 Wh. Angenommene durchschnittliche Gesamtleistung 200–450 W ergibt rechnerisch 1,7–3,8 h; Halteverluste und Fahranteile sind erst zu simulieren. Gemeinsame Rechen-/Sensorgrundlast 40 W enthalten.

**Stabilität:** Breite, tiefe Basis, kein Werkzeugbetrieb während der Fahrt. Stützrand, Reibgrenzen und Kontaktlasten überwachen; Arm bei hohen Kräften zurückziehen. Hohe Traktion garantiert keine Kippsicherheit. Beim Abstechen kann die Kette entlastet werden.

**Vorteile:** Einfachster Einstieg, große Werkzeuglastreserve, wenig Balanceregelung, gute Integrationsfläche. **Nachteile:** Wendeschäden im Beet, begrenztes Übersteigen, Schlupf und potenziell hohe Bodenverdichtung.

**Realer Bau:** Schmutzdichte Kettenlager, Spannung, Steine im Laufwerk, Getriebespiel, Armsteifigkeit und Dichtungen sind schwierig. Bodentraktion lässt sich aus idealen Kontakten nur eingeschränkt vorhersagen.

**Verkleinerter Druckprototyp:** Beste Eignung, z. B. Maßstab 1:3 als späterer Tischversuch mit stumpfen Werkzeugen. Gedruckte Verkleidung und leichte Struktur; hoch belastete Lager-/Wellenstellen benötigen später geeignete Verstärkungen. Kein Nachweis realer Auszugskraft allein durch erfolgreiche Modellfahrt.

## 2. Vierbeiniger Quadruped mit Manipulator

**Freiheitsgrade und Antrieb:** Vier Beine mit Hüftabduktion, Hüftbeugung und Kniebeugung = 12; Arm 6; Greifer 1: insgesamt 19. Elektrische, drehmomentgeregelte Antriebe mit moderater Untersetzung, strombasierter Kraftschätzung und zusätzlicher Kontaktsensorik. Arm vorne mittig, Batterie zentral unten.

**Gelenkkräfte:** Beine Hüfte/Knie zunächst 60/120 Nm, Abduktion 35/70 Nm. Bei 55 kg tragen vier Füße im Mittel 135 N. Dreibeinstand trägt im Mittel 180 N pro Fuß; 0,25 m Hebel erzeugt 45 Nm, bei Faktor 2 dynamischer Last bereits 90 Nm. Tatsächliche Verteilung folgt Pose und Werkzeuglast; ein Einzelbein kann deutlich mehr tragen. Arm 110/190 Nm Schulter, 75/130 Nm Ellbogen, 25/50 Nm Handgelenk. Gemeinsame 300-N-Prüfung kann wegen Balance oder Drehmomentgrenze scheitern.

**Werkzeug und Sensorik:** Gleiches Werkzeugmodul und gleiche optische/Kraftsensoren wie Kette; zusätzlich Fußkontaktkräfte, Gelenkdrehmomente, Beinstellung und Rumpfzustand. Füße zunächst rund, Durchmesser 0,10 m. Im Vierfußstand liegt der nominelle Bodendruck schon bei etwa 17 kPa; Einsinken bleibt außerhalb des Basismodells.

**Energie:** 576 Wh nutzbar; angenommene Gesamtleistung 350–750 W ergibt 0,8–1,6 h. Stehende Beine brauchen unter Umständen dauerhaft Strom, auch wenn mechanische Arbeit null ist.

**Stabilität:** Langsamer statischer Kriechgang bei Anfahrt, vier Füße am Boden während Werkzeugkontakt. Stand verbreitern und Körper absenken; Fußkraftverteilung, Reibkegel und Gelenkmomente gemeinsam optimieren. Kein Dreibein-Werkzeugbetrieb in der ersten Vergleichsstufe.

**Vorteile:** Gezielte Fußplätze zwischen Pflanzen, Übersteigen und Körperhöhenanpassung. **Nachteile:** Hohe Regelkomplexität, konzentrierte Bodenlasten, Halteenergie, kleinerer verbleibender Nutzlastanteil.

**Realer Bau:** Stoßfeste Getriebe, spielfreie Füße, Kabelzyklen, wasserdichte bewegliche Gelenke und schnelle Drehmomentregelung. Ein Arm verändert das Bewegungsmodell erheblich. Fußrutschen kann mehrere Gelenke gleichzeitig sättigen.

**Verkleinerter Druckprototyp:** Mittelmäßig geeignet, etwa 1:3 für Kinematik, langsamen Gang und Reichweiten. Druckteile kriechen unter Dauerlast, Servospiel erschwert Kraftregelung. Zunächst passive Sicherung gegen Sturz im späteren Prüfstand; deren Kräfte dürfen im Vergleich nicht als eigene Stabilität zählen.

## 3. Humanoider Zweibeiner mit zwei Greifhänden

**Freiheitsgrade und Antrieb:** Je Bein sechs Achsen (Hüfte 3, Knie 1, Sprunggelenk 2), Rumpf zwei, je Arm sieben, je Hand ein aktiver unteraktuierter Griff: 12 + 2 + 14 + 2 = 30. Zwei einfache Greifhände erfüllen beidhändiges Halten und Werkzeugführen, keine vollständig unabhängigen Finger. Elektrische drehmomentgeregelte Gelenke, Lastbremsen und elastische/kraftmessende Elemente als spätere Optionen.

**Gelenkkräfte:** Hüftbeugung und Knie 100/180 Nm, übrige Hüftachsen 60/120 Nm, Sprunggelenke 50/100 Nm, Rumpf 80/150 Nm. Einbeinlast 638 N bei 0,20 m Hebel bedeutet 128 Nm vor dynamischen Zuschlägen; die Position muss daher begrenzt werden. Arme jeweils Schulter 70/120 Nm, Ellbogen 50/90 Nm, Handgelenk 20/40 Nm. 150 N an einem 0,35-m-Hebel erzeugen schon 52,5 Nm. Zweihändiges Ziehen kann Armkräfte teilen, aber nicht die äußere Gesamtlast auf die Basis reduzieren.

**Werkzeug:** Beide Hände greifen dasselbe standardisierte Werkzeug oder eine Hand stabilisiert die Pflanze, während die andere schneidet. Einhändiger Vergleichslauf plus getrennt ausgewiesener zweihändiger Zusatzlauf; identische Werkzeuggrenzkräfte. Bodenerreichbarkeit über Hocke und Rumpfneigung muss ohne unrealistische Gelenkwinkel nachgewiesen werden.

**Sensorik:** Gemeinsame Sensoren, zusätzlich Kraft-/Momentensensoren unter beiden Füßen, Handgelenksensor an jedem Arm und belastbare Schätzung des Gesamtschwerpunkts. Fußsohlenkontakt in mehrere Messpunkte auflösen.

**Energie:** 768 Wh nutzbar; angenommene Gesamtleistung 450–1.000 W ergibt 0,8–1,7 h. Dynamische Balance und viele Haltegelenke machen die Schätzung besonders unsicher.

**Stabilität:** Werkzeugbetrieb zuerst nur im Doppelstütz mit breitem Stand und gebeugten Knien. Kontakt-Wrench-Zulässigkeit, Schwerpunkt und bei Bewegung ZMP/CoP überwachen. Hände an Boden oder Hilfsstützen verändern das Konzept und werden separat geprüft. Werkzeugkräfte können den CoP rasch an den Fußrand verschieben.

**Vorteile:** Zwei Hände, großes späteres Aufgabenspektrum, gezieltes Platzieren der Füße. **Nachteile:** Geringe passive Stabilität, hoher Energie-/Softwareaufwand, großer Sturzraum und geringe Bodenreichweite ohne anspruchsvolle Hocke.

**Realer Bau:** Getriebesteifigkeit bei niedriger Masse, Sturzfestigkeit, thermische Reserven, kleine steife Hände und robuste Ganzkörperregelung. Für diesen Gartenauftrag größte technische Unsicherheit.

**Verkleinerter Druckprototyp:** Geringste Eignung für belastbare Werkzeugversuche; sinnvoll zunächst für Bewegungsraum und beidhändige Abläufe. Ein späterer gesicherter Tischversuch beweist keine freie Balance im Garten.

## Gemeinsame Werkzeugdimensionierung und Skalierung

Für reibschlüssiges Ziehen gilt bei zwei Backen näherungsweise F_z ≤ 2 μ_g N_Backe. Mit μ_g = 0,5 und Sicherheitsfaktor 1,5 benötigen 150 N Auszug 225 N pro Backe, 300 N bereits 450 N pro Backe. Nasse Pflanzen können deutlich niedrigere Reibwerte haben: μ_g = 0,2/0,5/0,8 variieren. Quetschen oder Stängelbruch kann vor dem Wurzellösen eintreten; höhere Klemmkraft ist deshalb keine universelle Lösung. Formschlüssige Wurzelaufnahme wird als eigene Variante modelliert.

Schere: bei 300 N Schneidkraft und 20 mm wirksamem Hebel mindestens 6 Nm, mit 1,5 Reserve 9 Nm vor Verlusten. Stechspindel: bei 300 N, 4 mm Steigung und Wirkungsgrad 0,35 theoretisch T = F p/(2π η) ≈ 0,55 Nm, mit Reserve 0,82 Nm; Führungsreibung und Knicken sind zusätzlich zu prüfen. Das ersetzt keine Detailauslegung.

Bei geometrischem Maßstab s = 1/3 und gleicher Dichte skaliert Masse mit s³, Gewichtsmoment mit s⁴. Externe Kraft muss für ähnliche Lastverhältnisse mit s³ skaliert werden: 150 N werden 5,56 N, 300 N werden 11,11 N. Gleiche Spannungen würden dagegen F ∝ s² verlangen. Beide Ähnlichkeiten sind nicht gleichzeitig erreichbar; reale Pflanzen und Druckmaterial verhalten sich nicht skaliert. Für dynamische Schwerkraftähnlichkeit gilt Zeit ∝ √s. Prototypdaten daher nur für den jeweils ausdrücklich definierten Nachweis verwenden.
