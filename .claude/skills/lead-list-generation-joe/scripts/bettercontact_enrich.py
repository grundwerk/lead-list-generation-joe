#!/usr/bin/env python3
"""Schritt 4: E-Mail und Mobilnummer über BetterContact holen.

Liest output/03_personen_gefiltert.csv, schickt die Personen in Paketen zu 100 los
und holt die Ergebnisse ab. Legt jede Antwort roh ab.

Die eine Falle, die hier Geld kostet: BetterContact ist NICHT wiederhol-sicher.
Ein zweites Abschicken derselben Personen zahlt zweimal. Deshalb merkt sich dieses
Skript jede Paket-Nummer in output/04_bettercontact_state.json und schickt ein bereits
abgeschicktes Paket nie erneut los. Diese Datei nicht löschen.

Beispiel:
  python3 scripts/bettercontact_enrich.py --telefon --email
"""
import argparse
import csv
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import OUT, confirm, die, http, need, read_json, write_json  # noqa: E402

BASIS = "https://app.bettercontact.rocks/api/v2"
PAKET = 100


def domain_von(wert):
    w = (wert or "").strip().lower()
    for p in ("https://", "http://", "www."):
        if w.startswith(p):
            w = w[len(p):]
    return w.split("/")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--personen", default=str(OUT / "03_personen_gefiltert.csv"))
    ap.add_argument("--email", action="store_true", help="E-Mail-Adressen suchen.")
    ap.add_argument("--telefon", action="store_true", help="Mobilnummern suchen.")
    ap.add_argument("--ja", action="store_true")
    a = ap.parse_args()
    if not a.email and not a.telefon:
        a.email = a.telefon = True

    key = need("BETTERCONTACT_API_KEY")

    with open(a.personen, newline="", encoding="utf-8-sig") as f:
        personen = [r for r in csv.DictReader(f)]
    if not personen:
        die(f"{a.personen} ist leer. Erst Schritt 3 (Passung prüfen) abschließen.")

    fehlend = [p.get("person_id") for p in personen
               if not (p.get("vorname") and p.get("nachname")
                       and (p.get("firma_domain") or p.get("linkedin_url")))]
    if fehlend:
        print(f"WARNUNG: {len(fehlend)} Personen ohne Vorname+Nachname und ohne Firmen-Domain "
              f"oder LinkedIn-URL. BetterContact findet dazu nichts. Sie laufen trotzdem mit, "
              f"kosten aber nur, wenn etwas gefunden wird.")

    st, konto = http("GET", f"{BASIS}/account", headers={"X-API-Key": key})
    if st == 401:
        die("BetterContact lehnt den Schlüssel ab (401). Er gehört in den Header X-API-Key, "
            "nicht als Authorization: Bearer.")
    guthaben = konto.get("credits_left")

    pakete = [personen[i:i + PAKET] for i in range(0, len(personen), PAKET)]
    zustand = read_json(OUT / "04_bettercontact_state.json", {"pakete": {}})

    offen = [i for i in range(len(pakete)) if str(i) not in zustand["pakete"]]
    text = (
        f"\nBetterContact\n"
        f"  Personen:      {len(personen)}\n"
        f"  Pakete:        {len(pakete)} (je höchstens {PAKET})\n"
        f"  davon neu:     {len(offen)} - der Rest wurde früher schon abgeschickt und wird nur abgeholt\n"
        f"  Gesucht wird:  {'E-Mail ' if a.email else ''}{'Mobilnummer' if a.telefon else ''}\n"
        f"  Guthaben:      {guthaben if guthaben is not None else 'nicht auslesbar'}\n"
        f"  Abgerechnet wird je gefundener Angabe, nicht je Anfrage. Wo nichts gefunden\n"
        f"  wird, kostet es nichts.\n"
    )
    if not confirm(text, a.ja):
        return

    for i, paket in enumerate(pakete):
        schluessel = str(i)
        if schluessel in zustand["pakete"]:
            print(f"Paket {i + 1}/{len(pakete)}: lief schon, Nummer {zustand['pakete'][schluessel]['id']}")
            continue
        daten = []
        for p in paket:
            eintrag = {
                "first_name": p.get("vorname", ""),
                "last_name": p.get("nachname", ""),
                "custom_fields": {"person_id": p.get("person_id", "")},
            }
            dom = domain_von(p.get("firma_domain", ""))
            if dom:
                eintrag["company_domain"] = dom
            elif p.get("firma"):
                eintrag["company"] = p["firma"]
            if p.get("linkedin_url"):
                eintrag["linkedin_url"] = p["linkedin_url"]
            daten.append(eintrag)

        st, res = http("POST", f"{BASIS}/async", headers={"X-API-Key": key}, body={
            "enrich_email_address": bool(a.email),
            "enrich_phone_number": bool(a.telefon),
            "data": daten,
        })
        if st == 402:
            die("BetterContact hat kein Guthaben mehr (402). Aufladen, dann dieses Skript "
                "erneut starten - die bereits abgeschickten Pakete werden nicht doppelt bezahlt.")
        if st not in (200, 201):
            die(f"Paket {i + 1} wurde nicht angenommen (HTTP {st}): {res}")
        zustand["pakete"][schluessel] = {"id": res.get("id"), "anzahl": len(daten)}
        write_json(OUT / "04_bettercontact_state.json", zustand)
        print(f"Paket {i + 1}/{len(pakete)}: abgeschickt, Nummer {res.get('id')}")

    print("\nWarte auf die Ergebnisse. Das dauert je Paket ein bis einige Minuten.")
    alle = []
    for schluessel, info in sorted(zustand["pakete"].items(), key=lambda x: int(x[0])):
        rid = info["id"]
        beginn = time.time()
        while True:
            st, body = http("GET", f"{BASIS}/async/{rid}", headers={"X-API-Key": key})
            status = body.get("status")
            # Entscheidend: auf status prüfen, nicht auf den HTTP-Code. Ein 202 ist
            # "läuft noch" und hat ein leeres data-Feld. Wer nur auf 2xx prüft, liest
            # das leere Feld und glaubt, es sei nichts gefunden worden.
            if status == "terminated":
                alle.extend(body.get("data", []))
                print(f"  Paket {int(schluessel) + 1}: fertig, {len(body.get('data', []))} Zeilen")
                break
            if status == "on_hold":
                die(f"Paket {int(schluessel) + 1} hängt: das Guthaben ist mitten im Lauf leer "
                    f"geworden. Aufladen, dann läuft es von selbst weiter. NICHT neu abschicken.")
            if time.time() - beginn > 1800:
                die(f"Paket {int(schluessel) + 1} ist nach 30 Minuten noch nicht fertig "
                    f"(Zustand: {status}). Später dieses Skript erneut starten, "
                    f"die Pakete werden dann nur abgeholt.")
            time.sleep(15)

    write_json(OUT / "04_bettercontact_raw.json", alle)
    mit_mail = sum(1 for r in alle if r.get("contact_email_address"))
    mit_tel = sum(1 for r in alle if r.get("contact_phone_number"))
    print(f"\nGespeichert: output/04_bettercontact_raw.json")
    print(f"  Zeilen:       {len(alle)}")
    print(f"  mit E-Mail:   {mit_mail}")
    print(f"  mit Nummer:   {mit_tel}")


if __name__ == "__main__":
    main()
