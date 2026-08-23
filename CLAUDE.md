# Police Stop Analysis

> Projekt-Anweisungen für Claude Code. Wird automatisch geladen, sobald die Session in
> diesem Ordner läuft.

## Projektüberblick

Explorative pandas/scipy-Analyse eines US-Polizeikontrollen-Datensatzes (Kaggle,
siehe README.md). Ein einzelnes Analyseskript, kein größeres Softwareprojekt, deshalb
ist Subagenten/Skills-Infrastruktur hier bewusst weggelassen.

## Technischer Stack

| Bibliothek | Zweck |
|---|---|
| pandas | Datenbereinigung und -aufbereitung |
| scipy.stats | Chi-Quadrat-Tests auf Unabhängigkeit |
| numpy | Hilfsfunktionen |

Python 3, eigenes `.venv` im Projektordner (nicht committen, siehe `.gitignore`).

## Arbeitsregeln

- `police_stop_analysis.py` ist in nummerierte Schritte gegliedert (Schritt 1 bis 7:
  Profiling, Bereinigung, Datenqualitätscheck, Fragestellungen, Analyse,
  Visualisierung, Dokumentation). Neue Auswertungen in Schritt 5 ergänzen, neue
  Fragen vorher in Schritt 4 dokumentieren.
- Wichtige methodische Einschränkung des Datensatzes (keine Baseline für
  "Wahrscheinlichkeit eines Verstoßes") steht in der README, bei neuen
  Fragestellungen daran halten, siehe README.md.
- Status offener/beantworteter Fragen in der README-Checkliste aktuell halten.

## Aktueller Stand

Siehe README.md ("Status der Fragestellungen"). Projekt ist **work in progress**,
Fragen b) bis f) und die Visualisierung stehen noch aus.
