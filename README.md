# Käuferliste: von "wer könnte kaufen" zur Nummer im Telefon

Wer sein Unternehmen verkauft, braucht keine Liste von Firmen. Er braucht Menschen,
die über einen Zukauf entscheiden, mit einer Nummer, unter der sie rangehen.

Dieser Claude-Skill baut genau das. Du sagst, was du verkaufst und an wen du es
verkaufen willst. Am Ende liegt eine Excel-Datei da, sortiert nach Anrufbarkeit:
Name, Position, Firma, warum ausgerechnet diese Person, Direkt-Mail und Mobilnummer.

## Was dabei herauskommt

Eine Datei, drei Blätter:

- **Anrufliste** - eine Zeile je Person, die mit Nummer oben. Von oben nach unten
  abtelefonieren.
- **Firmen** - welche Firmen in Frage kommen und warum, zum Nachschlagen im Gespräch.
- **Zusammenfassung** - wie viele Personen, wie viele anrufbar, was jede
  Anreicherungs-Quelle beigetragen hat.

## Wie es läuft

```
  1  Käuferprofil klären          Gespräch mit Claude
  2  Firmen + LinkedIn-Seiten     Claude recherchiert
  3  Personen von LinkedIn        Apify
  4  Passung prüfen               Claude liest jedes Profil
  5  E-Mail + Nummer, Runde 1     BetterContact
  6  E-Mail + Nummer, Runde 2     Lusha
  7  Excel-Datei bauen
```

Nach jedem Schritt liegt eine Datei in `output/`. Man kann sie aufmachen, nachlesen
und den Lauf an jeder Stelle anhalten.

### Warum zwei Anbieter für dieselbe Sache

Weil sie nicht dieselben Leute finden. Wo der eine nichts hat, hat der andere oft
etwas. Beide zusammen sind der Unterschied zwischen einer halben und einer ganzen
Anrufliste. Am Ende steht in der Tabelle getrennt, wer was geliefert hat - nach
dreissig Anrufen weisst du, welcher Anbieter bei deiner Zielgruppe besser ist.

### Warum Claude die Personen selbst durchsieht

Nach dem Scrapen stehen Assistenzkräfte, Praktikanten und längst ausgeschiedene
Leute in der Liste. Claude liest jedes Profil und entscheidet, ob die Person über
einen Zukauf mitentscheidet. Das kostet nichts ausser Nachdenken und halbiert die
Kosten der beiden Anreicherungsschritte, weil nur die Uebriggebliebenen angefragt
werden.

## Einrichten

Etwa fünfzehn Minuten, einmalig. Die vollständige Anleitung steht in
**[SETUP.md](SETUP.md)** - dort sind auch die Links zu den drei Konten.

Kurzfassung:

```bash
git clone https://github.com/grundwerk/lead-list-generation-joe.git
cd lead-list-generation-joe
cp .env.example .env     # und die drei Schlüssel eintragen
pip3 install openpyxl
claude
```

Dann in Claude Code einfach:

> Ich will mein Unternehmen verkaufen und brauche eine Käuferliste zum Anrufen.

Claude findet den Skill selbst und fängt mit den Fragen an.

## Was es kostet

Du zahlst bei drei Anbietern, jeweils nur für das, was du verbrauchst. Ein typischer
erster Lauf mit 60 Firmen:

| Wofür | Ungefähr |
|---|---|
| Apify, Personen von LinkedIn | 5 USD |
| BetterContact, E-Mail und Nummer | je gefundener Angabe, siehe Preisliste |
| Lusha, zweite Runde | je aufgedeckter Angabe, siehe Preisliste |

Apify rechnet je Profil ab, die beiden anderen **je gefundener Angabe** - wo nichts
gefunden wird, kostet es nichts. Jedes Skript rechnet die Obergrenze vor und fragt
nach, bevor es etwas ausgibt. Kein Schritt gibt ungefragt Geld aus.

## Was es nicht tut

- **Es ruft niemanden an und schreibt keine Mails.** Es baut die Liste. Das Gespräch
  führst du, und das ist auch richtig so.
- **Es sagt nicht, was dein Unternehmen wert ist.**
- **Es findet keine Käufer ohne Internet-Spur.** Eine Holding ohne Website und ohne
  LinkedIn taucht hier nicht auf. Dafür gibt es Berater und Branchenkontakte.
- **Es ersetzt keinen M&A-Berater**, wenn es ernst wird. Es bringt dich zu den
  Gesprächen, die du sonst nicht geführt hättest.

## Datenschutz

Du verarbeitest Kontaktdaten echter Menschen. In der EU heißt das: es braucht einen
Grund (die Anbahnung eines konkreten Geschäfts ist einer), die Leute dürfen
widersprechen, und du musst sagen können, woher die Daten stammen. Deshalb bleiben
die Rohdateien in `output/` liegen - sie sind deine Antwort auf genau diese Frage.

Ein Anruf bei einer Firma zur Anbahnung eines Geschäfts steht rechtlich deutlich
besser da als eine Massenmail. Darum ist die Mobilnummer hier die Zielgröße.

## Lizenz

MIT. Nimm es, ändere es, benutz es.

---

Gebaut von [Grundwerk Digital](https://grundwerk.digital).
