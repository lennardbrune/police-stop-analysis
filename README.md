# Police Stop Analysis

**Status: 🚧 Work in Progress, unfertig.**

Explorative Analyse eines US-amerikanischen Polizeikontrollen-Datensatzes mit pandas
und scipy. Ziel ist, Zusammenhänge zwischen Fahrer-Merkmalen (Geschlecht, Alter,
Hautfarbe), Verstoßart und dem Ausgang von Verkehrskontrollen zu untersuchen.

## Datenquelle

Der Datensatz `police.csv` stammt von Kaggle:
[https://www.kaggle.com/datasets/melihkanbay/police](https://www.kaggle.com/datasets/melihkanbay/police)

Lizenzbedingungen bitte direkt auf der Kaggle-Seite prüfen, hier nicht verbindlich
wiedergegeben, da nicht zweifelsfrei einsehbar.

## Wichtige methodische Einschränkung

Der Datensatz enthält ausschließlich Personen, die bereits kontrolliert wurden. Es
gibt keine Vergleichsgruppe von Fahrern, die nicht angehalten wurden oder nicht
verstoßen haben. Aussagen über die *Wahrscheinlichkeit*, kontrolliert oder eines
Verstoßes bezichtigt zu werden (z. B. nach Geschlecht oder Hautfarbe), lassen sich
mit diesen Daten allein **nicht** treffen, dafür fehlt eine externe Baseline (z. B.
Verkehrszählung oder Führerscheindaten der Gesamtbevölkerung). Testbar sind nur
Unterschiede *innerhalb* der bereits kontrollierten Personen (z. B. Durchsuchungs-
oder Verhaftungsquote je Gruppe).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 police_stop_analysis.py
```

## Status der Fragestellungen

- [x] a) Zusammenhang Geschlecht und Durchsuchungswahrscheinlichkeit: signifikant,
      Männer werden gut doppelt so oft durchsucht wie Frauen (4,33 % vs. 2,00 %)
- [x] a.i) Bleibt der Zusammenhang innerhalb der Verstoßkategorien bestehen? Ja,
      außer bei der Kategorie "Other"
- [ ] b) Alter vs. Verstoßart
- [ ] c) Hautfarbe vs. Verstoßart
- [ ] d) Drogenbezogene Kontrolle vs. Verstoßart
- [ ] e) Drogenbezogene Kontrolle vs. Geschwindigkeitsverstoß
- [ ] f) Tageszeit vs. Geschwindigkeitsverstoß
- [ ] Visualisierung der Ergebnisse

Details und Zwischenbefunde stehen als Kommentare direkt im Skript
(`police_stop_analysis.py`, Schritt 4 bis 7).
