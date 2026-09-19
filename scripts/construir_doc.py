#!/usr/bin/env python3
"""Convierte los guiones en Markdown a un HTML listo para importar a Google Docs.

  python3 construir_doc.py --guiones guiones/ --titulo "MARCA · 20 videos" --salida doc.html

Después, desde Claude Code:
  import_to_google_doc(file_path=..., source_format="html")
  set_drive_file_permissions(file_id=..., link_sharing="writer")

Ojo: el archivo debe estar dentro de ALLOWED_FILE_DIRS
(por omisión ~/.workspace-mcp/attachments).
"""
import argparse, glob, html, re, sys
from pathlib import Path

CSS = """body{font-family:Arial,Helvetica,sans-serif;font-size:11pt;line-height:1.5;color:#1a1a1a}
h1{font-size:22pt;margin-bottom:2pt}h2{font-size:16pt;border-bottom:2px solid #ddd;padding-bottom:4pt;margin-top:26pt}
h3{font-size:13pt;margin-top:18pt}h4{font-size:11pt;margin-top:12pt;margin-bottom:2pt}
table{border-collapse:collapse;width:100%;margin:8pt 0;font-size:9.5pt}
th{background:#eee;text-align:left;padding:5pt;border:1px solid #ccc}
td{padding:5pt;border:1px solid #e6e6e6;vertical-align:top}
blockquote{border-left:3px solid #999;margin-left:0;padding-left:12pt;color:#444}
.sub{color:#666;font-size:10pt}"""


def md_a_html(t: str) -> str:
    """Markdown mínimo pero suficiente: encabezados, tablas, listas, énfasis."""
    out, tabla = [], []

    def cerrar_tabla():
        if not tabla:
            return
        filas = [f for f in tabla if not re.match(r"^\s*\|[\s:|-]+\|\s*$", f)]
        out.append("<table>")
        for i, f in enumerate(filas):
            celdas = [c.strip() for c in f.strip().strip("|").split("|")]
            et = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(f"<{et}>{inline(c)}</{et}>" for c in celdas) + "</tr>")
        out.append("</table>")
        tabla.clear()

    def inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", s)
        s = re.sub(r"`([^`]+?)`", r"<span style='font-family:Courier New'>\1</span>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href='\2'>\1</a>", s)
        return s

    for ln in t.split("\n"):
        if ln.lstrip().startswith("|"):
            tabla.append(ln); continue
        cerrar_tabla()
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            n = len(s) - len(s.lstrip("#"))
            out.append(f"<h{min(n,4)}>{inline(s.lstrip('#').strip())}</h{min(n,4)}>")
        elif s.startswith(">"):
            out.append(f"<blockquote>{inline(s.lstrip('>').strip())}</blockquote>")
        elif s in ("---", "***", "___"):
            out.append("<hr>")
        elif re.match(r"^[-*] ", s):
            out.append(f"<p>&bull; {inline(s[2:])}</p>")
        elif re.match(r"^\d+\. ", s):
            out.append(f"<p>{inline(s)}</p>")
        else:
            out.append(f"<p>{inline(s)}</p>")
    cerrar_tabla()
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guiones", default="guiones", help="carpeta de .md, en orden alfabético")
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--salida", default="doc.html")
    a = ap.parse_args()

    archivos = sorted(glob.glob(str(Path(a.guiones) / "*.md")))
    if not archivos:
        sys.exit(f"No hay .md en {a.guiones}")
    cuerpo = "\n".join(md_a_html(Path(f).read_text()) for f in archivos)

    doc = (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
           f'<title>{html.escape(a.titulo)}</title><style>{CSS}</style></head><body>'
           f'<h1>{html.escape(a.titulo)}</h1>'
           + (f'<p class="sub">{html.escape(a.subtitulo)}</p>' if a.subtitulo else "")
           + cuerpo + "</body></html>")
    Path(a.salida).write_text(doc)
    print(f"-> {a.salida}  ({len(doc):,} bytes · {len(archivos)} archivos)")
    print("\nSiguiente paso: copiar a ~/.workspace-mcp/attachments/ e importar con")
    print("  import_to_google_doc(file_path=..., source_format='html')")


if __name__ == "__main__":
    main()
