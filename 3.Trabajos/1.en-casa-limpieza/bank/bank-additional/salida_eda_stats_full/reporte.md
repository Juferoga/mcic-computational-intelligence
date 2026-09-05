# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['age', 'duration', 'campaign', 'pdays', 'previous', 'emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed']

Categóricas: ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'day_of_week', 'poutcome']

| variable       |     n |   faltantes |      media |   mediana |   desv_std |   asimetria |   curtosis |
|:---------------|------:|------------:|-----------:|----------:|-----------:|------------:|-----------:|
| age            | 41188 |           0 |   40.02    |    38     |    10.42   |      0.7847 |   0.7911   |
| duration       | 41188 |           0 |  258.3     |   180     |   259.3    |      3.263  |  20.25     |
| campaign       | 41188 |           0 |    2.568   |     2     |     2.77   |      4.762  |  36.98     |
| pdays          | 41188 |           0 |  962.5     |   999     |   186.9    |     -4.922  |  22.23     |
| previous       | 41188 |           0 |    0.173   |     0     |     0.4949 |      3.832  |  20.11     |
| emp.var.rate   | 41188 |           0 |    0.08189 |     1.1   |     1.571  |     -0.7241 |  -1.063    |
| cons.price.idx | 41188 |           0 |   93.58    |    93.75  |     0.5788 |     -0.2309 |  -0.8299   |
| cons.conf.idx  | 41188 |           0 |  -40.5     |   -41.8   |     4.628  |      0.3032 |  -0.3587   |
| euribor3m      | 41188 |           0 |    3.621   |     4.857 |     1.734  |     -0.7092 |  -1.407    |
| nr.employed    | 41188 |           0 | 5167       |  5191     |    72.25   |     -1.044  |  -0.003906 |

## 2. Pruebas de normalidad (global y por clase)

|     n |   ks_lilliefors_p |   dagostino_p | veredicto   | variable       | grupo    |   shapiro_p |
|------:|------------------:|--------------:|:------------|:---------------|:---------|------------:|
| 41188 |        3.769e-320 |    0          | no normal   | age            | (global) | nan         |
| 36548 |        3.042e-274 |    0          | no normal   | age            | no       | nan         |
|  4640 |      nan          |    2.702e-131 | no normal   | age            | yes      |   5.708e-43 |
| 41188 |        0          |    0          | no normal   | duration       | (global) | nan         |
| 36548 |        0          |    0          | no normal   | duration       | no       | nan         |
|  4640 |      nan          |    0          | no normal   | duration       | yes      |   6.002e-54 |
| 41188 |        0          |    0          | no normal   | campaign       | (global) | nan         |
| 36548 |        0          |    0          | no normal   | campaign       | no       | nan         |
|  4640 |      nan          |    0          | no normal   | campaign       | yes      |   1.733e-71 |
| 41188 |        0          |    0          | no normal   | pdays          | (global) | nan         |
| 36548 |        0          |    0          | no normal   | pdays          | no       | nan         |
|  4640 |      nan          |    5.984e-200 | no normal   | pdays          | yes      |   2.314e-78 |
| 41188 |        0          |    0          | no normal   | previous       | (global) | nan         |
| 36548 |        0          |    0          | no normal   | previous       | no       | nan         |
|  4640 |      nan          |    0          | no normal   | previous       | yes      |   2.682e-72 |
| 41188 |        0          |    0          | no normal   | emp.var.rate   | (global) | nan         |
| 36548 |        0          |    0          | no normal   | emp.var.rate   | no       | nan         |
|  4640 |      nan          |    2.757e-263 | no normal   | emp.var.rate   | yes      |   1.178e-55 |
| 41188 |        0          |    0          | no normal   | cons.price.idx | (global) | nan         |
| 36548 |        0          |    0          | no normal   | cons.price.idx | no       | nan         |
|  4640 |      nan          |    2.038e-311 | no normal   | cons.price.idx | yes      |   1.129e-36 |
| 41188 |        0          |    4.667e-204 | no normal   | cons.conf.idx  | (global) | nan         |
| 36548 |        0          |    1.043e-216 | no normal   | cons.conf.idx  | no       | nan         |
|  4640 |      nan          |    1.142e-91  | no normal   | cons.conf.idx  | yes      |   3.998e-33 |
| 41188 |        0          |    0          | no normal   | euribor3m      | (global) | nan         |
| 36548 |        0          |    0          | no normal   | euribor3m      | no       | nan         |
|  4640 |      nan          |    0          | no normal   | euribor3m      | yes      |   3.605e-68 |
| 41188 |        0          |    0          | no normal   | nr.employed    | (global) | nan         |
| 36548 |        0          |    0          | no normal   | nr.employed    | no       | nan         |
|  4640 |      nan          |    0          | no normal   | nr.employed    | yes      |   1.125e-49 |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable       |   levene_p |   fligner_p | veredicto   |
|:---------------|-----------:|------------:|:------------|
| age            | 1.096e-150 |  1.409e-112 | heterogénea |
| duration       | 0          |  0          | heterogénea |
| campaign       | 1.438e-29  |  3.671e-28  | heterogénea |
| pdays          | 0          |  0          | heterogénea |
| previous       | 0          |  0          | heterogénea |
| emp.var.rate   | 3.165e-07  |  5.498e-12  | heterogénea |
| cons.price.idx | 2.023e-53  |  1.328e-45  | heterogénea |
| cons.conf.idx  | 3.747e-227 |  0          | heterogénea |
| euribor3m      | 1.087e-06  |  4.422e-94  | heterogénea |
| nr.employed    | 6.364e-225 |  3.594e-164 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable       |   n_clases | prueba         |   estadistico |    p_valor | significativo   |
|:---------------|-----------:|:---------------|--------------:|-----------:|:----------------|
| age            |          2 | Mann-Whitney U |     8.663e+07 | 0.01608    | True            |
| duration       |          2 | Mann-Whitney U |     3.079e+07 | 0          | True            |
| campaign       |          2 | Mann-Whitney U |     9.415e+07 | 3.419e-38  | True            |
| pdays          |          2 | Mann-Whitney U |     1.012e+08 | 0          | True            |
| previous       |          2 | Mann-Whitney U |     6.626e+07 | 0          | True            |
| emp.var.rate   |          2 | Mann-Whitney U |     1.215e+08 | 0          | True            |
| cons.price.idx |          2 | Mann-Whitney U |     1.035e+08 | 9.573e-136 | True            |
| cons.conf.idx  |          2 | Mann-Whitney U |     7.846e+07 | 5.902e-17  | True            |
| euribor3m      |          2 | Mann-Whitney U |     1.261e+08 | 0          | True            |
| nr.employed    |          2 | Mann-Whitney U |     1.27e+08  | 0          | True            |


## 6. Correlación entre variables continuas

**Pearson:**

| index          |        age |   duration |   campaign |    pdays |   previous |   emp.var.rate |   cons.price.idx |   cons.conf.idx |   euribor3m |   nr.employed |
|:---------------|-----------:|-----------:|-----------:|---------:|-----------:|---------------:|-----------------:|----------------:|------------:|--------------:|
| age            |  1         | -0.0008657 |   0.004594 | -0.03437 |    0.02436 |     -0.0003707 |        0.0008567 |        0.1294   |     0.01077 |      -0.01773 |
| duration       | -0.0008657 |  1         |  -0.0717   | -0.04758 |    0.02064 |     -0.02797   |        0.005312  |       -0.008173 |    -0.0329  |      -0.0447  |
| campaign       |  0.004594  | -0.0717    |   1        |  0.05258 |   -0.07914 |      0.1508    |        0.1278    |       -0.01373  |     0.1351  |       0.1441  |
| pdays          | -0.03437   | -0.04758   |   0.05258  |  1       |   -0.5875  |      0.271     |        0.07889   |       -0.09134  |     0.2969  |       0.3726  |
| previous       |  0.02436   |  0.02064   |  -0.07914  | -0.5875  |    1       |     -0.4205    |       -0.2031    |       -0.05094  |    -0.4545  |      -0.5013  |
| emp.var.rate   | -0.0003707 | -0.02797   |   0.1508   |  0.271   |   -0.4205  |      1         |        0.7753    |        0.196    |     0.9722  |       0.907   |
| cons.price.idx |  0.0008567 |  0.005312  |   0.1278   |  0.07889 |   -0.2031  |      0.7753    |        1         |        0.05899  |     0.6882  |       0.522   |
| cons.conf.idx  |  0.1294    | -0.008173  |  -0.01373  | -0.09134 |   -0.05094 |      0.196     |        0.05899   |        1        |     0.2777  |       0.1005  |
| euribor3m      |  0.01077   | -0.0329    |   0.1351   |  0.2969  |   -0.4545  |      0.9722    |        0.6882    |        0.2777   |     1       |       0.9452  |
| nr.employed    | -0.01773   | -0.0447    |   0.1441   |  0.3726  |   -0.5013  |      0.907     |        0.522     |        0.1005   |     0.9452  |       1       |

**Spearman:**

| index          |       age |   duration |   campaign |     pdays |   previous |   emp.var.rate |   cons.price.idx |   cons.conf.idx |   euribor3m |   nr.employed |
|:---------------|----------:|-----------:|-----------:|----------:|-----------:|---------------:|-----------------:|----------------:|------------:|--------------:|
| age            |  1        |  -0.002123 |   0.005715 | -0.001062 |   -0.01264 |         0.045  |         0.04479  |        0.1145   |     0.05439 |       0.04479 |
| duration       | -0.002123 |   1        |  -0.08095  | -0.08307  |    0.04241 |        -0.0692 |         0.002854 |       -0.008678 |    -0.07835 |      -0.09522 |
| campaign       |  0.005715 |  -0.08095  |   1        |  0.05551  |   -0.08742 |         0.1564 |         0.09649  |       -0.001554 |     0.1405  |       0.1443  |
| pdays          | -0.001062 |  -0.08307  |   0.05551  |  1        |   -0.5096  |         0.2277 |         0.05676  |       -0.07726  |     0.2785  |       0.2907  |
| previous       | -0.01264  |   0.04241  |  -0.08742  | -0.5096   |    1       |        -0.4353 |        -0.2827   |       -0.116    |    -0.4547  |      -0.4387  |
| emp.var.rate   |  0.045    |  -0.0692   |   0.1564   |  0.2277   |   -0.4353  |         1      |         0.6649   |        0.2247   |     0.9399  |       0.9447  |
| cons.price.idx |  0.04479  |   0.002854 |   0.09649  |  0.05676  |   -0.2827  |         0.6649 |         1        |        0.2456   |     0.491   |       0.4647  |
| cons.conf.idx  |  0.1145   |  -0.008678 |  -0.001554 | -0.07726  |   -0.116   |         0.2247 |         0.2456   |        1        |     0.2366  |       0.1327  |
| euribor3m      |  0.05439  |  -0.07835  |   0.1405   |  0.2785   |   -0.4547  |         0.9399 |         0.491    |        0.2366   |     1       |       0.9289  |
| nr.employed    |  0.04479  |  -0.09522  |   0.1443   |  0.2907   |   -0.4387  |         0.9447 |         0.4647   |        0.1327   |     0.9289  |       1       |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

| variable    | prueba                                               |    p_valor |   cramers_v | significativo   |
|:------------|:-----------------------------------------------------|-----------:|------------:|:----------------|
| job         | Chi-cuadrado                                         | 4.19e-199  |    0.1528   | True            |
| marital     | Chi-cuadrado                                         | 2.068e-26  |    0.05457  | True            |
| education   | Chi-cuadrado                                         | 3.305e-38  |    0.06847  | True            |
| default     | Chi-cuadrado (¡ojo: >20% de celdas con esperado <5!) | 5.162e-89  |    0.09935  | True            |
| housing     | Chi-cuadrado                                         | 0.05829    |    0.01175  | False           |
| loan        | Chi-cuadrado                                         | 0.5787     |    0.005154 | False           |
| contact     | Chi-cuadrado (Fisher como respaldo)                  | 1.526e-189 |    0.1447   | True            |
| month       | Chi-cuadrado                                         | 0          |    0.2744   | True            |
| day_of_week | Chi-cuadrado                                         | 2.958e-05  |    0.02519  | True            |
| poutcome    | Chi-cuadrado                                         | 0          |    0.3205   | True            |

## 8. Relevancia de variables frente a la clase (ranking)

| variable       |   anova_f_p |   kruskal_h_p |   info_mutua |
|:---------------|------------:|--------------:|-------------:|
| duration       |  0          |    0          |     0.07789  |
| pdays          |  0          |    0          |     0.04139  |
| previous       |  0          |    0          |     0.0173   |
| emp.var.rate   |  0          |    0          |     0.05593  |
| euribor3m      |  0          |    0          |     0.07489  |
| nr.employed    |  0          |    0          |     0.06442  |
| cons.price.idx |  9.319e-170 |    9.572e-136 |     0.06667  |
| campaign       |  2.008e-41  |    3.418e-38  |     0.007954 |
| cons.conf.idx  |  7.537e-29  |    5.902e-17  |     0.06884  |
| age            |  6.802e-10  |    0.01608    |     0.01158  |

## 9. Multicolinealidad (VIF y número de condición)

| variable       |    VIF |
|:---------------|-------:|
| euribor3m      | 64.35  |
| emp.var.rate   | 33.07  |
| nr.employed    | 31.68  |
| cons.price.idx |  6.338 |
| cons.conf.idx  |  2.65  |
| previous       |  1.797 |
| pdays          |  1.615 |
| campaign       |  1.038 |
| age            |  1.019 |
| duration       |  1.009 |

Índice de condición de la matriz estandarizada: 19.17

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable       |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:---------------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| age            |                        369 |                    469 |                 9.5   |                 69.5  |
| duration       |                        861 |                   2963 |              -223.5   |                644.5  |
| campaign       |                        869 |                   2406 |                -2     |                  6    |
| pdays          |                       1515 |                   1515 |               999     |                999    |
| previous       |                       1064 |                   5625 |                 0     |                  0    |
| emp.var.rate   |                          0 |                      0 |                -6.6   |                  6.2  |
| cons.price.idx |                          0 |                      0 |                91.7   |                 95.37 |
| cons.conf.idx  |                          0 |                    447 |               -52.15  |                -26.95 |
| euribor3m      |                          0 |                      0 |                -4.081 |                 10.39 |
| nr.employed    |                          0 |                      0 |              4906     |               5422    |

Mahalanobis multivariado: 2798 outlier(s) de 41188 filas evaluadas (umbral chi² = 29.6).

## 11. Balance de la variable objetivo

Clases: 2 (no: 36548, yes: 4640)

Prueba: Test binomial

p-valor: 0

¿Desbalanceado respecto a distribución uniforme? Sí

