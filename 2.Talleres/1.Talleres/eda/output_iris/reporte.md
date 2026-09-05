# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['longitud_sepalo', 'ancho_sepalo', 'longitud_petalo', 'ancho_petalo']

Categóricas: []

| variable        |   n |   faltantes |   media |   mediana |   desv_std |   asimetria |   curtosis |
|:----------------|----:|------------:|--------:|----------:|-----------:|------------:|-----------:|
| longitud_sepalo | 150 |           0 |   5.843 |      5.8  |     0.8281 |      0.3118 |    -0.5736 |
| ancho_sepalo    | 150 |           0 |   3.057 |      3    |     0.4359 |      0.3158 |     0.181  |
| longitud_petalo | 150 |           0 |   3.758 |      4.35 |     1.765  |     -0.2721 |    -1.396  |
| ancho_petalo    | 150 |           0 |   1.199 |      1.3  |     0.7622 |     -0.1019 |    -1.336  |

## 2. Pruebas de normalidad (global y por clase)

|   n |   shapiro_p |   dagostino_p | veredicto   | variable        | grupo    |
|----:|------------:|--------------:|:------------|:----------------|:---------|
| 150 |   0.01018   |     0.05682   | no normal   | longitud_sepalo | (global) |
| 100 |   0.1464    |     0.4312    | normal      | longitud_sepalo | 0        |
|  50 |   0.4595    |     0.9075    | normal      | longitud_sepalo | 1        |
| 150 |   0.1012    |     0.2097    | normal      | ancho_sepalo    | (global) |
| 100 |   0.1262    |     0.5404    | normal      | ancho_sepalo    | 0        |
|  50 |   0.2715    |     0.3742    | normal      | ancho_sepalo    | 1        |
| 150 |   7.412e-10 |     7.265e-49 | no normal   | longitud_petalo | (global) |
| 100 |   0.7445    |     0.6244    | normal      | longitud_petalo | 0        |
|  50 |   0.05481   |     0.3268    | normal      | longitud_petalo | 1        |
| 150 |   1.68e-08  |     1.349e-30 | no normal   | ancho_petalo    | (global) |
| 100 |   0.001057  |     0.0002283 | no normal   | ancho_petalo    | 0        |
|  50 |   8.659e-07 |     0.0005703 | no normal   | ancho_petalo    | 1        |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable        |   levene_p |   fligner_p | veredicto   |
|:----------------|-----------:|------------:|:------------|
| longitud_sepalo |  7.386e-05 |   7.225e-05 | heterogénea |
| ancho_sepalo    |  0.4748    |   0.4907    | homogénea   |
| longitud_petalo |  2.493e-12 |   1.136e-11 | heterogénea |
| ancho_petalo    |  2.812e-15 |   2.781e-13 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable        |   n_clases | prueba            |   estadistico |   p_valor | significativo   |
|:----------------|-----------:|:------------------|--------------:|----------:|:----------------|
| longitud_sepalo |          2 | t-test de Welch   |       -15.14  | 7.709e-32 | True            |
| ancho_sepalo    |          2 | t-test de Student |         9.204 | 3.055e-16 | True            |
| longitud_petalo |          2 | t-test de Welch   |       -39.98  | 1.746e-69 | True            |
| ancho_petalo    |          2 | Mann-Whitney U    |         0     | 1.325e-23 | True            |


## 6. Correlación entre variables continuas

**Pearson:**

| index           |   longitud_sepalo |   ancho_sepalo |   longitud_petalo |   ancho_petalo |
|:----------------|------------------:|---------------:|------------------:|---------------:|
| longitud_sepalo |            1      |        -0.1176 |            0.8718 |         0.8179 |
| ancho_sepalo    |           -0.1176 |         1      |           -0.4284 |        -0.3661 |
| longitud_petalo |            0.8718 |        -0.4284 |            1      |         0.9629 |
| ancho_petalo    |            0.8179 |        -0.3661 |            0.9629 |         1      |

**Spearman:**

| index           |   longitud_sepalo |   ancho_sepalo |   longitud_petalo |   ancho_petalo |
|:----------------|------------------:|---------------:|------------------:|---------------:|
| longitud_sepalo |            1      |        -0.1668 |            0.8819 |         0.8343 |
| ancho_sepalo    |           -0.1668 |         1      |           -0.3096 |        -0.289  |
| longitud_petalo |            0.8819 |        -0.3096 |            1      |         0.9377 |
| ancho_petalo    |            0.8343 |        -0.289  |            0.9377 |         1      |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

_Sin datos suficientes._

## 8. Relevancia de variables frente a la clase (ranking)

| variable        |   anova_f_p |   kruskal_h_p |   info_mutua |
|:----------------|------------:|--------------:|-------------:|
| ancho_petalo    |   1.289e-51 |     1.299e-23 |       0.6399 |
| longitud_petalo |   3.623e-63 |     1.914e-23 |       0.6399 |
| longitud_sepalo |   5.289e-25 |     5.698e-20 |       0.4063 |
| ancho_sepalo    |   3.055e-16 |     2.981e-14 |       0.2584 |

## 9. Multicolinealidad (VIF y número de condición)

| variable        |    VIF |
|:----------------|-------:|
| longitud_petalo | 31.26  |
| ancho_petalo    | 16.09  |
| longitud_sepalo |  7.073 |
| ancho_sepalo    |  2.101 |

Índice de condición de la matriz estandarizada: 11.87

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable        |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:----------------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| longitud_sepalo |                          0 |                      0 |                  3.15 |                  8.35 |
| ancho_sepalo    |                          1 |                      4 |                  2.05 |                  4.05 |
| longitud_petalo |                          0 |                      0 |                 -3.65 |                 10.35 |
| ancho_petalo    |                          0 |                      0 |                 -1.95 |                  4.05 |

Mahalanobis multivariado: 0 outlier(s) de 150 filas evaluadas (umbral chi² = 18.5).

## 11. Balance de la variable objetivo

Clases: 2 (0: 100, 1: 50)

Prueba: Test binomial

p-valor: 5.448e-05

¿Desbalanceado respecto a distribución uniforme? Sí

