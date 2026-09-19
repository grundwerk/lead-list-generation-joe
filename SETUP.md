# Einrichten

Einmalig, etwa fuenfzehn Minuten. Danach laeuft jeder weitere Lauf ohne Einrichtung.

## 1. Claude Code

Wenn noch nicht vorhanden: https://claude.com/claude-code

## 2. Dieses Repo holen

```bash
git clone https://github.com/grundwerk/lead-list-generation-joe.git
cd lead-list-generation-joe
```

Der Skill liegt in `.claude/skills/` und wird von Claude Code automatisch gefunden,
sobald du in diesem Ordner `claude` startest.

## 3. Ein Python-Paket

```bash
pip3 install openpyxl
```

Das ist alles - alles andere laeuft mit dem, was Python mitbringt.

## 4. Die drei Konten

Alle drei rechnen nach Verbrauch ab. Kein Abo noetig, um anzufangen.

### Apify - holt die Personen von LinkedIn

Anmelden: https://www.apify.com?fpr=ggatm

Danach: **Settings -> Integrations -> API tokens**, Token kopieren.
Direkt: https://console.apify.com/settings/integrations

Apify braucht eine hinterlegte Zahlungsart, sonst bleibt der Lauf auf READY stehen,
ohne Fehlermeldung.

### BetterContact - E-Mail und Mobilnummer, Runde 1

Anmelden: https://bettercontact.rocks?fpr=gwd-1f7x

Danach: **API**, Schluessel kopieren.
Direkt: https://app.bettercontact.rocks/api_requests

BetterContact fragt hinter einer Anfrage viele Datenquellen nacheinander ab und
rechnet nur ab, was gefunden und geprueft wurde.

### Lusha - E-Mail und Mobilnummer, Runde 2

Anmelden: https://partnerstack.lusha.com/pdb9o1fn50bv

Danach im Dashboard unter **API** den Schluessel erzeugen.

Lusha ist die Gegenprobe. Es findet Leute, die BetterContact nicht hat.

## 5. Die Schluessel eintragen

```bash
cp .env.example .env
```

Dann `.env` oeffnen und die drei Werte eintragen. Die Datei steht in `.gitignore`
und landet nie auf GitHub.

```
APIFY_TOKEN=apify_api_...
BETTERCONTACT_API_KEY=...
LUSHA_API_KEY=...
```

## 6. Pruefen, ob alles sitzt

```bash
python3 .claude/skills/lead-list-generation-joe/scripts/pruefe_setup.py
```

Das Skript fragt bei allen drei Anbietern nach dem Kontostand. Es gibt kein Geld aus
und druckt keinen Schluessel. Drei gruene Haken heisst startklar.

## 7. Loslegen

```bash
claude
```

Und dann einfach sagen:

> Ich will mein Unternehmen verkaufen und brauche eine Kaeuferliste zum Anrufen.

Claude stellt die Fragen aus Schritt 1 und arbeitet sich durch.

---

## Wenn etwas klemmt

| Was passiert | Was es heisst |
|---|---|
| `APIFY_TOKEN fehlt` | `.env` liegt nicht im Repo-Wurzelverzeichnis oder die Zeile hat einen Tippfehler |
| Apify-Lauf bleibt auf READY | keine Zahlungsart im Apify-Konto hinterlegt |
| BetterContact antwortet `401` | Schluessel falsch. Er gehoert in `X-API-Key`, nicht als `Authorization: Bearer` |
| BetterContact antwortet `402` | Guthaben leer. Aufladen, Skript neu starten - schon abgeschickte Pakete werden nicht doppelt bezahlt |
| Lusha antwortet `429` | zu schnell gefragt. Das Skript wartet von selbst. Bei dauerhaftem 429 spaeter neu starten |
| `No module named openpyxl` | `pip3 install openpyxl` |

**Eine Datei niemals loeschen:** `output/04_bettercontact_state.json`. Darin steht,
welche Personen schon abgeschickt wurden. Ohne sie zahlt ein zweiter Lauf dieselben
Daten noch einmal.
