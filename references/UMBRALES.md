# Umbrales

Los umbrales son **por cuenta** y se recalculan en cada tanda. Un número que es
un éxito en una cuenta de 4,000 seguidores es un fracaso en una de 200,000.

## Cómo se calculan

Sobre la **mediana de reproducciones** de la cuenta, con los últimos 40–80 posts:

| Resultado | Fórmula | Qué significa | Qué se hace |
|---|---|---|---|
| Bajo | < 0.7 × mediana | Falló el hook | Revisar los primeros 3 segundos |
| Normal | 0.7 – 1.6 × mediana | Llegó a los seguidores, no salió de ahí | Nada |
| Bueno | 1.6 – 4 × mediana | El algoritmo lo empujó fuera de la cuenta | Anotar el formato |
| **Muy bueno** | 4 – 12 × mediana | Formato ganador | **Parte 2 en 72 h. Parte 3 antes de 10 días.** |
| Viral | > 12 × mediana | Techo roto | Parte 2 en 48 h y la tanda se reordena alrededor de ese formato |

`scripts/analizar_cuenta.py` los calcula e imprime la tabla lista para el documento.

## Las tres tasas

Se vigilan siempre, y pesan más que las reproducciones.

| Tasa | Cálculo | Objetivo | Qué predice |
|---|---|---|---|
| **Compartido** | compartidos ÷ reproducciones | > 2 % en el bloque de compartir | Seguidores nuevos. Es la única métrica que los predice |
| **Guardado** | guardados ÷ reproducciones | > 4 % en el bloque de guardar | Intención de compra |
| **Comentarios** | comentarios ÷ reproducciones | > 0.1 % en todos | Que el contenido generó conversación, no solo consumo |

## Revisión semanal, diez minutos

Cada lunes:

1. Anotar las tres tasas de los videos de la semana anterior.
2. Marcar el mejor.
3. **¿Alguno pasó «muy bueno»?** Si sí, el calendario de esa semana se rompe y la
   secuela entra en el hueco reservado.

Sin este paso, la regla de repetición no se cumple. Está documentado que se
incumple sola: ver `ANTIPATRONES.md` §1.

## Advertencia sobre las métricas de las plataformas

- **Reproducciones ≠ vistas.** Instagram reporta las dos y son muy distintas
  (en el caso Anyara, 453,161 contra 252,252 en la misma pieza). Elegir una y
  no mezclarlas nunca dentro de una misma tabla.
- Las cifras de una pieza siguen creciendo. Lo que no cambia es la **proporción**
  entre piezas, que es lo que se usa para decidir.
- Anotar siempre la fecha de corte de los datos.
