import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import os

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

# Zwolf eindeutige Duplikate Raus mit dem Index (83361 bis 83372)
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

# a).i) Chi-Quadrat-Test innerhalb der Verstoßkategorien
for verstoß in df['violation'].unique():
    teil = df[df['violation'] == verstoß]
    kontingenz_tabelle = pd.crosstab(teil["driver_gender"], teil["search_conducted"])
    print(f"Verstoß: {verstoß}")
    print(kontingenz_tabelle)
    chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
    print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.2e}, Freiheitsgrade: {dof}")

# b) Unterschiede im Alter der Fahrer zwischen den Verstoßarten
# erstmal ein Schiefe-Test
print(trennung, "Schiefe der Altersverteilung")
print(stats.skew(df["driver_age"], nan_policy='omit'))  # Schiefe der Altersverteilung

for verstoß in df['violation'].unique():
    teil = df[df['violation'] == verstoß]
    print(f"Verstoß: {verstoß}, Durchschnittsalter: {teil['driver_age'].mean():.2f}, Standardabweichung: {teil['driver_age'].std():.2f}")

# Kruskal-Wallis-Test auf Unterschiede im Alter der Fahrer zwischen den Verstoßarten
from scipy.stats import kruskal
gruppen = [teil['driver_age'].dropna() for _, teil in df.groupby('violation')]
h_stat, p_value = kruskal(*gruppen)
print(f"Kruskal-Wallis H-Statistik: {h_stat:.2f}, p-Wert: {p_value:.5f}")

# c) Unterschiede in der Verteilung der Verstoßarten zwischen den Hautfarben der Fahrer
kontingenz_tabelle = pd.crosstab(df["driver_race"], df["violation"])
normalisierte_tabelle = kontingenz_tabelle.div(kontingenz_tabelle.sum(axis=1), axis=0)
print(trennung, "Kontingenztabelle der Verstoßarten nach Hautfarbe")
print(normalisierte_tabelle)
chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.5f}, Freiheitsgrade: {dof}")      
n = kontingenz_tabelle.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(kontingenz_tabelle.shape) - 1)))
print(f"Cramer's V: {cramers_v:.3f}")

# d) Zusammenhang zwischen drogenbezogener Kontrolle und Art des Verstoßes
anteil_drogen = df.groupby('violation')['drugs_related_stop'].mean() * 100
print(trennung, "Anteil drogenbezogener Kontrollen nach Verstoßart")
print(anteil_drogen.sort_values(ascending=False))

kontingenz_tabelle = pd.crosstab(df["violation"], df["drugs_related_stop"])
chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.2e}, Freiheitsgrade: {dof}")
n = kontingenz_tabelle.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(kontingenz_tabelle.shape) - 1)))
print(f"Cramer's V: {cramers_v:.3f}")

# e) Häufigkeit drogenbezogener Kontrollen bei Geschwindigkeitsverstößen
df['ist_speeding'] = df['violation'] == 'Speeding'
kontingenz_tabelle = pd.crosstab(df['ist_speeding'], df['drugs_related_stop'])
print(kontingenz_tabelle)
chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.5f}, Freiheitsgrade: {dof}")  

n = kontingenz_tabelle.values.sum()
cramers_v = (chi2 / (n * (min(kontingenz_tabelle.shape) - 1))) ** 0.5
print(f"Cramer's V: {cramers_v:.3f}")

quote_speeding = df[df['ist_speeding']]['drugs_related_stop'].mean() * 100
quote_rest = df[~df['ist_speeding']]['drugs_related_stop'].mean() * 100
print(f"Anteil drogenbezogener Kontrollen bei Geschwindigkeitsverstößen: {quote_speeding:.2f}%")
print(f"Anteil drogenbezogener Kontrollen bei anderen Verstößen: {quote_rest:.2f}%")

# f) Unterschiede in der Wahrscheinlichkeit eines Geschwindigkeitsverstoßes jeden nach Tageszeiten 
def tageszeit(stunde):
    if 5 <= stunde < 12:
        return 'Morgen'
    elif 12 <= stunde < 18:
        return 'Nachmittag'
    elif 18 <= stunde < 22:
        return 'Abend'
    else:
        return 'Nacht'

df['tageszeit'] = df['stop_time'].apply(lambda zeit: tageszeit(zeit.hour))

anteil_speeding = df.groupby('tageszeit')['ist_speeding'].mean() * 100
print(trennung, "Anteil Speeding-Verstöße nach Tageszeit")
print(anteil_speeding.sort_values(ascending=False))

kontingenz_tabelle = pd.crosstab(df['tageszeit'], df['ist_speeding'])
chi2, p, dof, expected = chi2_contingency(kontingenz_tabelle)
print(f"Chi-Quadrat-Wert: {chi2:.2f}, p-Wert: {p:.5f}, Freiheitsgrade: {dof}")
n = kontingenz_tabelle.values.sum()
cramers_v = (chi2 / (n * (min(kontingenz_tabelle.shape) - 1))) ** 0.5
print(f"Cramer's V: {cramers_v:.3f}")




# ============================================================
# SCHRITT 6: Visualisierung der Ergebnisse
# ============================================================

os.makedirs("assets", exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")

# b) Boxplot: Altersverteilung je Verstoßart
reihenfolge_alter = df.groupby('violation')['driver_age'].median().sort_values(ascending=False).index
daten_alter = [df.loc[df['violation'] == v, 'driver_age'].dropna() for v in reihenfolge_alter]
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(daten_alter, tick_labels=reihenfolge_alter)
ax.set_title("Altersverteilung nach Verstoßart")
ax.set_ylabel("Alter der Fahrer")
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig("assets/alter_nach_verstossart.png", dpi=150)
plt.close()

# c) Balkendiagramm: Anteil Speeding an allen Verstößen je Hautfarbe
anteil_speeding_rasse = (df['violation'] == 'Speeding').groupby(df['driver_race']).mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(7, 5))
anteil_speeding_rasse.plot(kind='bar', ax=ax, color='#4C72B0')
ax.set_title("Anteil Speeding an allen Verstößen nach Hautfarbe")
ax.set_xlabel("")
ax.set_ylabel("Anteil Speeding (%)")
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig("assets/speeding_anteil_nach_hautfarbe.png", dpi=150)
plt.close()

# f) Balkendiagramm: Anteil Speeding je Tageszeit (chronologisch sortiert)
reihenfolge_tageszeit = ['Morgen', 'Nachmittag', 'Abend', 'Nacht']
fig, ax = plt.subplots(figsize=(6, 5))
anteil_speeding.reindex(reihenfolge_tageszeit).plot(kind='bar', ax=ax, color='#55A868')
ax.set_title("Anteil Speeding an allen Verstößen nach Tageszeit")
ax.set_xlabel("")
ax.set_ylabel("Anteil Speeding (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("assets/speeding_anteil_nach_tageszeit.png", dpi=150)
plt.close()

# ============================================================
# SCHRITT 7: Dokumentation und Befunde
# ============================================================

# 1. Vorgenommene Datenbereinigung und -Aufbereitung
# Zwei auffällige stop_duration-Werte ('1', '2') wurden in Schritt 2 entfernt, da sie nicht zu den erwarteten Kategorien gehören.
# Zwolf auffällige Duplikate (Index 83361 bis 83372) wurden in Schritt 2 entfernt, da es sich um exakt identische Personen handelte.
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
#.
#. b) Das Alter der Fahrer unterscheidet sich statistisch signifikant zwischen den Verstoßarten.
#.   Getestet mit Kruskal-Wallis statt ANOVA, weil die Altersverteilung mit einer Schiefe von 0,84 spürbar rechtsschief ist und die Normalverteilungsannahme der ANOVA damit verletzt wäre.
#.   H gleich 1721,72, p praktisch 0.
#.   Fahrer bei "Other"-Verstößen sind im Median am ältesten (39 Jahre), bei Equipment und Seat belt am jüngsten (Median 28 bzw. 29 Jahre), siehe Boxplot in Schritt 6.
#.   Grenzen: Der Test zeigt nur, dass sich irgendwo ein Unterschied befindet, nicht zwischen welchen Paaren genau, dafür bräuchte es einen Post-hoc-Test wie den Dunn-Test.
#.
#. c) Es gibt einen statistisch signifikanten, aber inhaltlich schwachen Zusammenhang zwischen Hautfarbe und Verstoßart.
#.   Chi-Quadrat gleich 4712,07, p praktisch 0, 20 Freiheitsgrade, Cramers V gleich 0,117, nach gängiger Einordnung ein schwacher Effekt.
#.   Deutlichster Unterschied: Speeding macht bei Asian- (67,5%) und White-Fahrern (62,2%) den größten Teil aller Verstöße aus, bei Hispanic- (32,5%) und Black-Fahrern (41,2%) liegt der Anteil deutlich niedriger, dort fallen Moving violation und Equipment stärker ins Gewicht.
#.   Grenzen: Chi-Quadrat zeigt nur, dass die Verteilungen nicht unabhängig sind, keine Aussage über die Ursache, zum Beispiel sind unterschiedliche Kontrollorte oder -anlässe je Gruppe hier nicht kontrolliert.
#.
#. d) Es gibt einen statistisch signifikanten, aber sehr schwachen Zusammenhang zwischen Verstoßart und drogenbezogener Kontrolle.
#.   Chi-Quadrat gleich 308,75, p gleich 1,32 mal 10 hoch minus 64, 5 Freiheitsgrade, Cramers V gleich 0,060.
#.   Der Anteil drogenbezogener Kontrollen ist bei Equipment am höchsten (1,96%) und bei Speeding am niedrigsten (0,49%), ein Faktor 4 Unterschied bei insgesamt niedriger Basisrate (0,89% über den gesamten Datensatz).
#.
#. e) Nein, im Gegenteil: Speeding-Kontrollen sind seltener drogenbezogen als andere Verstöße, nicht häufiger.
#.   Anteil bei Speeding 0,49% gegenüber 1,53% bei allen anderen Verstößen, Chi-Quadrat gleich 246,20, p praktisch 0, Cramers V gleich 0,053.
#.   Macht auch fachlich Sinn: Speeding wird häufig durch Radar ausgelöst, ohne vorherigen Verdacht, während andere Verstöße öfter im Rahmen einer bereits verdachtsbegründeten Kontrolle auffallen.
#.
#. f) Die Wahrscheinlichkeit eines Geschwindigkeitsverstoßes unterscheidet sich statistisch signifikant nach Tageszeit.
#.   Chi-Quadrat gleich 542,13, p praktisch 0, 3 Freiheitsgrade, Cramers V gleich 0,079.
#.   Speeding-Anteil ist morgens am höchsten (60,4%) und nachmittags am niedrigsten (50,6%), ein Unterschied von etwa 10 Prozentpunkten, siehe Balkendiagramm in Schritt 6.
#.
#. Durchgängiges Muster bei c) bis f): Bei rund 86.000 Fällen wird praktisch jeder Zusammenhang statistisch signifikant, auch wenn er inhaltlich klein ist. Cramers V ordnet das ein, alle vier Effekte liegen im schwachen Bereich (0,05 bis 0,12). Der p-Wert allein hätte hier ein falsches Bild von der Größe der Effekte gegeben.

# 3. Visualisierung
# Drei Diagramme in Schritt 6 gespeichert (Ordner assets/):
# alter_nach_verstossart.png (b), speeding_anteil_nach_hautfarbe.png (c), speeding_anteil_nach_tageszeit.png (f).
