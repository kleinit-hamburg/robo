# Browserprüfung · 2026-09-07

Getrennte Testinstanz auf localhost:8094, ROS-Domain 180, Chromium mit Software-WebGL. Keine Änderung der Hauptansicht während der Tests.

- `tests/check_browser.cjs`: bestanden; Maus/Tastatur, Vor-/Rückfahrt mit Wegprüfung, Loslassen, Fokusverlust, Pause, drei exklusive Modelle und Gangreglersperren, mobile Breite, keine JavaScript-Ausnahmen.
- `tests/check_workbench_browser.cjs`: bestanden; Wechsel in Pflanzenprofil, sichtbarer dynamischer Arm, gesperrte manuelle Armaufträge während Automatik, physikalisch bestätigter Pflanzenzyklus, Desktop/Mobilansicht ohne horizontales Überlaufen oder JavaScript-Ausnahmen.
- Die Ansicht des beweglichen Arms und der freigegebenen Pflanze wurde zusätzlich visuell geprüft. Screenshots liegen lokal in `/tmp/garden-browser-test/`.

Frühere Browserversuche scheiterten an der Wegprüfung. Der finale Test beginnt auf einer neu geladenen freien Ebene und wartet über explizite Zustandsabfragen auf Simulationszeit. Eine Zwischenfassung mit asynchronem Browser-Warteprädikat wartete nachweislich nicht die geforderte Zeit; sie wurde ersetzt. Die Weggrenzen wurden nicht gelockert.

Bei der Wiederholung wurde eine Freigabelücke nach Profilwechsel sichtbar: Der Server wies einen vorzeitig ausgelösten Zyklus ab. Die Oberfläche sperrt nun Arm-/Aufgabenknöpfe sofort beim Wechsel und wartet auf frische Bereitschaftsdaten; der Browsertest prüft zusätzlich die erfolgreiche Auftragsannahme.

Ein zusätzlicher Wiederholungstest fand ein ROS-Array in der Arm-Stopp-Statusantwort. Diese wird nun explizit in eine JSON-Liste umgewandelt; `test_arm_stop.py` reproduziert den Fehlerpfad ohne ROS-Installation. Der Browser-Prüfer fragt nach Arm-Stopp erneut den Zustand ab.
