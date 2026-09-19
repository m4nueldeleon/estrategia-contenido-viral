#!/usr/bin/env python3
"""Diagnóstico de las cuentas propias: mediana, umbrales, top y qué pasó tras cada pico.

  python3 analizar_cuenta.py --datos out/ --corte 2026-09-07
"""
import argparse, glob, json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.norma import normalizar, tasa


def umbrales(mediana: float) -> list[tuple]:
    return [
        ("Bajo",       f"< {mediana*0.7:,.0f}",                      "Falló el hook. Revisar los primeros 3 s"),
        ("Normal",     f"{mediana*0.7:,.0f} – {mediana*1.6:,.0f}",   "Llegó a los seguidores, no salió de ahí"),
        ("Bueno",      f"{mediana*1.6:,.0f} – {mediana*4:,.0f}",     "El algoritmo lo empujó fuera"),
        ("Muy bueno",  f"{mediana*4:,.0f} – {mediana*12:,.0f}",      "Parte 2 en 72 h. Parte 3 antes de 10 días"),
        ("Viral",      f"> {mediana*12:,.0f}",                       "Parte 2 en 48 h y la tanda se reordena"),
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", default="out", help="carpeta con los .json")
    ap.add_argument("--corte", default=None, help="AAAA-MM-DD de la tanda anterior")
    ap.add_argument("--cuentas", default="", help="limitar a estas cuentas")
    a = ap.parse_args()

    items = []
    for f in sorted(glob.glob(str(Path(a.datos) / "*.json"))):
        items += normalizar(json.load(open(f)))
    solo = {c.strip().lstrip("@") for c in a.cuentas.split(",") if c.strip()}

    # clave (red, autor): la misma persona en dos redes son dos cuentas distintas
    por_autor = {}
    for x in items:
        por_autor.setdefault((x["red"], x["autor"]), {})[x["id"]] = x
    if solo:
        por_autor = {k: v for k, v in por_autor.items() if k[1] in solo}
    # solo cuentas con volumen suficiente para que la mediana signifique algo
    por_autor = {k: v for k, v in por_autor.items() if len(v) >= 10}

    resumen = []
    for (red, autor), d in sorted(por_autor.items(), key=lambda kv: -len(kv[1])):
        ps = sorted(d.values(), key=lambda x: x["fecha"] or "")
        vids = [x for x in ps if x.get("reproducciones")]
        if not vids:
            continue
        rep = [x["reproducciones"] for x in vids]
        med = st.median(rep)
        seg = next((x["seguidores"] for x in ps if x.get("seguidores")), None)
        lks = [x["likes"] for x in ps if x.get("likes") is not None]

        print("=" * 78)
        print(f"@{autor}  ·  {red}  ·  {len(ps)} posts  ·  {ps[0]['fecha']} → {ps[-1]['fecha']}")
        print(f"  seguidores: {seg:,}" if seg else "  seguidores: n/d")
        print(f"  MEDIANA de reproducciones: {med:,.0f}   (media {sum(rep)/len(rep):,.0f} · máx {max(rep):,})")
        if lks and seg:
            print(f"  likes/seguidor (mediana): {st.median(lks)/seg*100:.2f} %")
        if a.corte:
            ant = [x["reproducciones"] for x in vids if (x["fecha"] or "") < a.corte]
            des = [x["reproducciones"] for x in vids if (x["fecha"] or "") >= a.corte]
            if ant and des:
                print(f"  antes de {a.corte}: mediana {st.median(ant):,.0f} (n={len(ant)})")
                print(f"  desde  {a.corte}: mediana {st.median(des):,.0f} (n={len(des)})")

        print("\n  UMBRALES")
        for n, r, q in umbrales(med):
            print(f"    {n:<11} {r:<26} {q}")

        print("\n  TOP 8 POR REPRODUCCIONES")
        top = sorted(vids, key=lambda x: -x["reproducciones"])[:8]
        for x in top:
            tc = tasa(x.get("compartidos"), x["reproducciones"])
            tg = tasa(x.get("guardados"), x["reproducciones"])
            tcm = tasa(x.get("comentarios"), x["reproducciones"])
            extra = f" C{tc}% G{tg}%" if tc is not None else ""
            print(f"    {x['fecha']} {x['reproducciones']:>9,} rep · {x.get('likes') or 0:>7,} likes"
                  f" · com {tcm if tcm is not None else '?'}%{extra}")
            print(f"        {x['texto'][:78]}")

        # qué pasó DESPUÉS de cada pico — el antipatrón número 1
        print("\n  DESPUÉS DE CADA PICO  (antipatrón 1: no repetir el formato que explotó)")
        alerta = False
        for x in top[:3]:
            i = vids.index(x)
            sig = vids[i+1:i+6]
            if not sig:
                continue
            m2 = st.median([s["reproducciones"] for s in sig])
            caida = (1 - m2 / x["reproducciones"]) * 100
            marca = "  <-- SE PERDIÓ LA VENTANA" if caida > 85 else ""
            alerta = alerta or caida > 85
            print(f"    pico {x['fecha']} {x['reproducciones']:>9,}  →  "
                  f"mediana de los 5 siguientes {m2:>9,.0f}  (−{caida:.0f} %){marca}")
        if alerta:
            print("    ACCIÓN: reservar casilla de secuela en el calendario. Ver ANTIPATRONES.md §1")
        print()
        resumen.append((f"{autor} ({red})", seg, med))

    if len(resumen) > 1:
        print("=" * 78)
        print("COMPARATIVA")
        base = min(r[2] for r in resumen if r[2])
        for autor, seg, med in sorted(resumen, key=lambda r: -(r[2] or 0)):
            print(f"  @{autor:<24} {seg or 0:>9,} seg · mediana {med:>9,.0f} · {med/base:.2f}×")
        print("\n  Si una cuenta rinde varias veces otra, eso reordena el reparto de los guiones.")


if __name__ == "__main__":
    main()
