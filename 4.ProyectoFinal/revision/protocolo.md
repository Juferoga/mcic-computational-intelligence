# Protocolo de la revisión (Fase 1)

Escrito el 2026-11-06, **antes** del tamizaje. Si algo cambia después, se anota abajo con fecha y motivo.

## Problema en una frase

Predecir, en el momento de integrarlo, si un commit del kernel de Linux será corregido después (riesgo), con un modelo interpretable que siga funcionando cuando cambian los datos, en particular con la llegada de contribuciones asistidas por IA.

## Bloques de búsqueda (OR dentro, AND entre bloques)

| Bloque | Términos |
| --- | --- |
| A Dominio | commit(s), code change(s), software change(s), patch(es), pull request(s), Linux kernel |
| B Tarea | defect prediction, bug prediction, bug-introducing, bug-inducing, fix-inducing, just-in-time, change risk, risk prediction, defect-prone, buggy |
| C Método | fuzzy, rule-based, evolutionary, genetic algorithm, genetic programming, search-based, interpretable/interpretability, explainable/explainability |
| C' Deriva | concept drift, drift, temporal validation, time-aware, realistic evaluation, data shift, distribution shift, time travel |

- **Q1** = A AND B AND C (el método propuesto).
- **Q2** = A AND B AND C' (la validez temporal, que es la brecha).
- Rango: 2019–2026. Los clásicos muy citados (anteriores a 2019) entran como "identificados por otros métodos" en el diagrama PRISMA.
- Bases: arXiv (API pública, `busqueda_arxiv.py`) y OpenAlex (API pública, `busqueda_openalex.py`, búsqueda en título y resumen). OpenAlex indexa IEEE, ACM, Springer, Elsevier y arXiv. Se usan las mismas cadenas expandidas en las dos bases.

## Criterios de inclusión

- **I1 Misma tarea.** Predice el riesgo de un cambio individual (defecto, bug o vulnerabilidad a nivel de commit, parche o PR), o estudia la validez de cómo se evalúa esa predicción (orden temporal, deriva, latencia de la etiqueta, ruido de SZZ o `Fixes:`).
- **I2 Métricas cuantitativas.** Reporta al menos una métrica de desempeño o de validez.
- **I3 Datos descritos.** Dice qué proyectos, cuántos cambios y cómo se etiquetaron.

## Criterios de exclusión

- **E1** Reparación automática de programas, generación de pruebas o de código sin predicción de riesgo.
- **E2** Predicción solo a nivel de archivo, clase o método. Se exceptúan los trabajos difusos o evolutivos de predicción de defectos, que se admiten si no hay equivalentes a nivel de cambio, y se señalan así en la matriz.
- **E3** Otro dominio (medicina, robótica, etc.).
- **E4** Solo dataset o herramienta, sin evaluación predictiva.
- **E5** No es un trabajo académico (blog, presentación) o no se puede verificar.

## Rondas

1. Título y resumen.
2. Texto completo, cuando está disponible. Si no, la matriz marca la fila "solo resumen".

## Cambios al protocolo

- **2026-11-07.** Se reemplaza IEEE Xplore por OpenAlex como segunda base: el autor no tiene el acceso institucional y OpenAlex se puede consultar de forma reproducible por API. Esto se aparta de "Scopus o IEEE Xplore" del enunciado y se declara en el artículo. Los criterios no cambian. El tamizaje de OpenAlex se hizo con los mismos criterios, después del de arXiv.
