"""Normaliza posts de Instagram y TikTok a un mismo esquema.

Campos: red, autor, seguidores, id, url, fecha, texto, dur,
        reproducciones, vistas, likes, comentarios, compartidos, guardados
"""
from __future__ import annotations


def desde_instagram(x: dict) -> dict | None:
    md = x.get("metaData") or {}
    sc = x.get("shortCode")
    return {
        "red": "instagram",
        "autor": x.get("ownerUsername"),
        "seguidores": md.get("followersCount"),
        "id": x.get("id"),
        "url": f"https://www.instagram.com/reel/{sc}/" if sc else None,
        "fecha": (x.get("timestamp") or "")[:10],
        "texto": (x.get("caption") or "").replace("\n", " ").strip(),
        "dur": None,
        "reproducciones": x.get("videoPlayCount"),
        "vistas": x.get("videoViewCount"),
        "likes": x.get("likesCount") if (x.get("likesCount") or 0) >= 0 else None,
        "comentarios": x.get("commentsCount"),
        "compartidos": None,   # Instagram público no lo expone
        "guardados": None,     # idem
        "tipo": x.get("type"),
    } if x.get("id") else None


def desde_tiktok(x: dict) -> dict | None:
    a = x.get("authorMeta") or {}
    return {
        "red": "tiktok",
        "autor": a.get("name"),
        "seguidores": a.get("fans"),
        "id": x.get("id"),
        "url": x.get("webVideoUrl"),
        "fecha": (x.get("createTimeISO") or "")[:10],
        "texto": (x.get("text") or "").replace("\n", " ").strip(),
        "dur": (x.get("videoMeta") or {}).get("duration"),
        "reproducciones": x.get("playCount"),
        "vistas": x.get("playCount"),
        "likes": x.get("diggCount"),
        "comentarios": x.get("commentCount"),
        "compartidos": x.get("shareCount"),
        "guardados": x.get("collectCount"),
        "tipo": "Video",
        "busqueda": x.get("searchQuery"),
    } if x.get("id") else None


def normalizar(items: list[dict]) -> list[dict]:
    out = []
    for x in items:
        n = desde_tiktok(x) if "authorMeta" in x else desde_instagram(x)
        if n and n.get("autor"):
            out.append(n)
    return out


def tasa(num, den):
    """Tasa en porcentaje, o None si no se puede calcular."""
    if not den or num is None:
        return None
    return round(num / den * 100, 2)
