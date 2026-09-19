---
name: lead-list-generation-joe
description: Baut eine anrufbare Kaeuferliste fuer den Verkauf eines Unternehmens. Findet passende Kaeufer-Firmen samt LinkedIn-Seite, scrapt ueber Apify die Entscheider dieser Firmen, prueft jede Person auf Passung und reichert E-Mail und Mobilnummer ueber BetterContact und Lusha an. Ergebnis ist eine Excel-Datei, die man von oben nach unten abtelefonieren kann. Ausloesen bei Kaeuferliste bauen, Kaeufer fuer mein Unternehmen finden, Exit-Liste, Anrufliste fuer den Verkauf, wer koennte meine Firma kaufen, lead list generation, Liste anreichern mit Telefonnummern.
---

# Kaeuferliste bauen

Du verkaufst dein Unternehmen und willst Kaeufer anrufen. Dieser Skill baut dafuer die
Liste: von der Frage "wer kaeme ueberhaupt in Frage" bis zur Excel-Datei mit Name,
Position, Direkt-Mail und Mobilnummer.

Sechs Schritte. Nach jedem liegt eine Datei in `output/`, die man aufmachen und
nachlesen kann. Nichts passiert im Verborgenen.

```
  1  Kaeuferprofil klaeren        Gespraech          ->  keine Datei, aber die Grundlage
  2  Firmen + LinkedIn-Seiten     Recherche          ->  01_firmen.csv
  3  Personen von LinkedIn        Apify              ->  02_personen.csv        (kostet)
  4  Passung pruefen              Claude liest       ->  03_personen_gefiltert.csv
  5  E-Mail + Nummer, Runde 1     BetterContact      ->  04_bettercontact_raw.json (kostet)
  6  E-Mail + Nummer, Runde 2     Lusha              ->  05_lusha_raw.json      (kostet)
  7  Alles zusammenfuehren        Excel              ->  06_kaeuferliste.xlsx
```

## Die eine Regel

**Das Ziel ist nicht eine lange Liste, sondern eine anrufbare.** Eine Zeile ohne
Mobilnummer ist beim Telefonieren wertlos, egal wie gut die Firma passt. Deshalb
misst dieser Skill den Erfolg an einer einzigen Zahl: **wie viele Personen haben am
Ende eine Nummer.** Alles andere ist Zwischenstand.

Realistische Erwartung: von den Entscheidern, die ueberhaupt durchlaufen, bekommen
etwa **30 bis 45 Prozent eine Mobilnummer**, E-Mail deutlich mehr. Wer 200 Leute
anrufen will, braucht also ungefaehr 500 gepruefte Personen im Trichter. Rechne von
hinten, nicht von vorne.

## Schritt 1 - Kaeuferprofil klaeren

**Nie ueberspringen.** Ohne dieses Gespraech recherchiert man 60 Firmen, von denen 50
nie gekauft haetten.

Die Fragen stehen in `references/kaeuferprofil.md`. Stelle sie alle, bevor du
irgendetwas suchst. Wenn eine Antwort fehlt, frag nach, statt zu raten.

Das Ergebnis ist ein kurzer Steckbrief, den du waehrend des ganzen Laufs sichtbar
haeltst - er ist der Massstab fuer jede spaetere Ja/Nein-Entscheidung.

## Schritt 2 - Firmen finden und die LinkedIn-Seite dazu

Recherchiere die Kaeufer-Firmen ueber die Websuche. Die Kaeufertypen und die
Suchwege stehen in `references/kaeuferprofil.md`.

Schreib das Ergebnis nach `output/01_firmen.csv` mit genau diesen Spalten:

| Spalte | Inhalt |
|---|---|
| `firma` | Name, so wie er im Handelsregister oder auf der Website steht |
| `domain` | nur die Domain, ohne https und ohne www |
| `linkedin_company_url` | die vollstaendige LinkedIn-Firmenseite |
| `typ` | welcher Kaeufertyp (strategisch, Beteiligung, Aggregator, ...) |
| `begruendung` | ein Satz: warum genau die Firma kaufen wuerde |

### Die teuerste Falle des ganzen Laufs

**Eine geratene LinkedIn-Firmen-URL macht den kompletten Rest wertlos.**
`linkedin.com/company/mustermann` sieht richtig aus und gehoert einer anderen Firma
mit aehnlichem Namen. Der Scraper holt dann brav deren Mitarbeiter, die Anreicherung
findet brav deren Nummern, und niemand merkt es - bis jemand am Telefon sagt, dass er
noch nie etwas von dir gehoert hat.

Deshalb gilt: **jede LinkedIn-URL wird geoeffnet und gegen die Domain geprueft.**
Stimmt die Website auf der LinkedIn-Seite nicht mit `domain` ueberein, lass das Feld
leer und schreib den Zweifel in `begruendung`. Eine leere Zelle kostet eine Firma.
Eine falsche kostet die Glaubwuerdigkeit beim ersten Anruf.

Sag am Ende von Schritt 2 laut, wie viele Firmen gefunden wurden und **bei wie vielen
die LinkedIn-Seite fehlt**. Beide Zahlen gehoeren zum Ergebnis.

## Schritt 3 - Personen von LinkedIn holen

```bash
python3 .claude/skills/lead-list-generation-joe/scripts/apify_employees.py \
    --pro-firma 8 \
    --seniority 220,300,310,320 \
    --titel "CEO,Geschaeftsfuehrer,Managing Director,M&A,Corporate Development,Head of Acquisitions,Investment Manager,Partner"
```

Das Skript zeigt die Obergrenze der Kosten und fragt nach, bevor es etwas ausgibt.
Details zu Filtern, Modi und Preisen: `references/apify.md`.

`--pro-firma` ist die Kostenbremse. Fang mit 5 bis 8 an. Lieber zweimal laufen lassen,
als beim ersten Mal 40 Assistenzkraefte je Konzern zu bezahlen.

## Schritt 4 - Passung pruefen

Jetzt liest **du** als Claude jede Person aus `02_personen.csv` und entscheidest, ob
sie zum Steckbrief aus Schritt 1 passt. Das kostet nichts ausser Nachdenken, und es
ist der Schritt, der die spaeteren Anreicherungskosten halbiert.

Je Person zwei Werte:

- `passung_score` von 1 bis 10
- `passung_begruendung`: ein Satz, warum. Kein "passt gut", sondern **die Rolle im
  Kaufprozess**: "entscheidet ueber Zukaeufe", "fuehrt die Pruefung durch",
  "traegt das Budget", "kennt den Markt, entscheidet aber nicht".

Was rausfliegt, ohne Diskussion:

- Praktikanten, Werkstudenten, Assistenz ohne eigene Entscheidung
- Leute, die laut Profil nicht mehr in der Firma sind
- Doppelte Eintraege derselben Person
- Alle unter deinem Score-Schwellwert. **Setz den Schwellwert, bevor du die Namen
  siehst**, sonst redest du dich bei jedem zweiten hoch.

Schreib die Ueberlebenden nach `output/03_personen_gefiltert.csv`. Spalten wie in
`02_personen.csv`, plus `firma_domain`, `passung_score`, `passung_begruendung`.

`firma_domain` ist wichtig: **BetterContact findet mit einer Domain deutlich mehr als
mit einem Firmennamen.** Die Domain steht schon in `01_firmen.csv` - uebertrag sie.

Sag danach, wie viele von wie vielen uebrig geblieben sind. Wenn fast alle
ueberleben, war der Filter zu weich.

## Schritt 5 und 6 - E-Mail und Mobilnummer

Zwei Anbieter, nacheinander, **nicht** wahlweise. Sie finden verschiedene Leute; erst
zusammen ergeben sie eine brauchbare Abdeckung. Wer nur einen nimmt, laesst rund ein
Drittel der erreichbaren Nummern liegen.

```bash
python3 .claude/skills/lead-list-generation-joe/scripts/bettercontact_enrich.py --email --telefon
python3 .claude/skills/lead-list-generation-joe/scripts/lusha_enrich.py
```

Lusha fragt standardmaessig nur die Personen an, bei denen BetterContact nicht beides
gefunden hat. Das spart Guthaben. `--alle` fragt alle an, wenn du zwei unabhaengige
Nummern je Person willst.

Die Fallen beider Anbieter stehen in `references/anreicherung.md`. Eine davon ist
wichtig genug fuer hier:

> **BetterContact ist nicht wiederhol-sicher.** Dieselben Personen ein zweites Mal
> abzuschicken kostet ein zweites Mal Geld. Das Skript merkt sich deshalb jede
> abgeschickte Sendung in `output/04_bettercontact_state.json`. **Diese Datei nicht
> loeschen**, auch nicht beim Aufraeumen.

> **Ein `2xx` heisst nicht, dass Ergebnisse da sind.** Waehrend die Anreicherung
> laeuft, antwortet BetterContact mit `202` und einem leeren Datenfeld. Wer nur auf
> "hat geklappt" prueft, liest das leere Feld und meldet "nichts gefunden". Geprueft
> wird auf `status == "terminated"`, nichts anderes. Das Skript macht das richtig -
> bau es nicht nach.

## Schritt 7 - Die Excel-Datei

```bash
python3 .claude/skills/lead-list-generation-joe/scripts/build_excel.py
```

Ergebnis: `output/06_kaeuferliste.xlsx`, drei Blaetter, Anrufbare oben.
Die Spalten stehen in `references/excel-format.md`.

Beide Anbieter stehen in **getrennten** Spalten, dazu je eine Spalte "beste E-Mail"
und "beste Nummer" zum direkten Arbeiten. Getrennt bleiben sie, damit man bei einer
falschen Nummer weiss, wer sie geliefert hat, und beim naechsten Mal anders gewichtet.

## Pflicht-Pruefung, bevor du die Datei uebergibst

Kein "fertig", bevor diese fuenf Punkte gemessen sind. Nicht geschaetzt, gemessen:

1. **Wie viele Zeilen haben eine Mobilnummer?** Steht im Blatt Zusammenfassung.
   Null Nummern ist fast nie richtig - dann ist ein Schritt nicht durchgelaufen.
2. **Stichprobe von fuenf Zeilen**: passt die Firma in der Zeile zur LinkedIn-URL
   der Person? Wenn nicht, war in Schritt 2 eine Firmen-URL falsch.
3. **Doppelte Personen?** Dieselbe Person bei zwei Firmen ist ein Treffer, dieselbe
   Person zweimal bei derselben Firma ist ein Fehler.
4. **Sehen die Nummern nach Mobilnummern aus?** Eine Zentrale hilft beim Verkaufs-
   gespraech nicht weiter.
5. **Stimmt die Zahl der Firmen** im Blatt Firmen mit dem ueberein, was du in
   Schritt 2 gemeldet hast?

Danach sagst du in **einem** Satz, was rauskam: wie viele Personen, wie viele
anrufbar, aus wie vielen Firmen.

## Was dieser Skill nicht tut

- **Er schreibt keine Mails und ruft niemanden an.** Er baut die Liste. Das Gespraech
  fuehrst du.
- **Er bewertet nicht, was dein Unternehmen wert ist.** Andere Aufgabe, andere Leute.
- **Er findet keine Kaeufer ohne Internet-Spur.** Eine Holding ohne Website und ohne
  LinkedIn taucht nicht auf. Das ist eine echte Luecke, keine Formsache - fuer solche
  Kaeufer bleiben Berater und Branchenkontakte.
- **Er ersetzt nicht den M&A-Berater**, wenn es ernst wird. Er bringt dich zu den
  Gespraechen, die du sonst nicht gefuehrt haettest.

## Datenschutz, kurz und ernst

Du verarbeitest Kontaktdaten echter Menschen. In der EU heisst das: es muss ein Grund
dafuer geben (berechtigtes Interesse an einer geschaeftlichen Anbahnung ist einer),
die Leute duerfen widersprechen, und du musst auf Nachfrage sagen koennen, woher die
Daten kommen. Deshalb bleiben die Rohdateien in `output/` liegen - sie sind deine
Antwort auf genau diese Frage.

Werbe-E-Mails an Privatpersonen ohne Einwilligung sind in Deutschland heikel. Ein
Anruf bei einer Firma zur Anbahnung eines konkreten Geschaefts steht deutlich besser
da als eine Massenmail. Genau darum ist die Mobilnummer hier die Zielgroesse.
