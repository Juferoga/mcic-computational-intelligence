# Prueba de factibilidad (compuerta de viabilidad, 7 de noviembre de 2026)

Datos: clon bare completo de `torvalds/linux`, con corte en el último commit del 6 de noviembre de 2026. La tabla se generó con `src/minar_kernel.py` y el análisis con `src/factibilidad.py`. Todas las cifras salen de `resultados.json`.

**Veredicto: el plan A es viable.** Hay datos de sobra, la etiqueta funciona, los modelos simples encuentran señal clara y se ve deriva en 2026. El riesgo real está en el criterio C1: un árbol de 15 hojas queda en el 90 % del AUC-PR de la regresión logística, y la meta es el 95 %.

## 1. Datos y etiqueta

- 1.001.080 commits sin merges desde 2014. De ellos, 974.947 tienen al menos 90 días de observación y 26.133 están censurados (agosto a noviembre de 2026).
- 151.705 referencias `Fixes:`, de las cuales se resuelve el 90,6 % a un commit de mainline. El resto apunta a commits anteriores a 2014 o a otros árboles.
- Prevalencia de la clase "riesgoso" (`Fixes:` en 90 días o menos) por año:

| Año | Commits | Riesgosos | Prevalencia |
|---|---:|---:|---:|
| 2014 | 70.096 | 537 | 0,77 % |
| 2016 | 70.928 | 2.016 | 2,84 % |
| 2018 | 73.963 | 2.865 | 3,87 % |
| 2019 | 76.493 | 3.265 | 4,27 % |
| 2021 | 79.671 | 3.558 | 4,47 % |
| 2023 | 84.780 | 3.295 | 3,89 % |
| 2025 | 78.150 | 3.336 | 4,27 % |
| 2026 (ene–jul) | 57.355 | 1.947 | 3,39 % |

**Decisión que se desprende de los datos:** entre 2014 y 2018 la prevalencia sube porque el uso del trailer `Fixes:` se fue adoptando, no porque hubiera más bugs. Entrenar con esos años mezclaría la adopción de la etiqueta con el riesgo. **El entrenamiento debe empezar en 2019**, cuando la prevalencia ya es estable (cerca del 4 %).

## 2. Hay señal

Los modelos se entrenaron con 2019–2022 (319.007 commits, 4,37 % positivos), sin ajuste de hiperparámetros, y se evaluaron por año. La clase mayoritaria tiene un AUC-PR igual a la prevalencia.

| Modelo | 2023 | 2024 | 2025 | 2026 ene–jul |
|---|---|---|---|---|
| Clase mayoritaria | 0,039 | 0,041 | 0,043 | 0,035 |
| Regresión logística | 0,151 [0,141–0,162] | 0,143 | 0,152 [0,143–0,161] | 0,127 [0,115–0,139] |
| Gradient boosting | 0,156 | 0,147 | 0,154 | 0,126 [0,115–0,138] |
| Árbol de 15 hojas | 0,134 | 0,130 | 0,139 | 0,115 [0,104–0,123] |

Los corchetes son intervalos de confianza del 95 % por bootstrap. El AUC-ROC de la regresión logística está entre 0,76 y 0,78, en línea con la literatura (Kamei 2013: 0,73).

- Los modelos superan entre 3,5 y 4 veces a la clase mayoritaria. Hay señal.
- Gradient boosting no supera a la regresión logística. Esto coincide con Zeng 2021 y le deja espacio a un modelo simple.
- El árbol de 15 hojas alcanza el **90 %** del AUC-PR de la regresión logística en 2026 (0,115 frente a 0,127). El criterio C1 pide el 95 %, así que el modelo difuso-evolutivo tiene que cerrar esa brecha. Es plausible, porque las funciones de pertenencia suavizan los cortes duros del árbol y la evolución ajusta los umbrales, pero no está garantizado.
- Las reglas del árbol usan sobre todo el tamaño (`lineas_add`, `lineas_del`) y la difusión (`n_subsistemas`, `n_dirs_raiz`), igual que el JIT clásico.

## 3. Deriva hacia 2026

- El AUC-PR cae de 0,152 en 2025 a 0,127 en 2026 con la regresión logística, y los intervalos no se solapan. Parte de la caída viene de que la prevalencia baja (4,27 % a 3,46 %): el cociente AUC-PR/prevalencia casi no cambia (3,55 frente a 3,67). Medir solo AUC-PR exagera la deriva, así que conviene reportar también el cociente.
- **Cambia la mezcla de commits:** los que traen `Fixes:` pasan del 18,4 % (2025) al 26,3 % (2026). Es una deriva de covariables, que es justo lo que anticipaba la literatura sobre contribuciones con IA.

### `Assisted-by` en 2026

| Mes | Commits | Con `Assisted-by` |
|---|---:|---:|
| ene | 8.157 | 1 |
| mar | 8.951 | 75 |
| may | 8.230 | 334 |
| jul | 10.257 | 881 (8,6 %) |
| sep | 10.830 | 1.739 (16,1 %) |
| oct | 9.668 | 1.754 (18,1 %) |

- Entre enero y julio (los meses observados), 2.031 commits traen la etiqueta. Su prevalencia es 2,8 %, frente a 3,5 % de los que no la traen. Es una diferencia descriptiva y sin prueba formal. Además, los commits con etiqueta son más recientes y tienen menos tiempo para recibir un `Fixes:`, aunque todos superan los 90 días.
- Los valores más comunes son `LLM` (1.695) y luego modelos concretos: `Claude:claude-opus-*`, `Antigravity:gemini-3.1-pro`, `Cursor:claude-opus-5`.
- El tamaño del subgrupo alcanza para un análisis descriptivo, no para conclusiones causales, como ya preveía el plan.

## 4. Advertencias metodológicas

- **Ya se miró la prueba de 2026.** Esta compuerta evaluó modelos simples en enero–julio de 2026, el periodo reservado como prueba. Para no invalidarla, ninguna decisión del modelo final (variables, hiperparámetros, número de reglas) puede tomarse a partir de las cifras de 2026 de este informe; esas decisiones se toman solo con la validación de 2020 a 2025. Esto se declara en el artículo como análisis de factibilidad previo.
- La fecha usada es la del committer. Los parches de un árbol de subsistema entran a mainline semanas después, cosa que no afecta la etiqueta pero sí la ventana exacta.
- Los `Fixes:` que apuntan a backports de stable no se cuentan, porque solo se mineó mainline.
