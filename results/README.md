# Versuchsergebnisse

M1-Fahrversuche wurden am 2026-09-07 ausgeführt. Lokale Laufakten:

- `m1-preflight-20260907/`: ein vorläufiger Funktionslauf.
- `m1-acceptance-20260907/`: neun bestandene Fahrdurchläufe; zehnter Weltstart nach 20 s nicht bereit, Serie nicht abgenommen. Rohdaten bleiben erhalten.
- `m1-acceptance-20260907-r2/`: fünf bestandene Läufe, ein vorzeitiger Sensor-Stopp, ein Bereitschaftsfehler mit fehlender Uhr, drei ungeprüft; keine Freigabe.
- `m1-acceptance-20260907-r3/`: acht bestandene Läufe, IMU beim neunten Start nicht bereit, zehnter Lauf ungeprüft; keine Freigabe.
- `m1-acceptance-20260907-r4/`: ein bestandener Lauf, zweiter Start ohne Daten, acht ungeprüft; erfolglose Partitionserneuerung zurückgenommen.
- `m1-final-function-20260907-r2/`: finaler einzelner Fahrtest und korrigierte Sensorfehlerinjektion bestanden (51 verworfene IMUs, `heading_timeout` nach rund 0,52 s); keine Zehner-Abnahme.
- `m1-final-function-20260907/`: ein bestandener Fahrdurchlauf; Sensorfehlerinjektion nicht erfolgreich isoliert (`command_timeout`, keine verworfenen IMUs). Keine M1-Abnahme.

Jede Laufakte enthält Quellkopien, SHA-256-Manifest, Simulator-/Bridge-Logs, Einzelmetriken und JSONL-Zeitreihen. Keine elektrischen Energiemessungen oder Werkzeug-/Geländevergleiche vorhanden. Große Logs und Rohdaten bleiben außerhalb von Git; kleine Nachweise werden unter `docs/validation/` abgelegt. Der weitergehende Messvertrag steht in [Messgrößen](../docs/05-messgroessen.md).
