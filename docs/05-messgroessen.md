# Objektiver Konzeptvergleich

Noch keine Messwerte vorhanden. Die folgenden Definitionen werden vor der Implementierung eingefroren.

| Messgröße | Definition / Einheit |
|---|---|
| Methoden-Erfolg | bestätigter Endzustand passend zum Auftrag / alle begonnenen Aufträge; % |
| Vollständige Entfernung | `uprooted` und Pflanze in Ablage / alle Zieh- bzw. Stech-und-Zieh-Aufträge; % |
| Schnitt-Erfolg | oberirdischer Teil getrennt und abgelegt; Wurzel verbleibt ausdrücklich |
| Nutzpflanzenschaden | Läufe mit Schutzverletzung/Kontakt oder modelliertem Schaden / alle Läufe; % |
| Zeit pro Aufgabe | Sekunden vom Auftrag bis Ergebnis, Phasen separat; Fehler-/Timeoutzeiten behalten |
| Energie pro Aufgabe | Integral elektrischer Schätzleistung inklusive Halten und Grundlast; Wh |
| Energie pro Erfolg | Gesamtenergie aller Versuche einschließlich Fehler / Anzahl Erfolge; bei null Erfolgen nicht endlich |
| Durchsatz | Erfolge / gesamte aktive Simulationszeit inklusive gescheiterter Aufgaben; Pflanzen/h |
| M4-Tragfähigkeit | je Richtung/Höhe höchste über volle 3 s tatsächlich gehaltene Kraftstufe; zusätzlich angeforderte/erreichte Kraft in N, erfüllte Haltezeit in s und Abbruchgrund |
| Krafttreue | RMSE zur Sollkurve in N, Spitzenwert und Überschwingen; Kontaktphase separat |
| Werkzeugpräzision | Positions-/Orientierungsfehler am Kontakt in mm/Grad |
| Greifschlupf | Relativweg Pflanze–Backe, mm; Griffverlustanzahl |
| Traktion | bei Kette (v_Kette − v_Boden)/max(abs(v_Kette), 0,02 m/s), dimensionslos; bei Beinen Fußgleitweg in mm |
| Kippreserve | minimales Restmoment um jeden zulässigen Stützrand, Nm; zusätzlich Abstand Schwerpunktprojektion zum Polygon, mm |
| Dynamische Stabilität | CoP-/ZMP-Abstand zum gültigen Stützgebiet, mm, nur bei passenden planaren Kontaktannahmen |
| Kontaktreserve | minimale Normalkraft sowie μN − ||F_t|| je Kontakt, N; auf unebenem Boden vollständige Wrench-Zulässigkeit |
| Auslastung | max abs(τ)/τ_cont sowie Zeit über Dauergrenze, s; Peakverletzungen extra |
| Bodeneinwirkung als Proxy | Kontaktlast / nominelle Auflagefläche in kPa, Gleitweg und tangentiale Reibarbeit in J |
| Mobilität | Passagequote, Bahnfehler, maximale bewältigte Hindernisstufe/Steigung |
| Simulationskosten | Echtzeitfaktor = simulierte / reale Laufzeit, CPU/GPU-Auslastung und Speicher |

Boden-Proxywerte sind kein Nachweis realer Bodenverdichtung. Unterschiedliche Schlupfmetriken von Ketten und Füßen nicht zu einem scheinbar identischen Score verrechnen. Körpergewicht-Normierung ergänzt die absoluten Werkzeugleistungen; sie ersetzt diese nicht, da die Gartenaufgabe absolute Kräfte fordert.

## Statistik und Auswahl

Je Fall und Konzept Anzahl gestartet/erfolgreich/abgebrochen/Timeout sowie Gründe berichten. Erfolgsquoten mit Wilson-95-%-Intervall; kontinuierliche Größen mit Median, p95 und gepaartem Bootstrap-95-%-Intervall über die gemeinsamen Seeds. Ergebnisse sowohl für alle Versuche als auch für erfolgreiche Versuche zeigen; Timeouts sind rechtszensiert und werden nicht als schnelle Erfolge gewertet. Bei 30 Seeds ist p95 unsicher; Rohwerte und Intervall ausweisen. Keine unabhängigen Wiederholungen aus Physik-Zeitschritten vortäuschen.

Geplante Mindestkriterien für Baseline (Ebene, μ 0,6, 75 N): mindestens 90 % Methoden-Erfolg, keine beobachtete Nutzpflanzenverletzung, kein Sturz, keine harten Gelenkgrenzverletzungen und p95 erfolgreicher Zykluszeiten ≤120 s. Das sind Entwicklungsziele, kein Sicherheitsnachweis; null Schäden in 30 Läufen beweisen keine Schadenfreiheit. Dies gilt insbesondere für die neue M4-Reihe 100/250/500/1000 N: `held`, `safe_abort`, `failure` und `not_tested` getrennt berichten; eine softwarebedingt noch nicht durchführbare Prüfung ist keine gemessene mechanische Grenze. Ein M4-Meilenstein kann durch vollständige Charakterisierung einschließlich Abbrüchen abgearbeitet sein, ohne dass jede Last getragen wurde. Grenzlasten dürfen sicher als nicht ausführbar erkannt werden; eine Ablehnung bleibt ohne Aufgabenerfolg.

Zuerst zulässige Konzepte anhand dieser Kriterien bestimmen. Dann Paretovergleich aus Erfolgsquote, Energie pro Erfolg, Durchsatz, Boden-Proxy, Fähigkeit auf schwierigen Flächen und Konstruktionsaufwand. Aufwand wird als qualitative Einschätzung separat geführt, nicht als gemessene Zahl. Keine willkürlich gewichtete Gesamtnote. Bei Bedarf später Gewichtung vor neuen Läufen festlegen und Sensitivität zeigen. Die Auswahl ist vorläufig, wenn Energieparameter oder Kontaktmodelle das Ranking umkehren.

## Ergebnisformat

Geplante Datei `results/<batch>/<run>/summary.json` mit mindestens:

```json
{
  "schema_version": 1,
  "run_id": "example-only",
  "concept": "tracked",
  "test_id": "T08",
  "mode": "oracle",
  "seed": 100,
  "method": "pull",
  "status": "not_run",
  "failure_reason": null,
  "duration_sim_s": null,
  "energy_est_Wh": null,
  "peak_tool_force_N": null,
  "min_tip_margin_Nm": null,
  "plant_final_state": null,
  "crop_damage": null
}
```

Zusätzlich `manifest.json` mit vollständigen Parametern/Versionen, `events.jsonl` für Phasen, `physics.csv` für Kontakt-/Lastsignale und ROS-Bag. `null` bedeutet nicht gemessen, niemals null Leistung. Ein Lauf zählt nur nach erfolgreicher Validierung der Pflichtfelder in den finalen Bericht.


Für T14 den Ergebnisdatensatz zusätzlich um `requested_force_N`, `actual_peak_force_N`, `achieved_hold_s`, `force_direction`, `force_frame`, `tool_position_m`, `milestone_id`, `load_outcome` und `abort_reason` erweitern. Beispielstatus vor Implementierung: `load_outcome: "not_tested"`; keine Nullwerte als bereits erfolgreich gemessene Last verwenden. Für T15 außerdem Streckenversion/-Hash und Lastvariante speichern, damit unterschiedliche Szenen nicht als identischer Kurs verglichen werden.
