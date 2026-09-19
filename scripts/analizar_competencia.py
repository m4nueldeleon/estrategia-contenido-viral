#!/usr/bin/env python3
"""Filtra la competencia y la separa en las dos economías.

  python3 analizar_competencia.py --datos out/ --min-likes 10000 --excluir anyaramove
  python3 analizar_competencia.py --datos out/ --csv seleccion.csv
"""
import argparse, csv, glob, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.norma import normalizar, tasa, indice_utilidad

PISO_TASA = 300_000   # reproducciones mínimas para que una tasa signifique algo


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", default="out")
    ap.add_argument("--min-likes", type=int, default=10000, help="filtro duro")
    ap.add_argument("--tope-tiktok", type=int, default=2, help="máx piezas por autor")
    ap.add_argument("--tope-instagram", type=int, default=4)
    ap.add_argument("--excluir", default="", help="cuentas propias, separadas por coma")
    ap.add_argument("--csv", default=None, help="exportar la selección")
    a = ap.parse_args()

    fuera = {c.strip().lstrip("@") for c in a.excluir.split(",") if c.strip()}
    vistos, pool = set(), []
    for f in sorted(glob.glob(str(Path(a.datos) / "*.json"))):
        for x in normalizar(json.load(open(f))):
            if x["id"] in vistos or x["autor"] in fuera:
                continue
            vistos.add(x["id"])
            if (x.get("likes") or 0) >= a.min_likes:
                pool.append(x)

    print(f"Revisadas {len(vistos)} piezas · {len(pool)} pasan el filtro de "
          f"{a.min_likes:,} likes\n")
    if not pool:
        sys.exit("Nada pasó el filtro. Baja --min-likes o amplía las fuentes.")

    # tope por autor, quedándose con lo mejor de cada uno
    sel, cuenta = [], {}
    for x in sorted(pool, key=lambda x: -(x.get("likes") or 0)):
        tope = a.tope_tiktok if x["red"] == "tiktok" else a.tope_instagram
        k = (x["red"], x["autor"])
        if cuenta.get(k, 0) < tope:
            cuenta[k] = cuenta.get(k, 0) + 1
            sel.append(x)

    for x in sel:
        x["t_comp"] = tasa(x.get("compartidos"), x.get("reproducciones"))
        x["t_guard"] = tasa(x.get("guardados"), x.get("reproducciones"))
        x["t_com"] = tasa(x.get("comentarios"), x.get("reproducciones"))
        x["utilidad"] = indice_utilidad(x.get("guardados"), x.get("likes"))

    print(f"Selección tras el tope por autor: {len(sel)} "
          f"({sum(1 for x in sel if x['red']=='instagram')} IG · "
          f"{sum(1 for x in sel if x['red']=='tiktok')} TikTok)")
    print(f"Autores distintos: {len(cuenta)}\n")

    med = [x for x in sel if (x.get("reproducciones") or 0) >= PISO_TASA
           and x["t_comp"] is not None]

    def bloque(titulo, filas, campo, nota):
        print("=" * 78); print(titulo); print(nota + "\n")
        for i, x in enumerate(filas, 1):
            print(f"{i:>2}. @{x['autor']:<24} {x.get('seguidores') or 0:>9,} seg · "
                  f"{x['reproducciones']:>10,} rep · {x.get('likes') or 0:>8,} likes · "
                  f"comp {x['t_comp']}% · guard {x['t_guard']}%")
            print(f"    {x['texto'][:82]}")
            print(f"    {x['url']}")
        print()

    if med:
        bloque("ECONOMÍA DE COMPARTIR — traen gente nueva",
               sorted(med, key=lambda x: -(x["t_comp"] or 0))[:20], "t_comp",
               "Objetivo del bloque de guiones de compartir: > 2 % de compartidos.")
        bloque("ECONOMÍA DE GUARDAR — convierten",
               sorted(med, key=lambda x: -(x["t_guard"] or 0))[:20], "t_guard",
               "Objetivo del bloque de guiones de guardar: > 4 % de guardados.")
        # índice de utilidad: la métrica que premia valor, no juego
        util = [x for x in sel if x.get("utilidad") is not None
                and (x.get("reproducciones") or 0) >= 100_000]
        if util:
            print("=" * 78)
            print("ÍNDICE DE UTILIDAD — guardados ÷ likes  (objetivo > 0.40)")
            print("La tasa de compartido premia juegos. Esta premia lo que la gente necesita.")
            print("Entretenimiento: 0.05-0.15 · Educadores: 0.35-1.14 · Ver references/VALOR.md\n")
            for i, x in enumerate(sorted(util, key=lambda x: -x["utilidad"])[:20], 1):
                marca = "  <-- VALOR" if x["utilidad"] >= 0.40 else ""
                print(f"{i:>2}. util {x['utilidad']:>5.2f}x | @{x['autor']:<24} "
                      f"{x.get('seguidores') or 0:>9,} seg · {x['reproducciones']:>10,} rep · "
                      f"L{x.get('likes') or 0:>8,} G{x.get('guardados') or 0:>8,}{marca}")
                print(f"    {x['texto'][:82]}")
                print(f"    {x['url']}")
            print()

        dual = [x for x in med if (x["t_comp"] or 0) > 2 and (x["t_guard"] or 0) > 2]
        print("=" * 78)
        print(f"PIEZAS FUERTES EN LAS DOS ECONOMÍAS: {len(dual)} de {len(med)}")
        for x in dual:
            print(f"  @{x['autor']} · {x['reproducciones']:,} rep · "
                  f"comp {x['t_comp']}% guard {x['t_guard']}% · {x.get('dur')}s")
        print("  Son la excepción, no la regla. Suelen durar menos de 10 segundos.")
        print("  Ver references/DOS-ECONOMIAS.md\n")
    else:
        print("Sin datos de compartidos/guardados (Instagram público no los expone).")
        print("Para el análisis de economías hacen falta datos de TikTok.\n")

    print("=" * 78)
    print("INSTAGRAM — por likes")
    for i, x in enumerate([x for x in sel if x["red"] == "instagram"][:25], 1):
        print(f"{i:>2}. @{x['autor']:<24} {x.get('likes') or 0:>8,} likes · "
              f"{x.get('reproducciones') or 0:>10,} rep · {x['url']}")
        print(f"    {x['texto'][:82]}")

    if a.csv:
        cols = ["red", "autor", "seguidores", "fecha", "dur", "reproducciones",
                "likes", "comentarios", "compartidos", "guardados",
                "t_comp", "t_guard", "t_com", "utilidad", "texto", "url"]
        with open(a.csv, "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            wr.writeheader(); wr.writerows(sel)
        print(f"\nCSV -> {a.csv}")


if __name__ == "__main__":
    main()
