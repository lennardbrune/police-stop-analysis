import pandas as pd
import numpy as np

df = pd.read_csv("police.csv")

trennung = "========================================================="


# ============================================================
# SCHRITT 1: Erster Überblick über die Rohdaten
# ============================================================
print(trennung, "weird stop_duration")
weird_stop_duration = df[~df['stop_duration'].isin(['0-15 Min', '16-30 Min', '30+ Min', float('nan')])]
print(weird_stop_duration)
print(df.head()) # erste Zeile ansehen
print(trennung)
print(df.shape) # Anzahl Zeilen/Spalten
print(trennung)
print(df.info()) # Daten-Typen und Null-Werte
print(trennung)
print(df.describe()) # Statistische Übersicht
print(trennung)
print(df.columns) # Spaltennamen
print(trennung)


# ============================================================
# SCHRITT 1b: Zusammenhang der Fehlwerte in den Rohdaten prüfen
# ============================================================
# Muss auf den ungefilterten Rohdaten laufen, bevor dropna(thresh=10) in
# Schritt 2 die betroffenen Zeilen entfernt - sonst ist die Frage "hängt
# fehlendes violation_raw mit den anderen Fehlwerten zusammen" schon durch
# den Filter beantwortet (und liefert danach immer 0).

kernspalten = ['driver_gender', 'driver_race', 'violation', 'stop_outcome', 'is_arrested', 'stop_duration']
unvollständig = df[df[kernspalten].isna().any(axis=1)]
violation_raw_fehlt = unvollständig[unvollständig["violation_raw"].isna()]
print(trennung, "Beispiel aus den unvollständigen Zeilen (Rohdaten)")
print(unvollständig.head(20))
print(len(violation_raw_fehlt), "von", len(unvollständig), "unvollständigen Zeilen haben auch bei violation_raw keinen Wert")


# ============================================================
# SCHRITT 2: Data Set aufbereiten
# ============================================================
df = df.drop(columns=['county_name'])  # zu 100% leer

df['stop_outcome'] = df['stop_outcome'].replace('N/D', pd.NA)  # verdeckter Fehlwert

df['search_type'] = df['search_type'].fillna('Keine Durchsuchung')  # NaN hier = fachlich korrekt, keine Durchsuchung

# driver_age_raw ist das Geburtsjahr des Fahrers (nicht das Alter!) -
# Werte wie 0, 2919 oder 8801 sind Tippfehler. Das bereits korrekt
# berechnete Alter steht in driver_age.
df['driver_age_raw'] = df[(df['driver_age_raw'] >= 1900) & (df['driver_age_raw'] <= 2015)]['driver_age_raw']

# stop_duration ist kategorial ('0-15 Min', '16-30 Min', '30+ Min'), kein
# numerischer Wert - ein Vergleich mit > 5 ist nicht möglich. Zwei Zeilen
# enthalten zudem Datenmüll ('1', '2'), der zu keiner Kategorie gehört.
df['stop_duration'] = df['stop_duration'].replace({'1': pd.NA, '2': pd.NA})

df = df.dropna(thresh=10)  # Zeilen mit weniger als 10 ausgefüllten Spalten löschen

df["is_arrested"] = df["is_arrested"].astype("bool")  # bool statt int64
df["stop_date"] = pd.to_datetime(df["stop_date"])  # datetime statt object
df["stop_time"] = pd.to_datetime(df["stop_time"], format="%H:%M").dt.time  # datetime statt object

# Zwolf eindeutige Duplikate Raus mit dem Index (83361–83372)
df = df.drop(index=range(83361, 83373))

df = df.drop_duplicates()  # alle weiteren Duplikate raus

# ============================================================
# SCHRITT 3: Datenqualität nach der Bereinigung prüfen
# ============================================================
print(df["driver_gender"].isna().sum())
print(trennung, "Anzahl der Null-Werte in der Spalte 'driver_gender'")

print(df.isnull().sum()) # Anzahl der Null-Werte pro Spalte
print(trennung, "Anzahl der Duplikate")

print(f"Anzahl der Duplikate: {df.duplicated().sum()}") # Anzahl der Duplikate
print(trennung, "Anzahl der eindeutigen Werte pro Spalte")

print(df.nunique()) # Anzahl der eindeutigen Werte pro Spalte
print(trennung, "Datentypen der Spalten")

print(df.dtypes) # Datentypen der Spalten
print(trennung, "Statistische Übersicht der numerischen Spalten")

print(df.describe()) # Statistische Übersicht der numerischen Spalten
print(trennung, "Spalten mit stop_duration > 5")
print(df[df['stop_duration'] == '30+ Min']) # Spalten mit stop_duration > 5

print(trennung, "Anzahl der Duplikate in den Spalten stop_date und stop_time")
print(df[["stop_date", "stop_time"]].duplicated().sum()) # Anzahl der Duplikate


print(trennung)
alle_duplikate = df[df.duplicated(keep=False)]  # keep=False zeigt ALLE beteiligten Zeilen, nicht nur die "zusätzlichen"
print(alle_duplikate.shape[0])
print(alle_duplikate.sort_values(list(df.columns)).head(20))

# wie oft kommt jede Kombination vor?
print(alle_duplikate.groupby(list(df.columns)).size().value_counts())




# ============================================================
# SCHRITT 4: Fachliche Fragestellungen
# ============================================================

# Wichtiger Rahmen für b) bis e): Der Datensatz enthält ausschließlich Personen,
# die bereits kontrolliert wurden. Es gibt keine Vergleichsgruppe von Fahrern, die
# nicht verstoßen haben oder nicht angehalten wurden. "Wahrscheinlichkeit eines
# Verstoßes" im Sinne von "wer verstößt öfter" ist mit diesen Daten daher nicht
# testbar, dafür fehlt eine externe Baseline. Testbar ist nur, ob sich Merkmale
# zwischen den bereits erfassten Verstoßarten unterscheiden.

# a) Gibt es einen Zusammenhang zwischen dem Geschlecht des Fahrers und der Wahrscheinlichkeit, nach einer Kontrolle durchsucht zu werden?
# a).i) Bleibt dieser Zusammenhang innerhalb der einzelnen Verstoßkategorien bestehen?
# b) Unterscheidet sich das Alter der Fahrer zwischen den verschiedenen Verstoßarten (unter den bereits kontrollierten Personen)?
# c) Unterscheidet sich die Verteilung der Verstoßarten zwischen den Hautfarben der Fahrer (unter den bereits kontrollierten Personen)?
# d) Gibt es einen Zusammenhang zwischen einer drogenbezogenen Kontrolle (drugs_related_stop) und der Art des Verstoßes?
# e) Ist eine Kontrolle häufiger drogenbezogen, wenn der Verstoß ein Geschwindigkeitsverstoß (Speeding) war?
# f) Unterscheidet sich die Wahrscheinlichkeit eines Geschwindigkeitsverstoßes (Speeding) je nach Tageszeit der Kontrolle?


# ============================================================
# SCHRITT 5: Analyse der daten und Beantwortung der Fragestellungen
# ============================================================

# a)
# 1. Prozentuale Verteilung der Geschlechter im Datensatz (nur beschreibend, kein Test)
proportion_gender = df['driver_gender'].value_counts(normalize=True) * 100
print(trennung, "Prozentuale Verteilung der Geschlechter im Datensatz")
print(proportion_gender)

# 2. Chi-Quadrat-Test auf Unabhängigkeit: hängt Geschlecht mit der Durchsuchungswahrscheinlichkeit zusammen?
from scipy.stats import chi2_contingency
kontingenz_tabelle = pd.crosstab(df["driver_gender"], df["search_conducted"])
print(kontingenz_tabelle)
chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.5f}, Freiheitsgrade: {dof}")

#a).i) Chi-Quadrat-Test innerhalb der Verstoßkategorien
for verstoß in df['violation'].unique():
    teil = df[df['violation'] == verstoß]
    kontingenz_tabelle = pd.crosstab(teil["driver_gender"], teil["search_conducted"])
    print(f"Verstoß: {verstoß}")
    print(kontingenz_tabelle)
    chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
    print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.2e}, Freiheitsgrade: {dof}")




# ============================================================
# SCHRITT 6: Visualisierung der Ergebnisse
# ============================================================

# ============================================================
# SCHRITT 7: Dokumentation und Befunde
# ============================================================

# 1. Vorgenommene Datenbereinigung und -Aufbereitung
# Zwei auffällige stop_duration-Werte ('1', '2') wurden in Schritt 2 entfernt, da sie nicht zu den erwarteten Kategorien gehören.
# Zwolf auffällige Duplikate (Index 83361–83372) wurden in Schritt 2 entfernt, da es sich um exakt identische Personen handelte.
# stop_date und stop_time wurden in Schritt 2 in das Datetime-Format konvertiert, um eine bessere Analyse zu ermöglichen.
# is_arrested wurde in Schritt 2 in den booleschen Datentyp konvertiert, um die Analyse zu erleichtern.

# 2. Beantwortung der Fragestellungen
# a) Es besteht ein statistisch signifikanter Zusammenhang zwischen Geschlecht und der Wahrscheinlichkeit einer Durchsuchunge  bei einer Kontrolle
#.   Männer werden in diesem Datensatz etwa doppelt so oft durchsucht wie Frauen (4,33% vs. 2,00%)
#.   Der P wert liegt bei 0,00000, genauer 2,5 * 10^-58, was ein Zufallsergebnis praktisch ausgeschlossen macht.
#.   Grenzen des Befundes: Keine rückschlusse auf die Ursache möglich. Chi-Quadrat zeigt nur dass die Merkmale nicht unabhängig sind.
#.   Wenn man der Ursache näher kommen will, dann müssten man die Verstoßarten stratifizieren und prüfen.
#.   Besteht der Unterschied auch innerhalb der Verstoßkategorien?
#.
#. a).i)
#.   Der Unterschied bleibt innerhalb praktisch jeder Verstoßkategorie statistisch signifikant.
#.   Bei Speeding, Equipment, Moving violation, Registration/plates und Seat belt werden Männer jeweils deutlich häufiger durchsucht als Frauen, alle p Werte liegen unter 0,01.
#.   Einzige Ausnahme ist die Kategorie Other mit n gleich 4299, dort ist der Unterschied nicht signifikant, p gleich 0,32, und geht sogar leicht in die andere Richtung.
#.   Der Gesamteffekt lässt sich also nicht dadurch erklären, dass Männer und Frauen unterschiedliche Verstoßarten begehen, der Unterschied ist über die Kategorien hinweg robust.
#.   Bei sechs parallelen Tests sollte man das Mehrfachtests Problem mitdenken, hier ändert das aber nichts an der Schlussfolgerung, da alle p Werte weit unter einer Bonferroni korrigierten Schwelle von 0,0083 liegen.

# 3. Offen (Fragen b bis f noch nicht beantwortet, siehe README "Status")
