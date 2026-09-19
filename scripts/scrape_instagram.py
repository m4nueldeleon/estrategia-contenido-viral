#!/usr/bin/env python3
"""Baja posts de Instagram (perfiles y/o hashtags) vía Apify.

  python3 scrape_instagram.py --perfiles anyaramove,mariana.dlrz --limite 80 --salida out/
  python3 scrape_instagram.py --hashtags pilatesencasa,wallpilates --salida out/ --nombre competencia
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.apify import token, correr, guardar, gasto_mensual

ACTOR = "apify/instagram-scraper"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--perfiles", default="", help="usuarios separados por coma")
    ap.add_argument("--hashtags", default="", help="hashtags sin # separados por coma")
    ap.add_argument("--limite", type=int, default=60, help="posts por fuente")
    ap.add_argument("--salida", default="out", help="carpeta de salida")
    ap.add_argument("--nombre", default="instagram", help="nombre del archivo")
    a = ap.parse_args()

    urls = [f"https://www.instagram.com/{p.strip().lstrip('@')}/"
            for p in a.perfiles.split(",") if p.strip()]
    urls += [f"https://www.instagram.com/explore/tags/{h.strip().lstrip('#')}/"
             for h in a.hashtags.split(",") if h.strip()]
    if not urls:
        ap.error("hacen falta --perfiles o --hashtags")

    tok = token()
    gastado, limite = gasto_mensual(tok)
    if limite:
        print(f"Apify: ${gastado:.2f} de ${limite:.2f} este mes", file=sys.stderr)
        if gastado > limite * 0.9:
            sys.exit("Estás al 90 % del límite mensual de Apify. Revisa antes de seguir.")

    print(f"Instagram · {len(urls)} fuentes × {a.limite} posts", file=sys.stderr)
    items = correr(ACTOR, {
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": a.limite,
        "addParentData": True,
    }, tok)
    guardar(items, Path(a.salida) / f"{a.nombre}.json")


if __name__ == "__main__":
    main()
