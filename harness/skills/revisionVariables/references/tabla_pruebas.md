# Tabla de referencia completa — Pruebas estadísticas para revisión de variables en datasets de clasificación

Consulta este archivo cuando necesites el detalle fino de una prueba puntual
(cuándo usarla, notas, alternativas). El `SKILL.md` trae el resumen ejecutable;
aquí está el marco teórico completo.

## 1. Análisis exploratorio previo (paso 0, obligatorio)

- Tipificación de variables: continuas, discretas, categóricas (nominales/ordinales), variable objetivo (binaria o multiclase).
- Estadísticos descriptivos: media, mediana, desviación estándar, asimetría (skewness), curtosis, valores faltantes.
- Visualización: histogramas, boxplots por clase, Q-Q plots.

Este paso determina la ruta paramétrica vs. no paramétrica de todo lo que sigue.

## 2. Pruebas de normalidad

| Prueba | Uso típico | Notas |
|---|---|---|
| Shapiro-Wilk | Muestras pequeñas/medianas (n < 50–2000) | La más recomendada en la práctica |
| Kolmogorov-Smirnov (con corrección de Lilliefors) | Muestras más grandes | Menos potente que Shapiro-Wilk |
| Anderson-Darling | Alternativa robusta, sensible a colas | Buena para detectar desviaciones en extremos |
| D'Agostino-Pearson (K²) | Basada en skewness y curtosis conjuntas | Útil como complemento |

## 3. Pruebas de homogeneidad de varianzas (homocedasticidad)

Necesarias antes de aplicar t-test/ANOVA "clásicos" entre clases.

| Prueba | Cuándo usarla |
|---|---|
| Levene | Robusta, no exige normalidad estricta (la más usada) |
| Bartlett | Solo si los datos ya son normales (muy sensible a violaciones) |
| Fligner-Killeen | Alternativa no paramétrica, robusta a outliers |

## 4. Comparación de variables continuas entre clases (2 clases)

**Paramétricas** (si hay normalidad + homocedasticidad):
- t-test de Student (varianzas iguales)
- t-test de Welch (varianzas desiguales) — buena práctica por defecto si hay duda

**No paramétricas** (si no hay normalidad):
- Mann-Whitney U (Wilcoxon rank-sum)

## 5. Comparación de variables continuas entre clases (>2 clases, multiclase)

**Paramétrica:** ANOVA de un factor (requiere normalidad + homocedasticidad)
  - Post-hoc: Tukey HSD, Bonferroni

**No paramétrica:** Kruskal-Wallis
  - Post-hoc: Dunn's test con corrección (Bonferroni/Holm)

## 6. Correlación entre variables continuas

| Prueba | Tipo | Cuándo usarla |
|---|---|---|
| Pearson | Paramétrica | Relación lineal, variables normales |
| Spearman | No paramétrica | Relación monótona, datos ordinales o no normales |
| Kendall (tau) | No paramétrica | Muestras pequeñas, más robusta ante empates |

## 7. Asociación entre variables categóricas (incluida la variable objetivo)

| Prueba | Uso |
|---|---|
| Chi-cuadrado de independencia (χ²) | Tablas de contingencia, muestras suficientes por celda (regla: esperado ≥5) |
| Test exacto de Fisher | Tablas 2x2 con muestras pequeñas o celdas con conteo bajo |
| V de Cramér | Tamaño del efecto de la asociación categórica (complementa χ²) |
| Coeficiente de contingencia / Phi | Alternativas de tamaño de efecto para tablas pequeñas |

## 8. Relevancia/selección de variables respecto a la clase

- ANOVA F-test (`f_classif`) — continua vs. clase, ruta paramétrica
- Chi-cuadrado (`chi2`) — categórica vs. clase (variables no negativas)
- Información Mutua (`mutual_info_classif`) — no paramétrica, captura relaciones no lineales
- Kruskal-Wallis H — como criterio de ranking no paramétrico de variables

## 9. Multicolinealidad entre variables predictoras

- Matriz de correlación (Pearson/Spearman) + mapa de calor
- VIF (Variance Inflation Factor) — regla práctica: VIF > 5–10 indica colinealidad problemática
- Índice de condición (condition number) de la matriz de diseño

## 10. Detección de outliers/atípicos

- Z-score (paramétrico, asume normalidad)
- Rango intercuartílico (IQR, regla 1.5×IQR) — no paramétrico, el más robusto y usado
- Test de Grubbs — outlier único bajo normalidad
- Distancia de Mahalanobis — multivariante, detecta outliers conjuntos

## 11. Balance de la variable objetivo (clase)

Test binomial (caso binario) o Chi-cuadrado de bondad de ajuste (multiclase) contra la
hipótesis de distribución uniforme/esperada, para cuantificar el desbalance de clases.

## 12. Casos especiales

| Situación | Prueba recomendada |
|---|---|
| Datos pareados/repetidos (mismo sujeto, dos condiciones) | Wilcoxon signed-rank (no paramétrica) / t-test pareado (paramétrica) |
| Comparación de más de 2 mediciones pareadas categóricas | Q de Cochran |
| Comparación de 2 mediciones categóricas pareadas | McNemar |

## 13. Técnicas gráficas complementarias

Estas no reemplazan las pruebas estadísticas, pero son el primer diagnóstico visual.

### 13.1 Distribución de una variable (univariado)
- Histograma con KDE superpuesta → forma, sesgo, multimodalidad
- Boxplot → mediana, dispersión, outliers
- Violin plot → boxplot + densidad, útil para comparar forma entre clases
- Q-Q plot → contraste visual de normalidad (complemento de Shapiro-Wilk/K-S)
- ECDF → distribución observada vs. teórica

### 13.2 Comparación entre clases
- Boxplot/Violin plot por clase → apoya t-test/Mann-Whitney/ANOVA/Kruskal-Wallis
- Ridgeline plot (joyplot) → varias distribuciones apiladas, útil con muchas clases
- Strip/swarm plot → puntos individuales sobre el boxplot, útil en muestras pequeñas

### 13.3 Relación entre dos variables continuas
- Scatter plot coloreado por clase → relación y separabilidad visual
- Scatter plot matrix / pairplot → relaciones dos a dos, clase como color
- Hexbin / density scatter → cuando hay demasiados puntos

### 13.4 Correlación y multicolinealidad
- Mapa de calor de correlación (Pearson/Spearman)
- Dendrograma de correlación (clustermap) → agrupa variables redundantes

### 13.5 Categóricas y variable objetivo
- Barras / countplot → frecuencia de categorías, balance de clases
- Barras apiladas/agrupadas por clase → asociación categórica visual
- Mosaic plot → visualización proporcional de tablas de contingencia

### 13.6 Outliers
- Boxplot (regla 1.5×IQR) → outliers univariados
- Scatter con elipses de confianza → outliers multivariados (relacionado con Mahalanobis)

### 13.7 Reducción de dimensionalidad para inspección global
- PCA (biplot / componentes principales) → separabilidad global, varianza explicada
- t-SNE → estructura no lineal/clusters en alta dimensión
- UMAP → alternativa a t-SNE, más rápida, suele preservar mejor la estructura global

### 13.8 Valores faltantes
- Matriz/mapa de calor de nulos (e.g. `missingno`) → patrones aleatorios vs. sistemáticos
