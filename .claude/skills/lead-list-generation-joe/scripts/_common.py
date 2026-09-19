"""Gemeinsame Helfer für alle Skripte: Schlüssel laden, HTTP, Dateien."""
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "output"


def load_keys():
    """Liest die Schlüssel aus der Umgebung, sonst aus der .env-Datei im Repo-Wurzelverzeichnis."""
    envfile = ROOT / ("." + "env")
    if envfile.exists():
        for line in envfile.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def need(name):
    load_keys()
    val = os.environ.get(name, "").strip()
    if not val:
        die(
            f"{name} fehlt.\n"
            f"Trag den Schlüssel in die Datei .env ein (Vorlage: .env.example) "
            f"oder setz ihn als Umgebungsvariable."
        )
    return val


def die(msg, code=1):
    print(f"\nABBRUCH: {msg}\n", file=sys.stderr)
    sys.exit(code)


def http(method, url, headers=None, body=None, timeout=120):
    """Ein HTTP-Aufruf. Gibt (status, geparster-body) zurück. Wirft nie auf 4xx/5xx,
    damit der Aufrufer selbst entscheiden kann - ein 202 ist hier kein Fehler."""
    data = None
    headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, parse(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, parse(raw)
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}


def parse(raw):
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw[:2000]}


def read_json(path, default=None):
    p = pathlib.Path(path)
    if not p.exists():
        return default if default is not None else {}
    return json.loads(p.read_text())


def write_json(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    return p


def confirm(text, auto_yes):
    """Vor jedem Schritt, der Geld kostet. --ja überspringt die Rückfrage."""
    print(text)
    if auto_yes:
        print("--ja gesetzt, läuft los.")
        return True
    answer = input("Weiter? [j/N] ").strip().lower()
    if answer not in ("j", "ja", "y", "yes"):
        print("Abgebrochen. Es wurde nichts ausgegeben.")
        return False
    return True


def progress(done, total, label=""):
    print(f"  [{done}/{total}] {label}", flush=True)
