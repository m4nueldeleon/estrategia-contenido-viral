# estrategia-contenido-viral

Skill de [Claude Code](https://claude.com/claude-code) que convierte datos reales
de Instagram y TikTok en guiones grabables.

No opina sobre contenido: mide, compara y cita. Cada guion que produce viene
anclado a dos o tres referencias con métricas verificadas, y cada afirmación del
documento final lleva su número al lado.

## Qué hace

1. **Audita tus cuentas** post por post: mediana real de reproducciones (nunca el
   promedio), likes por seguidor, umbrales de éxito y —lo que casi nadie mira—
   **qué pasó los 5 posts siguientes a cada pico.**
2. **Investiga a tu competencia** con un filtro duro de likes, en dos capas: el
   nicho directo y los *formatos prestados* de otros sectores que se puedan traer
   al tuyo. Esta segunda capa es la que produce los saltos de escala.
3. **Separa el contenido en las dos economías** —compartir y guardar— y demuestra
   con tus propios datos que casi ningún video hace las dos cosas.
4. **Construye N guiones** divididos en esos dos bloques y encadenados, con guion
   segundo a segundo, caption listo para copiar, referencias y nota de edición.
5. **Publica un Google Doc** público.

## El hallazgo que lo sostiene

Sobre 123 piezas con más de 10,000 likes, solo **2** estaban por encima del 2 %
en compartidos **y** en guardados a la vez. Las dos duraban menos de 10 segundos.

| | Economía de COMPARTIR | Economía de GUARDAR |
|---|---|---|
| Tasa típica | 1.1 % – 4.5 % de compartidos | 4.0 % – 7.6 % de guardados |
| Su otra tasa | 0.3 % – 2.2 % de guardados | 0.3 % – 0.9 % de compartidos |
| Qué es | humor, trends, opinión, storytime | rutinas, correcciones, series |
| Qué produce | seguidores nuevos | clientes |

No existe el video que crece y convierte al mismo tiempo. Hay que hacer dos, y
encadenarlos. Detalle completo en [`references/DOS-ECONOMIAS.md`](references/DOS-ECONOMIAS.md).

## Instalación

```bash
git clone https://github.com/<usuario>/estrategia-contenido-viral.git
ln -s "$PWD/estrategia-contenido-viral" ~/.claude/skills/estrategia-contenido-viral
cp estrategia-contenido-viral/.env.example ~/.apify-cli/.env   # y pon tu token
```

Requisitos: Python 3.10+ (solo biblioteca estándar), una cuenta de
[Apify](https://apify.com) y, para publicar el documento, el MCP de Google
Workspace.

## Uso

Desde Claude Code, en lenguaje natural:

> «Hazme una estrategia de 20 videos para @micuenta y @micuenta2»

O directamente los scripts:

```bash
# 1 · tus cuentas
python3 scripts/scrape_instagram.py --perfiles micuenta,micuenta2 --limite 80 --salida out/propias
python3 scripts/scrape_tiktok.py    --perfiles micuenta           --limite 40 --salida out/propias
python3 scripts/analizar_cuenta.py  --datos out/propias --corte 2026-09-07

# 2 · competencia: nicho + trends prestados
python3 scripts/scrape_tiktok.py    --buscar-nicho "pilates en casa;barre en casa" \
                                    --buscar-trends --salida out/comp
python3 scripts/scrape_instagram.py --perfiles comp1,comp2 --hashtags tag1,tag2 --salida out/comp
python3 scripts/analizar_competencia.py --datos out/comp --min-likes 10000 \
                                        --excluir micuenta --csv seleccion.csv

# 3 · documento
python3 scripts/construir_doc.py --guiones guiones/ --titulo "MARCA · 20 videos" --salida doc.html
```

Los scripts avisan del gasto de Apify antes de correr y se detienen solos al 90 %
del límite mensual.

## Estructura

```
SKILL.md                      las 8 fases, para Claude
references/
  METODOLOGIA.md              criterios de calidad por fase y checklist de guion
  DOS-ECONOMIAS.md            el análisis central
  FORMATOS-PORTABLES.md       catálogo de trends prestables, con números
  ANTIPATRONES.md             10 errores medidos, cada uno con su cifra
  UMBRALES.md                 cómo calcular umbrales por cuenta
  PREGUNTAS.md                banco de preguntas y cómo elegirlas
scripts/                      scrapers y analizadores (stdlib, sin dependencias)
templates/                    plantilla de guion y ficha de marca
casos/                        casos reales documentados
```

## Antipatrón número 1

El error más caro y el más repetido: **un video revienta y al día siguiente se
publica otra cosa.** Medido tres veces en la misma cuenta:

| Pico | Mediana de los 5 siguientes | Caída |
|---|---|---|
| 453,161 | 5,222 | −99 % |
| 240,341 | 9,781 | −96 % |
| 174,900 | 9,659 | −94 % |

`analizar_cuenta.py` lo detecta solo y lo marca. Los nueve antipatrones restantes
están en [`references/ANTIPATRONES.md`](references/ANTIPATRONES.md).

## Licencia

MIT.
