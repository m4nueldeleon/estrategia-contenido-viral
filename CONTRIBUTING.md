# Cómo contribuir

Lo más útil que puedes aportar no es código: son **casos con números**.

## Añadir un caso

Un archivo en `casos/<marca>-<AAAA-MM>.md` con volumen revisado, hallazgos con
su cifra, decisiones tomadas y qué revisar la próxima vez. Sin datos sensibles
ni cifras privadas de negocio: métricas públicas de las plataformas y nada más.

## Añadir un formato portable

En `references/FORMATOS-PORTABLES.md`, solo si pasa las tres pruebas:

1. La estructura se explica en una frase sin mencionar el tema original
2. El tema es intercambiable
3. **Funciona en cuentas chicas** — busca un caso de menos de 5,000 seguidores
   con millones de reproducciones

Siempre con el enlace y el número medido.

## Añadir un antipatrón

En `references/ANTIPATRONES.md`, con la cifra que lo delata. Un antipatrón sin
número es una opinión.

## Código

Solo biblioteca estándar de Python. Sin dependencias: la skill tiene que correr
en cualquier máquina con `python3` y nada más instalado. Si una idea necesita un
paquete, casi siempre hay una forma de hacerla sin él.

Antes de abrir un PR, prueba los scripts contra datos reales y pega la salida.
