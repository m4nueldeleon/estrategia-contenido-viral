---
name: estrategia-contenido-viral
description: >-
  Sistema de investigación y estrategia de contenido para cuentas de Instagram y
  TikTok. Audita las cuentas propias con métricas post por post, investiga a la
  competencia con un filtro duro de likes, detecta formatos portables de otros
  sectores, separa el contenido en las dos economías (compartir vs guardar) y
  construye N guiones listos para grabar, cada uno anclado a referencias con
  números verificados. Entrega un Google Doc público. TRIGGERS: "estrategia de
  contenido", "hazme N guiones", "investiga a mi competencia", "qué contenido
  grabo", "guiones para grabar", "analiza mis redes y dame un plan", "trends que
  pueda traer a mi nicho". NO usar para editar video (viral-short-video), para
  carruseles (carruseles-virales-ia), ni para auditar UNA sola cuenta sin producir
  guiones (instagram-audit).
metadata:
  author: Manuel de León
  version: 1.0.0
  licencia: MIT
  primer_caso: "Anyara · @anyaramove + @mariana.dlrz · 2026-09-18"
  requiere: APIFY_TOKEN, acceso a Google Drive
---

# Estrategia de contenido viral

Convierte datos reales en guiones grabables. No opina: mide, compara y cita.

## Regla que manda sobre todas

**Ninguna afirmación sin un número al lado, y ningún número sin su fuente.**
Si una cifra no salió de un scrape de esta sesión, no entra al documento.
Un guion sin al menos dos referencias con métricas verificadas no está terminado.

---

## Fase 0 · Base histórica

Antes de investigar nada, buscar si ya existe trabajo previo sobre esta marca:

```bash
# en el workspace
grep -ril "<marca>" --include="*.md" . | head
# en Drive
```
Buscar en Google Drive por el nombre de la marca y leer el documento anterior
**completo**. De ahí salen tres cosas que no se vuelven a calcular: la voz de la
persona (frases textuales suyas), el manual de edición y las reglas que ya se
fijaron. Si ya hay guiones anteriores, **los nuevos no los repiten**: se listan
los títulos viejos y se verifica uno por uno.

Si no existe trabajo previo, se salta a la Fase 1 y el manual de edición se
construye desde cero en la Fase 5.

---

## Fase 1 · Auditoría de las cuentas propias

```bash
python3 scripts/scrape_instagram.py --perfiles cuenta1,cuenta2 --limite 80 --salida out/
python3 scripts/scrape_tiktok.py     --perfiles cuenta1,cuenta2 --limite 40 --salida out/
python3 scripts/analizar_cuenta.py   --datos out/ --corte <fecha-del-doc-anterior>
```

Lo que hay que salir sabiendo, por cuenta:

| Dato | Para qué |
|---|---|
| Seguidores y crecimiento desde el corte | Saber si algo se movió |
| **Mediana** de reproducciones (nunca el promedio) | La línea base real; el promedio lo secuestra un viral |
| Likes por seguidor | Comparar cuentas de distinto tamaño |
| Top 8 por reproducciones, no por likes | El alcance y el cariño son cosas distintas |
| Mediana antes y después del corte | Si la cuenta sube o baja |
| Qué pasó **los 5 posts siguientes** a cada pico | Aquí es donde casi siempre está el error |

> Si hay varias cuentas, comparar medianas. Es frecuente que la cuenta personal
> rinda varias veces la cuenta de marca. Ese dato reordena toda la estrategia y
> hay que ponerlo en la primera tabla del documento.

Leer `references/ANTIPATRONES.md` antes de escribir el diagnóstico.

---

## Fase 2 · Las preguntas

Con los datos en mano, y solo entonces, preguntar. Las preguntas se hacen
**después** de la auditoría porque los datos cambian cuáles son las preguntas
que importan.

Buenas preguntas: las que cambian el trabajo según la respuesta.
Malas preguntas: las que ya están contestadas en los datos.

Ver `references/PREGUNTAS.md` para el banco de preguntas y cómo elegir.

---

## Fase 3 · Competencia

```bash
python3 scripts/scrape_tiktok.py --buscar-nicho --buscar-trends --limite 40 --salida out/
python3 scripts/scrape_instagram.py --perfiles <lista> --hashtags <lista> --salida out/
python3 scripts/analizar_competencia.py --datos out/ --min-likes 10000
```

Dos capas, siempre las dos:

1. **Nicho directo** — quién hace lo mismo y le funciona.
2. **Trends prestados** — formatos de otros sectores (comedia, pareja, moda,
   amistad, escuela, viajes) que se puedan traer al nicho. *Esta capa es la que
   produce los saltos de escala.* Sin ella solo se replica el techo del nicho.

**Filtro duro:** solo piezas por encima del umbral de likes acordado (10,000 por
omisión). **Tope por autor:** máximo 2 por cuenta en TikTok y 4 en Instagram,
para que la muestra no la domine un solo creador.

---

## Fase 4 · Las dos economías

Este es el análisis que convierte el scrape en estrategia. Leer
`references/DOS-ECONOMIAS.md` **completo** antes de seguir.

Resumen: calcular para cada pieza `compartidos ÷ reproducciones` y
`guardados ÷ reproducciones`. Aparecen dos grupos que casi no se tocan. Casi
ningún video hace las dos cosas. Los guiones se dividen deliberadamente en dos
bloques y se **encadenan**: uno trae gente, el siguiente la convierte.

De aquí sale también el catálogo de formatos portables: ver
`references/FORMATOS-PORTABLES.md`.

---

## Fase 5 · Los guiones

Cada guion lleva, sin excepción:

- **Ficha** — formato, duración, dónde se publica, qué economía
- **Set** — cómo se graba, en una frase que el que graba pueda seguir
- **Guion en tabla** — `Segundo | Dices | Se ve`
- **Caption** — listo para copiar y pegar, con la rutina completa escrita si es de guardar
- **Referencias** — 2 o 3, con sus métricas y qué copiar exactamente de cada una
- **Edición** — lo que el editor necesita y nada más

Reglas de construcción en `references/METODOLOGIA.md` §5.
Plantilla en `templates/guion.md`.

---

## Fase 6 · Reglas, calendario y medición

- Proporción alternada entre las dos economías
- **Regla de repetición con fecha**: si un video pasa el umbral de «muy bueno»,
  la secuela entra en 72 horas. En el calendario hay una casilla reservada para
  esto, no es una nota al pie. Es el error que más se repite.
- Umbrales recalculados por cuenta sobre su mediana actual: `references/UMBRALES.md`
- Las tres tasas que se vigilan: compartido, guardado y comentarios

---

## Fase 7 · Entrega

```bash
python3 scripts/construir_doc.py --datos out/ --guiones guiones/ --salida doc.html
```

Publicar como Google Doc:

```
import_to_google_doc(file_path=..., source_format="html")
set_drive_file_permissions(file_id=..., link_sharing="writer")
```

> El archivo tiene que estar dentro de `ALLOWED_FILE_DIRS`
> (por omisión `~/.workspace-mcp/attachments`). Si la Docs API está deshabilitada,
> `import_to_google_doc` funciona igual: usa la conversión de Drive.

---

## Fase 8 · Cierre

Guardar el caso en `casos/<marca>-<AAAA-MM>.md` con: qué se encontró, qué se
decidió y **qué habría que revisar la próxima vez**. Ese archivo es lo que hace
que la segunda pasada sea más barata que la primera.
