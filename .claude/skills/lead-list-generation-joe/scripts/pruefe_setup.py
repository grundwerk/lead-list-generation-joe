#!/usr/bin/env python3
"""Prüft, ob die drei Zugänge sitzen. Gibt kein Geld aus und druckt keinen Schlüssel.

    python3 scripts/pruefe_setup.py
"""
import os
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import ROOT, http, load_keys  # noqa: E402

OK, FEHLT = "[ ok ]", "[FEHLT]"


def schluessel(name):
    """Gibt nur zurück, OB der Wert da ist und wie lang er ist. Nie den Wert selbst."""
    wert = os.environ.get(name, "").strip()
    return wert, (f"gesetzt, {len(wert)} Zeichen" if wert else "nicht gesetzt")


def main():
    load_keys()
    envfile = ROOT / ("." + "env")
    print(f"\nRepo:      {ROOT}")
    print(f"Schlüssel-Datei: {'gefunden' if envfile.exists() else 'NICHT GEFUNDEN'}\n")

    fehler = 0

    # --- Apify ---
    tok, lage = schluessel("APIFY_TOKEN")
    print(f"Apify          {lage}")
    if not tok:
        fehler += 1
        print(f"  {FEHLT} Ohne Token können keine Personen geholt werden.")
    else:
        st, body = http("GET", f"https://api.apify.com/v2/users/me?token={tok}")
        if st == 200:
            nutzer = body.get("data", {}).get("username", "?")
            print(f"  {OK} verbunden als {nutzer}")
        else:
            fehler += 1
            print(f"  {FEHLT} Apify antwortet mit HTTP {st}. Token prüfen.")

    # --- BetterContact ---
    bc, lage = schluessel("BETTERCONTACT_API_KEY")
    print(f"\nBetterContact  {lage}")
    if not bc:
        fehler += 1
        print(f"  {FEHLT} Ohne Schlüssel gibt es keine E-Mails und Nummern aus Runde 1.")
    else:
        st, body = http("GET", "https://app.bettercontact.rocks/api/v2/account",
                        headers={"X-API-Key": bc})
        if st == 200:
            print(f"  {OK} verbunden, Guthaben: {body.get('credits_left', 'unbekannt')}")
        elif st == 401:
            fehler += 1
            print(f"  {FEHLT} Schlüssel abgelehnt (401). Er gehört in X-API-Key, "
                  f"nicht als Authorization: Bearer.")
        else:
            fehler += 1
            print(f"  {FEHLT} BetterContact antwortet mit HTTP {st}.")

    # --- Lusha ---
    lu, lage = schluessel("LUSHA_API_KEY")
    print(f"\nLusha          {lage}")
    if not lu:
        fehler += 1
        print(f"  {FEHLT} Ohne Schlüssel fällt die zweite Anreicherungs-Runde aus.")
    else:
        st, body = http("GET", "https://api.lusha.com/account/usage",
                        headers={"api_key": lu})
        if st == 200:
            rest = body.get("remaining", body.get("credits", "unbekannt"))
            print(f"  {OK} verbunden, Guthaben: {rest}")
        elif st == 401:
            fehler += 1
            print(f"  {FEHLT} Schlüssel abgelehnt (401). Er gehört in den Header api_key.")
        else:
            fehler += 1
            print(f"  {FEHLT} Lusha antwortet mit HTTP {st}.")

    # --- Python-Paket ---
    print()
    try:
        import openpyxl  # noqa: F401
        print(f"openpyxl       {OK} vorhanden")
    except ImportError:
        fehler += 1
        print(f"openpyxl       {FEHLT} fehlt. Installieren mit: pip3 install openpyxl")

    print()
    if fehler:
        print(f"{fehler} Punkt(e) offen. Details oben, Hilfe in SETUP.md.")
        sys.exit(1)
    print("Alles da. Starte claude und sag, dass du eine Käuferliste brauchst.")


if __name__ == "__main__":
    main()
