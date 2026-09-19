#!/usr/bin/env python3
"""Baja videos de TikTok (perfiles, hashtags o búsquedas) vía Apify.

  python3 scrape_tiktok.py --perfiles anyaramove --limite 40 --salida out/
  python3 scrape_tiktok.py --buscar-nicho "pilates en casa" --buscar-trends --salida out/
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.apify import token, correr, guardar, gasto_mensual

ACTOR = "clockworks/tiktok-scraper"

# Búsquedas de formatos prestados. Ver references/FORMATOS-PORTABLES.md
TRENDS = [
    "expectativa vs realidad trend",
    "tipos de personas en",
    "dos amigas comparacion trend",
    "pov cuando llegas",
    "quien es mas probable trend",
    "ranking tier list",
    "storytime incomodo",
    "boyfriend check trend",
    "cosas que ojala supiera antes",
    "adivina trend",
]

# Barrido por industrias ajenas: de aquí salieron los dos formatos con mejores
# números del caso Anyara. Ver references/FORMATOS-PORTABLES.md
INDUSTRIAS = [
    "que prefieres",                  # entretenimiento — 9.25 % de compartido
    "elige uno",
    "dia 1 de 30 dias reto",          # dibujo/guitarra/disciplina — 6.69 % guardado
    "asmr limpieza satisfactorio",    # cleantok — 30.3 M de reproducciones
    "restock organiza conmigo",
    "caro vs barato cual es mejor",   # bebidas/compras
    "trucos para ahorrar dinero",     # finanzas personales
    "rutina de skincare orden correcto",
    "probando productos virales de tiktok",
    "tipos de clientes",              # oficios de mostrador
    "3 errores que cometes",
    "cosas antes de dormir",
    "outfit transicion",
    "me converti en por un dia",
    "adivina el precio",
]

# Capa de educadores: especialistas que ganan ENSEÑANDO. Es la que produce el
# valor; sin ella la tanda sale llena de juegos que no enseñan nada.
# Sustituye el tema por el tuyo. Ver references/VALOR.md
EDUCADORES = [
    "fisioterapeuta explica por que te duele",
    "por que no siento el musculo al entrenar",
    "biomecanica explicada simple",
    "mito del ejercicio desmentido",
    "test casero para saber si tengo",
    "cuanto tarda realmente en verse",
    "no es desgaste es",
    "suelo pelvico fisioterapeuta",
    "entrenar segun tu ciclo menstrual",
    "menopausia y entrenamiento de fuerza",
    "respiracion diafragmatica como se hace",
    "3 errores que cometes al",
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--perfiles", default="")
    ap.add_argument("--hashtags", default="")
    ap.add_argument("--buscar-nicho", default="",
                    help="búsquedas del nicho separadas por ';'")
    ap.add_argument("--buscar-trends", action="store_true",
                    help="añade el set de trends prestados")
    ap.add_argument("--buscar-industrias", action="store_true",
                    help="añade el barrido por industrias ajenas (la capa que da los saltos de escala)")
    ap.add_argument("--buscar-educadores", action="store_true",
                    help="añade la capa de especialistas que enseñan (la capa que da el valor)")
    ap.add_argument("--limite", type=int, default=40, help="resultados por fuente")
    ap.add_argument("--pais", default="MX", help="código de proxy, ej. MX, ES, US")
    ap.add_argument("--salida", default="out")
    ap.add_argument("--nombre", default="tiktok")
    a = ap.parse_args()

    entrada = {
        "resultsPerPage": a.limite,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
        "proxyCountryCode": a.pais,
    }
    perfiles = [p.strip().lstrip("@") for p in a.perfiles.split(",") if p.strip()]
    hashtags = [h.strip().lstrip("#") for h in a.hashtags.split(",") if h.strip()]
    queries = [q.strip() for q in a.buscar_nicho.split(";") if q.strip()]
    if a.buscar_trends:
        queries += TRENDS
    if a.buscar_industrias:
        queries += INDUSTRIAS
    if a.buscar_educadores:
        queries += EDUCADORES
    if perfiles:
        entrada["profiles"] = perfiles
    if hashtags:
        entrada["hashtags"] = hashtags
    if queries:
        entrada["searchQueries"] = queries
    if not (perfiles or hashtags or queries):
        ap.error("hace falta --perfiles, --hashtags, --buscar-nicho, --buscar-trends, --buscar-industrias o --buscar-educadores")

    tok = token()
    gastado, limite = gasto_mensual(tok)
    if limite:
        print(f"Apify: ${gastado:.2f} de ${limite:.2f} este mes", file=sys.stderr)
        if gastado > limite * 0.9:
            sys.exit("Estás al 90 % del límite mensual de Apify. Revisa antes de seguir.")

    n = len(perfiles) + len(hashtags) + len(queries)
    print(f"TikTok · {n} fuentes × {a.limite}", file=sys.stderr)
    guardar(correr(ACTOR, entrada, tok), Path(a.salida) / f"{a.nombre}.json")


if __name__ == "__main__":
    main()
