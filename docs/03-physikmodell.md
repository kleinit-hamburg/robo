# Physik- und Widerstandsmodell

## Starrkörper, Boden und Kontakte

Erste Stufe: Boxen, Zylinder und Kapseln, physikalisch positive Trägheitstensoren, keine dekorativen CAD-Meshes. Gravitation 9,81 m/s². Ziel ist Gazebo Harmonic mit DART; die tatsächliche Verfügbarkeit der benötigten Kontaktparameter muss vor Benchmarkbeginn durch Mikrotests bestätigt werden. Schrittweite 1 ms, Reibwert normal 0,6 und reduziert 0,25, Restitution 0. Gleiche Engine, Solverkonfiguration und Geometrieauflösung für alle Konzepte.

Reduzierter Coulomb-Reibwert repräsentiert **rutschigen Untergrund**, nicht deformierbaren weichen Boden. Einsinken, Scherfestigkeit, Spurrinnen, Bodenbruch und Rollwiderstand durch Verdrängung werden nicht physikalisch vorhergesagt. Das Szenario heißt deshalb `soft_proxy`; seine Aussagegrenze steht in jedem Bericht. Optionale spätere Boden-Nachgiebigkeit bleibt ein eigener Versuchsblock.

Kette zunächst als reduziertes Kontaktmodell; keine unrealistisch seitlich unendlich haftende Basis. Kontaktlänge, Spurweite, Längs-/Querschlupf und effektiver Antriebsradius dokumentieren. Falls Gazebo-Track-System und Backend die geforderte Reibungswirkung nicht reproduzieren, auf ein kalibriertes Mehrrollenmodell wechseln und dessen fehlende echte Kettenkontaktfläche ausweisen. Modellrevisionen nicht innerhalb eines Vergleichsbatches mischen. Der native `TrackController` ist ausschließlich geschwindigkeitsgesteuert und hat keinen Effort-Regler ([offizielle API](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1TrackController.html)). Vor Energie- und Grenzlast-Rankings benötigt die Kette deshalb einen eigenen physikalisch wirksamen Antriebsadapter mit Moment-/Leistungsgrenzen oder ein validiertes angetriebenes Rollenmodell. Reine nachträgliche Energieschätzung begrenzt keine unrealistischen Antriebskräfte. Ohne diesen Nachweis sind nur entsprechend gekennzeichnete Kinematik-/Kontaktvorversuche zulässig.

## Pflanze als lokales Widerstandsmodell

Jede Pflanze besitzt feste Wurzelpose, sichtbaren Stängel, Zielklasse und verdeckte Parameter. Zustandsautomat: `rooted → gripped → extracting → uprooted`; alternativ `cut`, `stem_broken`, `released` oder `failed`. Beim Loslassen vor Wurzellösen wird das verbleibende Modell definiert zurückgesetzt: zunächst vollständig elastisch, kein kumulativer Wurzelschaden. Erneuter Griff zählt als neuer Versuch.

Lokale z-Achse zeigt entlang der Bodennormalen nach oben. u ist positive Auszugverschiebung des Wurzelkopfs, v ihre Geschwindigkeit. Im Zustand rooted/extracting gilt:

```text
u_peak = 0,02 m; u_release = 0,06 m
F_el(u) = F_peak * u/u_peak                         für 0 ≤ u ≤ u_peak
F_el(u) = F_peak * (u_release-u)/(u_release-u_peak)  für u_peak < u < u_release
F_el(u) = 0                                        ab u_release
F_root,z = -max(0, F_el(u) + c_z * v)               bis zum Lösen
c_z = 30 N s/m
```

Bei u ≥ u_release wird irreversibel `uprooted` gesetzt und die Wurzelbindung entfernt. Dämpfung wird dann ebenfalls null. Bei Entlastung folgt das elastische Modell zurück; max begrenzt Zug auf nichtnegative Widerstandsbeträge. Negative u erzeugt keinen Zug, sondern wird vom getrennten Boden-/Stechkontakt behandelt. Bei nominal 0,02 m/s addiert Dämpfung 0,6 N, sodass die momentane Kraft leicht über dem elastischen Peak liegt. Die ideale elastische Auszugarbeit beträgt 0,5 F_peak u_release: 0,75/2,25/4,5/9 J für 25/75/150/300 N. Das dient als analytische Integrationskontrolle, nicht als elektrische Energiebilanz.

Der Plugin bringt Wurzelkräfte am Wurzelkopf ein, mit Gegenreaktion auf den Bodenanker. Der Greifer überträgt Kräfte über Kontakt oder ein kalibriertes endliches Compliance-Modell an die Pflanze. Bei vereinfachter direkter Kopplung muss die gleiche Reaktion am Werkzeug samt Hebelarm wirken; keine Kraft darf nur im Messsignal stehen. Nach Freigabe ist die Pflanze ein beweglicher Starrkörper mit nominell 0,2 kg; bis 1 kg Zuladung ist ein separater Robustheitsfall.

Seitlich gilt F_xy = -k_lat x_xy - c_lat v_xy, k_lat = 2.000 N/m und c_lat = 20 N s/m, bis zum konfigurierten lateralen Versagen (nominal 150 N für 0,1 s, danach `stem_broken` und Bindung lösen; Sensitivität 75/150/300 N). Separater Stabilitätsprüfstand erzeugt definierte externe Seitenlasten 25/75/150 N als 1-s-Rampe, 3-s-Halten, 1-s-Abbau; diesen nicht mit der Pflanzenfeder doppelt belasten. Kraftangriff und Koordinatensystem werden geloggt.

## Griff, Schneiden und Abstechen

Greifen benötigt Backenkontakt, ausreichende Klemmkraft und Lage innerhalb des Griffbereichs. Reibgrenze aus tatsächlichen Normalkräften und μ_g; übersteigt die Belastung diese Grenze, entsteht Schlupf statt einer unzerstörbaren Weld-Verbindung. Eine virtuelle Griffkopplung muss Kraft-/Momentengrenzen und Löseregel haben. Stängelbruch wird bei Zug über 200 N für mindestens 0,1 s gesetzt, als vorläufige zusätzliche Schwelle; 100/200/400 N werden variiert. Für isolierte 300-N-Basistests wird ein unzerbrechlicher Prüfkörper verwendet. Natürliche Pflanzenläufe können vorher abbrechen oder die Methode wechseln.

Schneiden: zwei gegeneinander wirkende Backenkräfte mit F_peak_cut = 50/150/300 N. Über 10 mm Schließweg ein dreieckiger Widerstandsverlauf, nominelle Arbeit 0,25/0,75/1,5 J. `cut` nur bei korrekter Stängellage, vollständigem Weg und übertragener Arbeit; abgetrennter oberer Teil wird frei, Wurzel bleibt. Interne Kräfte nicht als doppelte äußere Wrench auf die Basis addieren. Unwucht und Seitenkräfte können separat aufgebracht werden.

Abstechen: Widerstand entlang negativer Bodennormalen, F(d) = F_peak_stab min(d/0,04 m, 1) + c_d max(d_dot,0), bis 0,08 m Hub, c_d = 30 N s/m. Bodenreaktion nach oben am Werkzeug kann den Roboter entlasten. Ein erfolgreicher Schnitt der modellierten Wurzelzone erfordert Werkzeugzentrum höchstens 20 mm vom Ziel, richtige Orientierung ±15° und 60 mm Tiefe. Danach sinkt F_peak_pull im Basismodell auf 30 %; anschließend ziehen. Diese 30 % sind eine zu variierende Modellannahme (10/30/70 %), kein biologisch gesicherter Effekt. Ohne nachfolgenden Auszug zählt Abstechen nicht als vollständige Wurzelentfernung.

Nutzpflanzen-Kollisionsvolumen und Schutzzone werden separat überwacht. Es gibt zunächst keine Blatt-/Bodenverformung, keinen Wurzelwachstumsnachweis und keine Aussage über spätere Wiederbewurzelung.

## Gelenke, Stabilität und Energie

Gelenklast: τ = J(q)^T W_tool + τ_gravity + τ_inertia + τ_friction. Alle Momente sind am Gelenkausgang. Geschwindigkeits-, Positions-, kontinuierliche und kurzzeitige Momentengrenzen aktiv modellieren; Peak maximal 2 s, anschließend Abbruch/Derating bis thermisches Modell vorliegt. Keine idealen unbeschränkt starken Positionsservos.

Quasistatisch gilt Summe der äußeren Kräfte/Momente = 0; für jeden Bodenkontakt N_i ≥ 0 und ||F_t,i|| ≤ μ_i N_i. Ein Schwerpunkt innerhalb des Stützpolygons allein genügt unter Werkzeuglast nicht. Ein nach oben an der Pflanze ziehendes Werkzeug erfährt eine **nach unten** wirkende Reaktion. Beim Abstechen wirkt sie **nach oben**. Beide Kräfte können durch ihren Hebelarm kippen; Abstechen reduziert zusätzlich die Normallast.

Plausibilitätsfall Kette, Schwerpunkt mittig: seitliches Gewichtsrückstellmoment 65·9,81·0,26 ≈ 166 Nm. 150 N Seitenlast in 0,50 m Höhe erzeugt 75 Nm, idealisierte Reserve 91 Nm. Rollende Kontakte, Armverschiebung und Hang verringern diese Reserve. Bei 300 N Abstechkraft bleibt ideal N_total ≈ 338 N; μ = 0,25 erlaubt dann nur rund 85 N tangential, nicht die unbelasteten 159 N. Entsprechende Bilanz für jede tatsächliche Pose berechnen.

Elektrische Schätzung ohne Rekuperationsgutschrift:

```text
P_el = P_aux + Σ[max(τ_i ω_i, 0)/η_i + a_i τ_i²]
E_el_Wh = Integral(P_el dt)/3600
```

P_aux = 40 W gemeinsam, η_i = 0,65 nominal (Sweep 0,45/0,65/0,80), a_i = 0,005 W/(Nm)² nominal am Gelenkausgang (Sweep 0,002/0,005/0,02). Für lineare Werkzeuge analog Fv/η plus F²-Verlustkoeffizient b = 0,0002 W/N² nominal (Sweep 0,00005/0,0002/0,001); bei zwei Greiferbacken beide Kräfte berücksichtigen. Die additive Verlustkomponente ist ein bewusst grobes Vergleichsmodell einschließlich Halten, kein Motorkennfeld. Nicht gleichzeitig zusätzliche Motor-Kupferverluste addieren. Verlorene Bremsenergie, mechanische positive/negative Arbeit und Haltezeit separat berichten. Batteriemasse bleibt in allen Fällen Teil der Betriebsmasse.

## Numerische Freigabe

Vor Vergleichsläufen: ruhende Masse trägt mg (±2 %), Werkzeug-Gegenreaktion stimmt (±2 %), Federkurve und quasi-statische Arbeit treffen analytische Werte (±5 %, Dämpfungsarbeit separat), Griff rutscht an Sollgrenze (±10 %), Ebene/Hang zeigen erwartete Reibgrenze. Zeitauflösung 1 ms gegen 0,5 ms vergleichen: Arbeit, Spitzenkraft und Kippbeginn innerhalb 5 %, sonst verfeinern. Physikalische Parameter gleich lassen; Software-/Solverwerte protokollieren. Ein unvalidiertes Kontaktmodell sperrt objektive Rankings.


## M4 – Erweiterte Werkzeuglasten

Zusätzlich zu den bisherigen Pflanzenkennlinien gelten die vom Nutzer vorgegebenen Prüfstufen **100/250/500/1000 N**. Sie werden an einem nicht brechenden, starren Werkzeug-Prüfkörper getestet. Bestehende Wurzel-Peaks 25/75/150/300 N und Stängelbruchgrenzen sind dadurch nicht stillschweigend verändert. Die M6-Lastvarianten verändern ausdrücklich nur den Wurzel-Peak.

**T14-Kraftvertrag:** Vorzeichen beziehen sich auf die äußere Kraft **auf den Roboter** am Werkzeugpunkt, in einem an der lokalen Bodenfläche ausgerichteten Prüfrahmen (x entlang der Strecke, y quer, z nach oben). Jede Stufe einzeln in +x/−x/+y/−y/+z/−z. −z entspricht der Reaktion beim Herausziehen, +z der Reaktion beim Abstechen. Die lokale Prüfkraft wird in Weltkoordinaten transformiert; Gegenkraft am Bodenanker und Moment aus dem tatsächlichen Angriffspunkt berücksichtigen. Nicht dieselbe Kraft zusätzlich über Pflanzenfeder oder Greifbindung doppelt aufbringen. Interne Schneidenkräfte sind ein anderer Test.

Zunächst Ebene, μ = 0,6, Werkzeughöhen 0,10 und 0,40 m über der Fläche. Je Höhe ein vor dem Vergleich festgeschriebener, für alle erreichbarer Werkzeugpunkt und dokumentierter horizontaler Hebelarm. Gibt es keinen gemeinsamen kollisionsfreien Punkt, ist dieser Geometriekonflikt vor den Lastläufen zu klären; unterschiedliche geheime Lastangriffspunkte sind kein identischer Test. 4 Kraftstufen × 6 Richtungen × 2 Höhen = **48 Fälle je Konzept**. Danach T11-Kombinationen mit Hang/Reibungsproxy separat; nicht alle Parameter unkontrolliert kreuzen.

Pro Fall: 2 s ruhiger Ausgangszustand, 2 s lineare Lastrampe, 3 s Halten, 2 s Entlasten. Jeden Fall aus einem frischen Zustand starten, innerhalb einer Richtung aufsteigende Kraftstufen. Vorhersage einer unzulässigen Pose/Last erlaubt eine protokollierte Ablehnung vor Belastung. Während der Rampe führt eine Grenzverletzung zum begrenzten Entlasten, nicht zum weiteren Erhöhen. Ein Lastfall gilt nur dann als getragen, wenn die angeforderte Kraft innerhalb ±5 % über die vollen 3 s gehalten wird, Werkzeugabweichung ≤20 mm bleibt, kein Sturz/Rutschen vorliegt und alle Kontakt-, Gelenk- und Dauergrenzen eingehalten werden. Eine 2-s-Peakfreigabe genügt nicht für 3 s Halten.

Der Plugin muss zuerst mit gesperrter Basis gegen analytische Kräfte/Momente geprüft werden. Diese Kalibrierung zählt nicht als Stabilitätsnachweis. Die anschließenden Roboterläufe sind frei stehend und nutzen die jeweiligen aktiven Regler. Erreichte Kraft, Haltezeit und Abbruchgrund werden auch bei vorzeitigem Ende gespeichert.

**Auslegungsfolge:** Bei 0,45 m senkrechtem Hebel ergeben sich ohne Eigengewicht bereits 45/112,5/225/450 Nm aus den vier Laststufen. Das bisherige Ketten-Schulterziel von 120 Nm dauerhaft bzw. 200 Nm kurzzeitig reicht bei diesem Hebel nicht für die beiden höchsten Stufen. Bei 65 kg beträgt das Gewicht rund 638 N; eine äußere vertikale Aufwärtskraft von 1000 N erlaubt ohne zusätzliche Verankerung keine statische Bodenauflage. Das gilt nicht identisch für die nach unten wirkende Reaktion beim Herausziehen. Auch 1000 N Seitenkraft in 0,40 m Höhe erzeugen 400 Nm Kippmoment, gegenüber etwa 166 Nm idealisiertem seitlichem Gewichtsrückstellmoment des Kettenentwurfs. Diese Überschläge begründen Grenzversuche, keine Behauptung tatsächlicher Tragfähigkeit.

Numerische Prüfung wie bisher: Gegenkraft-/Momentenbilanz und Zeitschrittkonvergenz vor Ranking. Große Kräfte dürfen nicht durch unbegrenzte Positionsregler oder ideale Haftbedingungen kaschiert werden. Neue, schwerere oder abgestützte Konstruktionen wären eigene versionierte Varianten.
