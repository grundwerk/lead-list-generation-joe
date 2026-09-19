# Die fertige Excel-Datei

`output/06_kaeuferliste.xlsx`, drei Blätter.

## Blatt 1: Anrufliste

Eine Zeile je Person. Sortiert: erst alle mit Mobilnummer, dann die mit nur E-Mail,
innerhalb der Gruppen nach Passung absteigend. Oben anfangen und nach unten
durcharbeiten.

| Spalte | Inhalt |
|---|---|
| `person_id` | laufende Nummer, verbindet die Zeile mit allen Rohdateien |
| `vorname`, `nachname` | getrennt, so wie man sie am Telefon braucht |
| `titel` | Position laut LinkedIn |
| `firma`, `firma_domain` | Arbeitgeber |
| `ort` | Standort laut LinkedIn |
| `passung_score` | 1 bis 10 aus Schritt 4 |
| `passung_begruendung` | warum diese Person, in einem Satz. **Das ist der Einstieg ins Gespräch.** |
| `beste_email` | BetterContact, sonst Lusha |
| `beste_nummer` | BetterContact, sonst Lusha |
| `anrufbar` | ja, wenn eine Nummer da ist |
| `email_bettercontact` | Rohwert Anbieter 1 |
| `nummer_bettercontact` | Rohwert Anbieter 1 |
| `email_lusha` | Rohwert Anbieter 2 |
| `nummer_lusha` | Rohwert Anbieter 2 |
| `linkedin_url` | Profil der Person, für den Blick vor dem Anruf |
| `firma_linkedin` | Firmenseite |

Kopfzeile fixiert, Filter gesetzt. Filtern auf `anrufbar = ja` gibt die Liste für
heute Nachmittag.

## Blatt 2: Firmen

Die Firmen aus `01_firmen.csv`, unverändert, mit der Begründung je Firma. Zum
Nachschlagen, wenn im Gespräch die Frage kommt, warum man ausgerechnet dort anruft.

## Blatt 3: Zusammenfassung

Was reinging, was rauskam, wo es verloren ging. Die wichtigste Zeile ist
**"davon mit Mobilnummer"** - das ist die Zahl, an der der ganze Lauf gemessen wird.

Die beiden Zeilen "Nummer nur von BetterContact" und "Nummer nur von Lusha" zeigen,
was der zweite Anbieter zusätzlich gebracht hat. Ist eine davon null, lohnt es sich,
beim nächsten Mal mit dem anderen anzufangen.
