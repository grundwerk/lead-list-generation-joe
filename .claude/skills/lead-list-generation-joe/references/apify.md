# Schritt 3: die Personen von LinkedIn holen

## Der Actor

`harvestapi/linkedin-company-employees`
https://apify.com/harvestapi/linkedin-company-employees

Er nimmt LinkedIn-Firmenseiten und gibt die Mitarbeiter zurueck, optional nach
Jobtitel, Seniority und Ort gefiltert. Er braucht keinen LinkedIn-Zugang und keine
Cookies - das ist der Grund fuer genau diesen Actor.

## Was das Skript schickt

| Feld | Wert | Warum |
|---|---|---|
| `companies` | die URLs aus `01_firmen.csv` | die Eingabe |
| `profileScraperMode` | `Full ($8 per 1k)` | genug Profiltext, damit Schritt 4 wirklich entscheiden kann |
| `companyBatchMode` | `one_by_one` | siehe unten |
| `maxItemsPerCompany` | `--pro-firma` | die Kostenbremse |
| `maxItems` | Firmen x pro-Firma | zweite Bremse, falls die erste ins Leere greift |
| `jobTitles` | `--titel` | optional |
| `seniorityLevelIds` | `--seniority` | optional |
| `locations` | `--orte` | optional |

### Warum eine Abfrage je Firma und nicht eine grosse

`all_at_once` sucht ueber alle Firmen zusammen. Dann frisst der groesste Konzern die
Obergrenze auf, und die zwanzig kleinen Kandidaten kommen mit null Personen zurueck -
ohne Fehlermeldung, es sieht einfach nach "da war nichts" aus.

`one_by_one` kostet die Startgebuehr je Firma, rund zwei Cent, und garantiert dafuer,
dass jede Firma drankommt. Bei sechzig Firmen ist das gut ein Dollar Aufpreis fuer
ein Ergebnis, das nicht still schief liegt.

## Seniority-Nummern

Die relevanten fuer eine Kaeuferliste:

| ID | Stufe |
|---|---|
| 220 | Director |
| 300 | Vice President |
| 310 | CXO |
| 320 | Inhaber, Partner |

`--seniority 220,300,310,320` ist der uebliche Zuschnitt. Bei kleinen Firmen und
Family Offices ruhig weglassen - dort tragen die Entscheider oft gar keinen dieser
Titel, und der Filter wirft sie dann heraus.

## Kosten

Stand 19.09.2026, laut Actor-Seite. Die verbindliche Zahl steht immer dort, nicht hier.

| Modus | Preis je 1.000 Profile |
|---|---|
| Short | rund 4 USD |
| Full | rund 8 USD |
| Full + E-Mail-Suche | rund 12 USD |

Dazu rund 2 Cent Startgebuehr je Abfrage, also je Firma.

**Die E-Mail-Suche wird hier nie benutzt.** Sie ist der teuerste Modus und liefert
schlechtere Adressen als BetterContact und Lusha, die genau dafuer gebaut sind.

Beispiel: 60 Firmen, je hoechstens 8 Personen, Modus Full
= 60 x 0,02 USD Start + hoechstens 480 x 0,008 USD
= hoechstens rund 5,00 USD.

Das Skript rechnet das vor und fragt nach, bevor es laeuft.

## Fallen

**Eine Firma liefert null Personen.** Meist kein Fehler, sondern ein zu enger Filter:
`jobTitles` verlangt eine Titel-Schreibweise, die es dort nicht gibt. Erst ohne
Titel-Filter erneut versuchen, bevor man die Firma aufgibt.

**Eine Firma liefert hundert Personen.** Dann war `--pro-firma` zu hoch oder der
Seniority-Filter fehlt. Abbrechen, enger stellen, neu starten.

**Der Lauf steht auf READY und bewegt sich nicht.** Das Apify-Konto hat kein Guthaben
oder keine hinterlegte Zahlung. Steht im Dashboard, nicht in der Antwort des Skripts.

**Die Rohdatei nicht loeschen.** `02_personen_raw.json` enthaelt mehr Felder als die
CSV. Wenn spaeter etwas fehlt, steht es dort drin - ein zweiter Lauf wuerde noch
einmal kosten.
