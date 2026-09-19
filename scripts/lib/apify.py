"""Cliente mínimo de Apify: lanzar un actor, esperar y bajar el dataset."""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

API = "https://api.apify.com/v2"


def token() -> str:
    """Toma el token de APIFY_TOKEN o de ~/.apify-cli/.env."""
    t = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")
    if t:
        return t
    env = Path.home() / ".apify-cli" / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith(("APIFY_TOKEN=", "APIFY_API_TOKEN=")):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("Falta APIFY_TOKEN. Ponlo en el entorno o en ~/.apify-cli/.env")


def _req(url: str, data: bytes | None = None, method: str = "GET"):
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def gasto_mensual(tok: str) -> tuple[float, float]:
    """Devuelve (gastado, limite) en USD. Para avisar antes de quemar el plan."""
    d = _req(f"{API}/users/me/limits?token={tok}")["data"]
    return (d.get("current", {}).get("monthlyUsageUsd", 0.0),
            d.get("limits", {}).get("maxMonthlyUsageUsd", 0.0))


def correr(actor: str, entrada: dict, tok: str, espera_max: int = 900,
           intervalo: int = 20, verboso: bool = True) -> list[dict]:
    """Lanza el actor, espera a que termine y devuelve los items del dataset."""
    actor = actor.replace("/", "~")
    run = _req(f"{API}/acts/{actor}/runs?token={tok}",
               data=json.dumps(entrada).encode(), method="POST")["data"]
    rid, dsid = run["id"], run["defaultDatasetId"]
    if verboso:
        print(f"  actor={actor} run={rid}", file=sys.stderr)
    t0 = time.time()
    while time.time() - t0 < espera_max:
        time.sleep(intervalo)
        st = _req(f"{API}/actor-runs/{rid}?token={tok}")["data"]["status"]
        n = _req(f"{API}/datasets/{dsid}?token={tok}")["data"]["itemCount"]
        if verboso:
            print(f"  [{int(time.time()-t0):>4}s] {st} · {n} items", file=sys.stderr)
        if st not in ("RUNNING", "READY"):
            break
    else:
        print(f"  AVISO: {rid} sigue corriendo tras {espera_max}s; bajo lo que haya",
              file=sys.stderr)
    return _req(f"{API}/datasets/{dsid}/items?token={tok}")


def guardar(items: list[dict], destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(items, ensure_ascii=False))
    print(f"  -> {destino} ({len(items)} items)", file=sys.stderr)
    return destino
