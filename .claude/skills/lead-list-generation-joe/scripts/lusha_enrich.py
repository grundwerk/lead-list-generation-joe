#!/usr/bin/env python3
"""Schritt 5: zweite Anreicherungs-Runde über Lusha.

Lusha ist die Gegenprobe zu BetterContact. Die beiden finden nicht dieselben Leute:
wo der eine nichts hat, hat der andere oft etwas. Deshalb laufen beide, und beide
Ergebnisse stehen am Ende in getrennten Spalten nebeneinander.

Standardmäßig werden nur die Personen angefragt, bei denen BetterContact NICHTS
gefunden hat. Das spart Guthaben. Mit --alle laufen alle Personen durch.

Jede Antwort wird roh gespeichert, und jede schon angefragte Person steht in
output/05_lusha_state.json. Ein zweiter Lauf fragt sie nicht erneut an.

Beispiel:
  python3 scripts/lusha_enrich.py
  python3 scripts/lusha_enrich.py --alle
"""
import argparse
import csv
import sys
import time
import urllib.parse

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import OUT, confirm, die, http, need, read_json, write_json  # noqa: E402

BASIS = "https://api.lusha.com/v2/person"


def domain_von(wert):
    w = (wert or "").strip().lower()
    for p in ("https://", "http://", "www."):
        if w.startswith(p):
            w = w[len(p):]
    return w.split("/")[0]


def treffer_aus(body):
    """Liest E-Mails und Nummern aus der Antwort heraus. Bewusst nachsichtig geschrieben:
    Lusha hat die Feldnamen über die Jahre geändert, und die Rohantwort liegt ohnehin
    vollständig in der Datei - wenn hier etwas fehlt, ist es nicht verloren."""
    daten = body.get("data", body) or {}
    if isinstance(daten, list):
        daten = daten[0] if daten else {}
    mails, nummern = [], []
    for schluessel in ("emailAddresses", "emails", "email_addresses"):
        for e in daten.get(schluessel, []) or []:
            wert = e.get("email") or e.get("emailAddress") if isinstance(e, dict) else e
            if wert:
                mails.append(wert)
    for schluessel in ("phoneNumbers", "phones", "phone_numbers"):
        for t in daten.get(schluessel, []) or []:
            wert = t.get("number") or t.get("internationalNumber") if isinstance(t, dict) else t
            if wert:
                nummern.append(wert)
    return mails, nummern


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--personen", default=str(OUT / "03_personen_gefiltert.csv"))
    ap.add_argument("--alle", action="store_true",
                    help="Alle Personen anfragen, nicht nur die ohne BetterContact-Treffer.")
    ap.add_argument("--pause", type=float, default=0.6, help="Sekunden zwischen zwei Anfragen.")
    ap.add_argument("--ja", action="store_true")
    a = ap.parse_args()

    key = need("LUSHA_API_KEY")

    with open(a.personen, newline="", encoding="utf-8-sig") as f:
        personen = [r for r in csv.DictReader(f)]
    if not personen:
        die(f"{a.personen} ist leer.")

    bc = read_json(OUT / "04_bettercontact_raw.json", [])
    schon_gefunden = set()
    for zeile in bc:
        pid = (zeile.get("custom_fields") or {}).get("person_id")
        if pid and zeile.get("contact_email_address") and zeile.get("contact_phone_number"):
            schon_gefunden.add(pid)

    zustand = read_json(OUT / "05_lusha_state.json", {"fertig": {}})
    todo = []
    for p in personen:
        pid = p.get("person_id", "")
        if pid in zustand["fertig"]:
            continue
        if not a.alle and pid in schon_gefunden:
            continue
        if not (p.get("linkedin_url") or (p.get("vorname") and p.get("nachname")
                                          and (p.get("firma_domain") or p.get("firma")))):
            continue
        todo.append(p)

    text = (
        f"\nLusha\n"
        f"  Personen in der Liste:      {len(personen)}\n"
        f"  schon vollständig via BC:  {len(schon_gefunden)}"
        f"{' (laufen trotzdem mit, --alle gesetzt)' if a.alle else ' (werden übersprungen)'}\n"
        f"  früher schon angefragt:    {len(zustand['fertig'])}\n"
        f"  jetzt anzufragen:           {len(todo)}\n"
        f"  Lusha rechnet je aufgedeckter Angabe ab. Kein Treffer, keine Kosten.\n"
    )
    if not todo:
        print(text + "\nNichts zu tun.")
        return
    if not confirm(text, a.ja):
        return

    roh = read_json(OUT / "05_lusha_raw.json", {})
    fehler = 0
    for i, p in enumerate(todo, 1):
        pid = p["person_id"]
        params = {"revealEmails": "true", "revealPhones": "true"}
        if p.get("linkedin_url"):
            params["linkedinUrl"] = p["linkedin_url"]
        else:
            params["firstName"] = p.get("vorname", "")
            params["lastName"] = p.get("nachname", "")
            dom = domain_von(p.get("firma_domain", ""))
            if dom:
                params["companyDomain"] = dom
            else:
                params["companyName"] = p.get("firma", "")

        url = f"{BASIS}?{urllib.parse.urlencode(params)}"
        versuch = 0
        while True:
            st, body = http("GET", url, headers={"api_key": key})
            if st == 429:
                versuch += 1
                if versuch > 5:
                    die("Lusha bremst dauerhaft (429). Später erneut starten - schon "
                        "angefragte Personen werden nicht doppelt bezahlt.")
                wartezeit = 5 * versuch
                print(f"  Lusha bremst, warte {wartezeit}s ...")
                time.sleep(wartezeit)
                continue
            break

        if st == 401:
            die("Lusha lehnt den Schlüssel ab (401). Er gehört in den Header api_key.")
        roh[pid] = {"http": st, "antwort": body}
        if st >= 400 and st != 404:
            fehler += 1
        zustand["fertig"][pid] = st
        mails, nummern = treffer_aus(body) if st == 200 else ([], [])
        print(f"  [{i}/{len(todo)}] {pid} {p.get('name', '')}: "
              f"{len(mails)} Mail(s), {len(nummern)} Nummer(n)")
        if i % 20 == 0 or i == len(todo):
            write_json(OUT / "05_lusha_raw.json", roh)
            write_json(OUT / "05_lusha_state.json", zustand)
        time.sleep(a.pause)

    write_json(OUT / "05_lusha_raw.json", roh)
    write_json(OUT / "05_lusha_state.json", zustand)
    mit_mail = sum(1 for v in roh.values() if treffer_aus(v["antwort"])[0])
    mit_tel = sum(1 for v in roh.values() if treffer_aus(v["antwort"])[1])
    print(f"\nGespeichert: output/05_lusha_raw.json")
    print(f"  angefragt:   {len(roh)}")
    print(f"  mit E-Mail:  {mit_mail}")
    print(f"  mit Nummer:  {mit_tel}")
    if fehler:
        print(f"  ACHTUNG: {fehler} Anfragen mit Fehler-Code, siehe die Rohdatei.")


if __name__ == "__main__":
    main()
