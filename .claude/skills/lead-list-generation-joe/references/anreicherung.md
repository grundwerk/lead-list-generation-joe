# Schritt 5 und 6: E-Mail und Mobilnummer

Zwei Anbieter, nacheinander. Sie finden nicht dieselben Leute. Wer nur einen nimmt,
laesst einen erheblichen Teil der erreichbaren Nummern liegen - deshalb laufen beide.

## BetterContact

Ein Wasserfall: hinter der einen Anfrage stecken viele Datenquellen, die
nacheinander befragt werden. Abgerechnet wird **je gefundener und geprueften
Angabe**, nicht je Anfrage und nicht je befragter Quelle. Wo nichts gefunden wird,
kostet es nichts.

| | |
|---|---|
| Basis | `https://app.bettercontact.rocks/api/v2` |
| Anmeldung | Kopfzeile `X-API-Key: <Schluessel>` |
| Losschicken | `POST /async`, hoechstens 100 Personen je Paket, antwortet mit `id` |
| Abholen | `GET /async/{id}` |
| Guthaben | `GET /account` |

Geprueft an der Anbieter-Doku am 19.09.2026: https://doc.bettercontact.rocks

### Die drei Fallen

**1. Es ist keine Kopfzeile `Authorization: Bearer`.** Der Schluessel gehoert in
`X-API-Key`. Anders geschickt kommt `401` zurueck.

**2. Ein `2xx` heisst nicht, dass Ergebnisse da sind.** Solange die Anreicherung
laeuft, antwortet der Abruf mit `202` und **ohne** Datenfeld. Viele Programme werten
jedes `2xx` als Erfolg, lesen das leere Feld und melden "nichts gefunden". Richtig
ist die Pruefung auf `status == "terminated"` - nur dieser Wert garantiert
Ergebnisse. Die anderen Werte: `not_started`, `processing`, `on_hold`.

**3. Zweimal abschicken kostet zweimal.** Das Losschicken ist nicht wiederhol-sicher.
Wer dieselben Personen erneut schickt, zahlt erneut. Darum merkt sich das Skript
jede Sendung in `output/04_bettercontact_state.json`. Wer diese Datei loescht und
neu startet, kauft dieselben Daten ein zweites Mal.

**Sonderfall `on_hold`:** das Guthaben ist mitten im Lauf leer geworden. Die Anfrage
ist **nicht** verloren. Aufladen, und sie laeuft von selbst weiter. Auf keinen Fall
neu abschicken - dann zahlt man die bereits bearbeiteten Personen doppelt.

### Was die Trefferquote hebt

- **Firmen-Domain statt Firmenname.** Deutlich besser, sagt der Anbieter selbst.
  Deshalb traegt Schritt 4 `firma_domain` ein.
- **LinkedIn-URL immer mitschicken**, und zwingend, wenn eine Mobilnummer gesucht wird.
- Vorname und Nachname sauber getrennt, keine Titel wie "Dr." im Vornamen.

## Lusha

Zweite Quelle, andere Datenbasis. Wird nach BetterContact angefragt, standardmaessig
nur fuer die Personen, bei denen dort etwas fehlt.

| | |
|---|---|
| Endpunkt | `GET https://api.lusha.com/v2/person` |
| Anmeldung | Kopfzeile `api_key: <Schluessel>` |
| Suchen ueber | `linkedinUrl`, oder `firstName` + `lastName` + `companyDomain` |
| Aufdecken | `revealEmails=true`, `revealPhones=true` |

Geprueft an der Anbieter-Doku am 19.09.2026: https://docs.lusha.com

Die **LinkedIn-URL ist der beste Schluessel** - sie ist eindeutig, ein Name plus
Firma ist es nicht. Das Skript nimmt sie immer, wenn sie da ist.

### Fallen

**Zu schnell gefragt.** Lusha bremst mit `429`. Das Skript wartet dann gestaffelt und
laesst eine kleine Pause zwischen den Anfragen (`--pause`). Bei dauerhaftem `429`
spaeter neu starten - schon angefragte Personen werden nicht erneut bezahlt.

**Die Antwort ist nicht immer gleich aufgebaut.** Lusha hat die Feldnamen ueber die
Jahre geaendert. Deshalb speichert das Skript **jede Antwort vollstaendig und roh** in
`05_lusha_raw.json` und liest die Werte nachsichtig heraus. Wenn in der Excel-Datei
etwas fehlt, das es geben muesste, steht es in der Rohdatei - und man muss nicht noch
einmal bezahlen, um es zu holen.

## Wie die beiden zusammenkommen

In der Excel-Datei stehen sie in **getrennten** Spalten. Zusaetzlich gibt es
"beste E-Mail" und "beste Nummer": dort steht BetterContact, und nur wo der nichts
hatte, Lusha.

Getrennt bleiben sie aus einem praktischen Grund: nach den ersten dreissig Anrufen
weisst du, welche Quelle bei deiner Zielgruppe besser liefert. Diese Erkenntnis ist
mehr wert als eine aufgeraeumte Tabelle - beim naechsten Lauf beginnst du mit dem
richtigen Anbieter.
