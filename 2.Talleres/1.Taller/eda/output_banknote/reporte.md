# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['varianza', 'asimetria', 'curtosis', 'entropia']

Categóricas: []

| variable   |    n |   faltantes |   media |   mediana |   desv_std |   asimetria |   curtosis |
|:-----------|-----:|------------:|--------:|----------:|-----------:|------------:|-----------:|
| varianza   | 1372 |           0 |  0.4337 |    0.4962 |      2.843 |     -0.1492 |    -0.7532 |
| asimetria  | 1372 |           0 |  1.922  |    2.32   |      5.869 |     -0.3937 |    -0.44   |
| curtosis   | 1372 |           0 |  1.398  |    0.6166 |      4.31  |      1.087  |     1.261  |
| entropia   | 1372 |           0 | -1.192  |   -0.5867 |      2.101 |     -1.021  |     0.4913 |

## 2. Pruebas de normalidad (global y por clase)

|    n |   shapiro_p |   dagostino_p | veredicto   | variable   | grupo    |
|-----:|------------:|--------------:|:------------|:-----------|:---------|
| 1372 |   4.686e-12 |     1.802e-21 | no normal   | varianza   | (global) |
|  762 |   8.765e-11 |     4.411e-08 | no normal   | varianza   | 0        |
|  610 |   0.0003136 |     0.007309  | no normal   | varianza   | 1        |
| 1372 |   8.224e-15 |     7.361e-12 | no normal   | asimetria  | (global) |
|  762 |   1.358e-16 |     2.879e-47 | no normal   | asimetria  | 0        |
|  610 |   8.562e-14 |     6.046e-09 | no normal   | asimetria  | 1        |
| 1372 |   2.759e-25 |     1.441e-49 | no normal   | curtosis   | (global) |
|  762 |   1.679e-11 |     1.637e-06 | no normal   | curtosis   | 0        |
|  610 |   1.687e-18 |     4.893e-16 | no normal   | curtosis   | 1        |
| 1372 |   4.471e-27 |     9.275e-40 | no normal   | entropia   | (global) |
|  762 |   2.353e-20 |     1.006e-21 | no normal   | entropia   | 0        |
|  610 |   1.806e-18 |     9.697e-20 | no normal   | entropia   | 1        |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable   |   levene_p |   fligner_p | veredicto   |
|:-----------|-----------:|------------:|:------------|
| varianza   |  0.01432   |   0.01651   | heterogénea |
| asimetria  |  0.4793    |   0.6419    | homogénea   |
| curtosis   |  4.878e-17 |   6.888e-13 | heterogénea |
| entropia   |  0.6204    |   0.6339    | homogénea   |

## 4-5. Comparación de variables continuas entre clases

| variable   |   n_clases | prueba         |   estadistico |    p_valor | significativo   |
|:-----------|-----------:|:---------------|--------------:|-----------:|:----------------|
| varianza   |          2 | Mann-Whitney U |     4.31e+05  | 2.357e-163 | True            |
| asimetria  |          2 | Mann-Whitney U |     3.483e+05 | 8.035e-57  | True            |
| curtosis   |          2 | Mann-Whitney U |     2.158e+05 | 0.02256    | True            |
| entropia   |          2 | Mann-Whitney U |     2.413e+05 | 0.2253     | False           |


## 6. Correlación entre variables continuas

**Pearson:**

| index     |   varianza |   asimetria |   curtosis |   entropia |
|:----------|-----------:|------------:|-----------:|-----------:|
| varianza  |     1      |      0.264  |    -0.3808 |     0.2768 |
| asimetria |     0.264  |      1      |    -0.7869 |    -0.5263 |
| curtosis  |    -0.3808 |     -0.7869 |     1      |     0.3188 |
| entropia  |     0.2768 |     -0.5263 |     0.3188 |     1      |

**Spearman:**

| index     |   varianza |   asimetria |   curtosis |   entropia |
|:----------|-----------:|------------:|-----------:|-----------:|
| varianza  |     1      |      0.2551 |    -0.3267 |     0.2415 |
| asimetria |     0.2551 |      1      |    -0.7294 |    -0.5725 |
| curtosis  |    -0.3267 |     -0.7294 |     1      |     0.4333 |
| entropia  |     0.2415 |     -0.5725 |     0.4333 |     1      |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

_Sin datos suficientes._

## 8. Relevancia de variables frente a la clase (ranking)

| variable   |   anova_f_p |   kruskal_h_p |   info_mutua |
|:-----------|------------:|--------------:|-------------:|
| varianza   |  5.741e-224 |    2.353e-163 |      0.378   |
| asimetria  |  1.372e-67  |    8.026e-57  |      0.2278  |
| curtosis   |  6.466e-09  |    0.02256    |      0.1237  |
| entropia   |  0.386      |    0.2253     |      0.01958 |

## 9. Multicolinealidad (VIF y número de condición)

| variable   |   VIF |
|:-----------|------:|
| asimetria  | 3.505 |
| curtosis   | 2.874 |
| entropia   | 1.865 |
| varianza   | 1.531 |

Índice de condición de la matriz estandarizada: 3.52

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable   |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:-----------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| varianza   |                          0 |                      0 |                -8.665 |                 9.713 |
| asimetria  |                          0 |                      0 |               -14.49  |                19.6   |
| curtosis   |                         20 |                     59 |                -8.706 |                10.31  |
| entropia   |                         16 |                     33 |                -6.626 |                 4.607 |

Mahalanobis multivariado: 8 outlier(s) de 1372 filas evaluadas (umbral chi² = 18.5).

## 11. Balance de la variable objetivo

Clases: 2 (0: 762, 1: 610)

Prueba: Test binomial

p-valor: 4.494e-05

¿Desbalanceado respecto a distribución uniforme? Sí

