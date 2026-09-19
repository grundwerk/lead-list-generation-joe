#!/usr/bin/env python3
"""Schritt 2: Personen der Firmen von LinkedIn holen (Apify).

Liest output/01_firmen.csv (Spalte linkedin_company_url), startet den Actor
harvestapi/linkedin-company-employees und legt das Ergebnis roh und normalisiert ab.

Beispiel:
  python3 scripts/apify_employees.py --pro-firma 8 \
      --titel "CEO,Geschaeftsfuehrer,M&A,Corporate Development,Head of Acquisition" \
      --modus full
"""
import argparse
import csv
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import OUT, confirm, die, http, need, write_json  # noqa: E402

ACTOR = "harvestapi~linkedin-company-employees"

# Preise laut Actor-Seite, Stand 19.09.2026. Die verbindliche Zahl steht immer auf
# https://apify.com/harvestapi/linkedin-company-employees - hier nur zum Schaetzen.
MODI = {
    "short": ("Short ($4 per 1k)", 0.004),
    "full": ("Full ($8 per 1k)", 0.008),
}
START_KOSTEN = 0.02  # pro Abfrage, und im Modus eine-nach-der-anderen ist das eine pro Firma


def firmen_lesen(pfad):
    with open(pfad, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        die(f"{pfad} ist leer.")
    spalte = None
    for kandidat in ("linkedin_company_url", "linkedin", "linkedin_url"):
        if kandidat in rows[0]:
            spalte = kandidat
            break
    if not spalte:
        die(f"{pfad} hat keine Spalte linkedin_company_url. Gefunden: {list(rows[0])}")
    urls, ohne = [], []
    for r in rows:
        u = (r.get(spalte) or "").strip()
        name = (r.get("firma") or r.get("company") or "").strip()
        if u.startswith("http") and "/company/" in u:
            urls.append(u)
        else:
            ohne.append(name or u or "(ohne Namen)")
    return urls, ohne, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmen", default=str(OUT / "01_firmen.csv"))
    ap.add_argument("--pro-firma", type=int, default=8,
                    help="Hoechstens so viele Personen je Firma. Das ist die Kostenbremse.")
    ap.add_argument("--titel", default="",
                    help="Jobtitel-Filter, mit Komma getrennt. Leer = alle Personen der Firma.")
    ap.add_argument("--seniority", default="",
                    help="LinkedIn-Seniority-IDs mit Komma, z.B. 220,300,310,320 "
                         "(Director, VP, CXO, Owner/Partner).")
    ap.add_argument("--orte", default="", help="Orts-Filter, mit Komma getrennt.")
    ap.add_argument("--modus", choices=list(MODI), default="full")
    ap.add_argument("--ja", action="store_true", help="Kosten-Rueckfrage ueberspringen.")
    a = ap.parse_args()

    token = need("APIFY_TOKEN")
    urls, ohne, _ = firmen_lesen(a.firmen)

    if ohne:
        print(f"WARNUNG: {len(ohne)} Zeilen ohne brauchbare LinkedIn-Firmen-URL, "
              f"sie werden uebersprungen:")
        for n in ohne[:10]:
            print(f"  - {n}")
        if len(ohne) > 10:
            print(f"  ... und {len(ohne) - 10} weitere")
    if not urls:
        die("Keine einzige gueltige LinkedIn-Firmen-URL. Ohne die kann der Scraper nichts tun.")

    label, preis = MODI[a.modus]
    max_profile = len(urls) * a.pro_firma
    schaetzung = len(urls) * START_KOSTEN + max_profile * preis

    text = (
        f"\nApify-Lauf\n"
        f"  Firmen:            {len(urls)}\n"
        f"  Personen je Firma: hoechstens {a.pro_firma}\n"
        f"  Modus:             {label}\n"
        f"  Obergrenze:        {max_profile} Profile\n"
        f"  Kosten hoechstens: rund ${schaetzung:.2f} "
        f"({len(urls)} x ${START_KOSTEN:.2f} Start + {max_profile} x ${preis:.3f})\n"
        f"  Weniger Treffer heisst weniger Kosten, mehr als die Obergrenze geht nicht.\n"
    )
    if not confirm(text, a.ja):
        return

    payload = {
        "companies": urls,
        "profileScraperMode": label,
        "companyBatchMode": "one_by_one",
        "maxItemsPerCompany": a.pro_firma,
        "maxItems": max_profile,
    }
    if a.titel:
        payload["jobTitles"] = [t.strip() for t in a.titel.split(",") if t.strip()]
    if a.seniority:
        payload["seniorityLevelIds"] = [s.strip() for s in a.seniority.split(",") if s.strip()]
    if a.orte:
        payload["locations"] = [o.strip() for o in a.orte.split(",") if o.strip()]

    print("\nStarte den Actor ...")
    status, run = http(
        "POST",
        f"https://api.apify.com/v2/acts/{ACTOR}/runs?token={token}",
        body=payload,
    )
    if status not in (200, 201):
        die(f"Apify hat den Lauf nicht angenommen (HTTP {status}): {run}")
    run_id = run.get("data", {}).get("id")
    dataset_id = run.get("data", {}).get("defaultDatasetId")
    if not run_id:
        die(f"Apify hat keine Lauf-Nummer zurueckgegeben: {run}")
    print(f"Lauf {run_id} laeuft. Live zusehen: https://console.apify.com/actors/runs/{run_id}")

    letzter = ""
    while True:
        time.sleep(10)
        st, info = http("GET", f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}")
        zustand = info.get("data", {}).get("status", "UNBEKANNT")
        if zustand != letzter:
            print(f"  Zustand: {zustand}")
            letzter = zustand
        if zustand in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    if zustand != "SUCCEEDED":
        die(f"Der Lauf endete mit {zustand}. Details im Apify-Dashboard, Lauf {run_id}.")

    st, items = http(
        "GET",
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}&clean=true&format=json",
        timeout=300,
    )
    if not isinstance(items, list):
        die(f"Unerwartete Antwort beim Abholen der Daten: {items}")

    write_json(OUT / "02_personen_raw.json", items)
    print(f"\nRoh gespeichert: output/02_personen_raw.json ({len(items)} Personen)")

    felder = ["person_id", "vorname", "nachname", "name", "titel", "firma",
              "firma_linkedin", "linkedin_url", "ort", "ueber_mich"]
    OUT.mkdir(exist_ok=True)
    with open(OUT / "02_personen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=felder)
        w.writeheader()
        for i, p in enumerate(items, 1):
            firma = p.get("currentPosition") or {}
            if isinstance(firma, list):
                firma = firma[0] if firma else {}
            w.writerow({
                "person_id": f"P{i:05d}",
                "vorname": p.get("firstName", ""),
                "nachname": p.get("lastName", ""),
                "name": p.get("name") or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip(),
                "titel": p.get("position") or p.get("headline") or firma.get("position", ""),
                "firma": firma.get("companyName") or p.get("companyName", ""),
                "firma_linkedin": firma.get("companyLinkedinUrl") or p.get("companyLinkedinUrl", ""),
                "linkedin_url": p.get("linkedinUrl") or p.get("publicIdentifier", ""),
                "ort": p.get("location", {}).get("linkedinText", "") if isinstance(p.get("location"), dict) else p.get("location", ""),
                "ueber_mich": (p.get("about") or "")[:600],
            })
    print(f"Lesbar gespeichert: output/02_personen.csv")
    print(f"\nNaechster Schritt: die Personen auf Passung pruefen (Schritt 3 im Skill).")


if __name__ == "__main__":
    main()
