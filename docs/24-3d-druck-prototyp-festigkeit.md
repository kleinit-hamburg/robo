# 3D-Druck beim ersten Raupenprototyp: vorläufige Lastbewertung

Stand 2026-10-25. Die aktive Gazebo-Raupe wiegt modelliert 64 kg; die Werkzeugstationen in der Feldansicht besitzen noch **keine** Masse, Gelenke oder Kollisionen. Die Testlasten 100/250/500/1000 N sind angeforderte Grenzfälle und keine bestätigten Arbeitskräfte. Der einzelne synthetische Pflanzenprüfstand nutzt 25 N Wurzelwiderstand; reale Unkraut- und Bodenkräfte in Kirchwerder sind nicht gemessen. Aus diesen Daten lässt sich noch keine Wandstärke oder Freigabe für einen Kunststoffrahmen ableiten.

## Warum die Querschnittsfrage entscheidend ist

Ein bewusst einfaches **Rechenbeispiel, kein Entwurf des aktuellen Teils**: Ein vollmassiver rechteckiger Kunststoffträger von 30 mm Breite und 20 mm Höhe kragt 250 mm aus. Eine Kraft am freien Ende erzeugt `M = F × 0,25 m`. Mit `Z = b h² / 6 = 2,0 × 10⁻⁶ m³` ergibt sich `σ = M/Z`:

| Kraft am Ende | Biegemoment | nominelle Randspannung |
| ---: | ---: | ---: |
| 25 N | 6,25 Nm | 3,1 MPa |
| 75 N | 18,75 Nm | 9,4 MPa |
| 100 N | 25 Nm | 12,5 MPa |
| 250 N | 62,5 Nm | 31,3 MPa |
| 500 N | 125 Nm | 62,5 MPa |
| 1000 N | 250 Nm | 125 MPa |

Das Datenblatt für **Prusament PETG** nennt für gedruckte Prüfkörper ungefähr 47 MPa Zugstreckgrenze in horizontaler Druckorientierung, etwa 1,7 GPa Biegemodul und **18 ± 4 MPa Zwischenlagenhaftung**. Dies sind Prüfwerte eines bestimmten Materials und Druckverfahrens, **keine zulässigen Werte unseres Bauteils**. Beim idealisierten Vollträger und 1,7 GPa Biegemodul ergibt die kleine-Balkenformel schon bei 100 N ungefähr 15 mm Durchbiegung. Bei großer Verformung gilt diese lineare Näherung nicht mehr. Hohlräume, Bohrungen, Kerben, Druckrichtung, Faserverlauf, Verbindungselemente und dynamische Lasten fehlen in der Rechnung. [Prusament-PETG-Datenblatt](https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf).

Die Rechnung zeigt: **100 N können für einen kurzen, massiven, passend gedruckten Einzelträger konstruktiv erreichbar sein, sind hier aber nicht nachgewiesen.** Bereits bei 250 N wäre dieser Beispielquerschnitt ungünstig; 500/1000 N dürfen nicht einfach durch mehr Infill als tragfähig angenommen werden. Die Druckorientierung beeinflusst die Festigkeit, wie [Prusa beim Konstruieren für FFF](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) erläutert.

## Tragstruktur und Druckteile trennen

Für einen **verkleinerten Funktionsprototypen** können gedruckte Gehäuse, Sensorhalter, Führungs- und Greiferformen sowie gegebenenfalls ein leicht belasteter Rahmen sinnvoll sein. Seine Masse, Kraftgrenzen und Geschwindigkeit müssen eigens festgelegt und geprüft werden; die 64-kg- und 1000-N-Werte des virtuellen Feldmodells werden nicht einfach auf ihn übertragen.

Für einen **vollgroßen Prototypen in der Größenordnung des 64-kg-Modells** ist ein rein gedruckter, ungetesteter Lastpfad von Kette über Spurverstellung zu Rumpf und Werkzeug keine belastbare Ausgangsannahme. Als Referenzentwurf sehen wir metallische Querträger/Schienen, formschlüssig verriegelte Spurteile, Metallachsen, Lager und verschraubte Werkzeugkraftpfade vor. Gedruckte Teile können dazu passende, austauschbare Gehäuse, Führungsabdeckungen, Kamerahalter, Krautabweiser und Greifergehäuse bilden. Metallbuchsen und Gewindeeinsätze verteilen lokale Lasten und Verschleiß; [Markforged beschreibt solche Hybridlösungen in seinem Designleitfaden](https://static.markforged.com/downloads/CompositesDesignGuide.pdf). Das ist noch keine Stückliste oder Materialfreigabe.

PETG ist eine naheliegende erste Druckoption für mechanische Versuchsteile; für dauerhaftes Außengelände kann ASA wegen seiner UV- und Wärmebeständigkeit interessant sein, braucht aber andere Druckbedingungen. Ein fasergefülltes Filament macht einen schlecht geführten Lastpfad nicht automatisch sicher. Quellen: [Prusa PETG](https://help.prusa3d.com/article/petg_2059), [Prusa ASA](https://help.prusa3d.com/article/asa_1809), [Prusa Verbundfilamente](https://help.prusa3d.com/article/composite-materials-filled-with-carbon-kevlar-or-glass_167387).

## Nachweise vor einer Belastungszusage

1. Kraftvektor, Angriffspunkt, Hebel, Anfahr-/Blockierfall und Lastzyklen aus Gazebo je Werkzeugstellung ermitteln; die Position der Werkzeugträger zuerst auf Erreichbarkeit und Kraftlinie prüfen.
2. Für Rahmen, Schiebeführung, Rastbolzen, Motor-/Lagerhalter, Arm und Greifer eigene Lastpfade sowie zulässige Verformung festlegen. Reine Starrkörperphysik in Gazebo liefert keine Kunststoffspannung.
3. CAD-Querschnitte und Verbindungen vorbemessen, dann gedruckte Probekörper und ganze Baugruppen **in derselben Druckorientierung und mit denselben Einstellungen** prüfen. Biegung, Auszug von Einsätzen, Schraubensitz, Wiederholzyklen, Feuchte und Temperatur gehören dazu.
4. Ergebnisse und Ausfälle in die Roboterspezifikation zurückführen; erst danach Material, Druckverfahren, Wandstärke und Kraftlimit festlegen.

**Arbeitsentscheidung:** 3D-Druck für schnelles Lernen und nichtkritische Formen einplanen; den tragenden Kraftpfad des großen Fahrwerks und der Zugwerkzeuge zunächst als Hybrid aus Metall und gedruckten Teilen auslegen. Ob ein konkretes gedrucktes Tragteil trotzdem genügt, entscheidet sein nachgewiesener Lastfall.
