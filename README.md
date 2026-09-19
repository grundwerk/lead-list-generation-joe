# Kaeuferliste: von "wer koennte kaufen" zur Nummer im Telefon

Wer sein Unternehmen verkauft, braucht keine Liste von Firmen. Er braucht Menschen,
die ueber einen Zukauf entscheiden, mit einer Nummer, unter der sie rangehen.

Dieser Claude-Skill baut genau das. Du sagst, was du verkaufst und an wen du es
verkaufen willst. Am Ende liegt eine Excel-Datei da, sortiert nach Anrufbarkeit:
Name, Position, Firma, warum ausgerechnet diese Person, Direkt-Mail und Mobilnummer.

## Was dabei herauskommt

Eine Datei, drei Blaetter:

- **Anrufliste** - eine Zeile je Person, die mit Nummer oben. Von oben nach unten
  abtelefonieren.
- **Firmen** - welche Firmen in Frage kommen und warum, zum Nachschlagen im Gespraech.
- **Zusammenfassung** - wie viele Personen, wie viele anrufbar, was jede
  Anreicherungs-Quelle beigetragen hat.

## Wie es laeuft

```
  1  Kaeuferprofil klaeren        Gespraech mit Claude
  2  Firmen + LinkedIn-Seiten     Claude recherchiert
  3  Personen von LinkedIn        Apify
  4  Passung pruefen              Claude liest jedes Profil
  5  E-Mail + Nummer, Runde 1     BetterContact
  6  E-Mail + Nummer, Runde 2     Lusha
  7  Excel-Datei bauen
```

Nach jedem Schritt liegt eine Datei in `output/`. Man kann sie aufmachen, nachlesen
und den Lauf an jeder Stelle anhalten.

### Warum zwei Anbieter fuer dieselbe Sache

Weil sie nicht dieselben Leute finden. Wo der eine nichts hat, hat der andere oft
etwas. Beide zusammen sind der Unterschied zwischen einer halben und einer ganzen
Anrufliste. Am Ende steht in der Tabelle getrennt, wer was geliefert hat - nach
dreissig Anrufen weisst du, welcher Anbieter bei deiner Zielgruppe besser ist.

### Warum Claude die Personen selbst durchsieht

Nach dem Scrapen stehen Assistenzkraefte, Praktikanten und laengst ausgeschiedene
Leute in der Liste. Claude liest jedes Profil und entscheidet, ob die Person ueber
einen Zukauf mitentscheidet. Das kostet nichts ausser Nachdenken und halbiert die
Kosten der beiden Anreicherungsschritte, weil nur die Uebriggebliebenen angefragt
werden.

## Einrichten

Etwa fuenfzehn Minuten, einmalig. Die vollstaendige Anleitung steht in
**[SETUP.md](SETUP.md)** - dort sind auch die Links zu den drei Konten.

Kurzfassung:

```bash
git clone https://github.com/grundwerk/lead-list-generation-joe.git
cd lead-list-generation-joe
cp .env.example .env     # und die drei Schluessel eintragen
pip3 install openpyxl
claude
```

Dann in Claude Code einfach:

> Ich will mein Unternehmen verkaufen und brauche eine Kaeuferliste zum Anrufen.

Claude findet den Skill selbst und faengt mit den Fragen an.

## Was es kostet

Du zahlst bei drei Anbietern, jeweils nur fuer das, was du verbrauchst. Ein typischer
erster Lauf mit 60 Firmen:

| Wofuer | Ungefaehr |
|---|---|
| Apify, Personen von LinkedIn | 5 USD |
| BetterContact, E-Mail und Nummer | je gefundener Angabe, siehe Preisliste |
| Lusha, zweite Runde | je aufgedeckter Angabe, siehe Preisliste |

Apify rechnet je Profil ab, die beiden anderen **je gefundener Angabe** - wo nichts
gefunden wird, kostet es nichts. Jedes Skript rechnet die Obergrenze vor und fragt
nach, bevor es etwas ausgibt. Kein Schritt gibt ungefragt Geld aus.

## Was es nicht tut

- **Es ruft niemanden an und schreibt keine Mails.** Es baut die Liste. Das Gespraech
  fuehrst du, und das ist auch richtig so.
- **Es sagt nicht, was dein Unternehmen wert ist.**
- **Es findet keine Kaeufer ohne Internet-Spur.** Eine Holding ohne Website und ohne
  LinkedIn taucht hier nicht auf. Dafuer gibt es Berater und Branchenkontakte.
- **Es ersetzt keinen M&A-Berater**, wenn es ernst wird. Es bringt dich zu den
  Gespraechen, die du sonst nicht gefuehrt haettest.

## Datenschutz

Du verarbeitest Kontaktdaten echter Menschen. In der EU heisst das: es braucht einen
Grund (die Anbahnung eines konkreten Geschaefts ist einer), die Leute duerfen
widersprechen, und du musst sagen koennen, woher die Daten stammen. Deshalb bleiben
die Rohdateien in `output/` liegen - sie sind deine Antwort auf genau diese Frage.

Ein Anruf bei einer Firma zur Anbahnung eines Geschaefts steht rechtlich deutlich
besser da als eine Massenmail. Darum ist die Mobilnummer hier die Zielgroesse.

## Lizenz

MIT. Nimm es, aendere es, benutz es.

---

Gebaut von [Grundwerk Digital](https://grundwerk.digital).
