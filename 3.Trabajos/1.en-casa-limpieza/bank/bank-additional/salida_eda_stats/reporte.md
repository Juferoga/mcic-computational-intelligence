# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['age', 'duration', 'campaign', 'pdays', 'previous', 'emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed']

Categóricas: ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'day_of_week', 'poutcome']

| variable       |    n |   faltantes |      media |   mediana |   desv_std |   asimetria |   curtosis |
|:---------------|-----:|------------:|-----------:|----------:|-----------:|------------:|-----------:|
| age            | 4119 |           0 |   40.11    |    38     |    10.31   |      0.7154 |    0.4361  |
| duration       | 4119 |           0 |  256.8     |   181     |   254.7    |      3.294  |   20.74    |
| campaign       | 4119 |           0 |    2.537   |     2     |     2.568  |      4.002  |   25.25    |
| pdays          | 4119 |           0 |  960.4     |   999     |   191.9    |     -4.773  |   20.79    |
| previous       | 4119 |           0 |    0.1903  |     0     |     0.5418 |      4.022  |   22.09    |
| emp.var.rate   | 4119 |           0 |    0.08497 |     1.1   |     1.563  |     -0.7274 |   -1.042   |
| cons.price.idx | 4119 |           0 |   93.58    |    93.75  |     0.5793 |     -0.2166 |   -0.8238  |
| cons.conf.idx  | 4119 |           0 |  -40.5     |   -41.8   |     4.595  |      0.2872 |   -0.3154  |
| euribor3m      | 4119 |           0 |    3.621   |     4.857 |     1.734  |     -0.7148 |   -1.396   |
| nr.employed    | 4119 |           0 | 5166       |  5191     |    73.67   |     -1.075  |    0.06019 |

## 2. Pruebas de normalidad (global y por clase)

|    n |   shapiro_p |   dagostino_p | veredicto   | variable       | grupo    |
|-----:|------------:|--------------:|:------------|:---------------|:---------|
| 4119 |   5.644e-33 |    3.454e-68  | no normal   | age            | (global) |
| 3668 |   2.851e-29 |    1.628e-40  | no normal   | age            | no       |
|  451 |   1.38e-13  |    3.292e-12  | no normal   | age            | yes      |
| 4119 |   1.032e-63 |    0          | no normal   | duration       | (global) |
| 3668 |   3.561e-59 |    0          | no normal   | duration       | no       |
|  451 |   1.208e-20 |    6.083e-50  | no normal   | duration       | yes      |
| 4119 |   4.296e-71 |    0          | no normal   | campaign       | (global) |
| 3668 |   2.693e-68 |    0          | no normal   | campaign       | no       |
|  451 |   3.613e-27 |    9.059e-57  | no normal   | campaign       | yes      |
| 4119 |   5.96e-86  |    0          | no normal   | pdays          | (global) |
| 3668 |   2.953e-85 |    0          | no normal   | pdays          | no       |
|  451 |   2.384e-33 |    2.664e-19  | no normal   | pdays          | yes      |
| 4119 |   1.307e-79 |    0          | no normal   | previous       | (global) |
| 3668 |   7.615e-78 |    0          | no normal   | previous       | no       |
|  451 |   8.766e-30 |    2.839e-46  | no normal   | previous       | yes      |
| 4119 |   1.438e-60 |    0          | no normal   | emp.var.rate   | (global) |
| 3668 |   4.18e-60  |    7.306e-133 | no normal   | emp.var.rate   | no       |
|  451 |   1.117e-20 |    7.113e-33  | no normal   | emp.var.rate   | yes      |
| 4119 |   6.963e-39 |    9.235e-92  | no normal   | cons.price.idx | (global) |
| 3668 |   1.7e-38   |    3.044e-79  | no normal   | cons.price.idx | no       |
|  451 |   1.485e-11 |    7.562e-35  | no normal   | cons.price.idx | yes      |
| 4119 |   3.713e-41 |    9.085e-18  | no normal   | cons.conf.idx  | (global) |
| 3668 |   1.144e-42 |    5.552e-19  | no normal   | cons.conf.idx  | no       |
|  451 |   1.065e-07 |    0.0001293  | no normal   | cons.conf.idx  | yes      |
| 4119 |   4.487e-66 |    0          | no normal   | euribor3m      | (global) |
| 3668 |   3.644e-65 |    1.23e-285  | no normal   | euribor3m      | no       |
|  451 |   9.241e-28 |    4.821e-61  | no normal   | euribor3m      | yes      |
| 4119 |   5.148e-59 |    2.612e-119 | no normal   | nr.employed    | (global) |
| 3668 |   1.253e-58 |    4.219e-140 | no normal   | nr.employed    | no       |
|  451 |   4.206e-18 |    9.788e-113 | no normal   | nr.employed    | yes      |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable       |   levene_p |   fligner_p | veredicto   |
|:---------------|-----------:|------------:|:------------|
| age            | 4.217e-15  |   1.475e-12 | heterogénea |
| duration       | 1.974e-76  |   9.591e-93 | heterogénea |
| campaign       | 7.282e-06  |   2.184e-05 | heterogénea |
| pdays          | 1.443e-106 |   3.247e-98 | heterogénea |
| previous       | 1.726e-62  |   3.269e-54 | heterogénea |
| emp.var.rate   | 0.04449    |   0.006218  | heterogénea |
| cons.price.idx | 7.901e-09  |   2.661e-08 | heterogénea |
| cons.conf.idx  | 8.28e-17   |   3.119e-32 | heterogénea |
| euribor3m      | 0.05772    |   6.47e-11  | homogénea   |
| nr.employed    | 7.483e-29  |   4.438e-25 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable       |   n_clases | prueba         |   estadistico |    p_valor | significativo   |
|:---------------|-----------:|:---------------|--------------:|-----------:|:----------------|
| age            |          2 | Mann-Whitney U |     7.922e+05 | 0.142      | False           |
| duration       |          2 | Mann-Whitney U |     2.951e+05 | 2.078e-110 | True            |
| campaign       |          2 | Mann-Whitney U |     9.157e+05 | 9.191e-05  | True            |
| pdays          |          2 | Mann-Whitney U |     9.972e+05 | 6.906e-101 | True            |
| previous       |          2 | Mann-Whitney U |     6.254e+05 | 1.021e-43  | True            |
| emp.var.rate   |          2 | Mann-Whitney U |     1.168e+06 | 2.446e-50  | True            |
| cons.price.idx |          2 | Mann-Whitney U |     9.564e+05 | 4.42e-08   | True            |
| cons.conf.idx  |          2 | Mann-Whitney U |     7.562e+05 | 0.002666   | True            |
| euribor3m      |          2 | Mann-Whitney U |     1.234e+06 | 2.385e-65  | True            |
| nr.employed    |          2 | Mann-Whitney U |     1.233e+06 | 2.221e-70  | True            |


## 6. Correlación entre variables continuas

**Pearson:**

| index          |       age |   duration |   campaign |    pdays |   previous |   emp.var.rate |   cons.price.idx |   cons.conf.idx |   euribor3m |   nr.employed |
|:---------------|----------:|-----------:|-----------:|---------:|-----------:|---------------:|-----------------:|----------------:|------------:|--------------:|
| age            |  1        |    0.0413  |  -0.01417  | -0.04342 |    0.05093 |       -0.01919 |        -0.000482 |        0.09814  |    -0.01503 |      -0.04194 |
| duration       |  0.0413   |    1       |  -0.08535  | -0.047   |    0.02572 |       -0.02885 |         0.01667  |       -0.03474  |    -0.03233 |      -0.04422 |
| campaign       | -0.01417  |   -0.08535 |   1        |  0.05874 |   -0.09149 |        0.1761  |         0.145    |        0.007882 |     0.1594  |       0.161   |
| pdays          | -0.04342  |   -0.047   |   0.05874  |  1       |   -0.5879  |        0.2707  |         0.05847  |       -0.09209  |     0.3015  |       0.382   |
| previous       |  0.05093  |    0.02572 |  -0.09149  | -0.5879  |    1       |       -0.4152  |        -0.1649   |       -0.05142  |    -0.4589  |      -0.5149  |
| emp.var.rate   | -0.01919  |   -0.02885 |   0.1761   |  0.2707  |   -0.4152  |        1       |         0.7552   |        0.195    |     0.9703  |       0.8972  |
| cons.price.idx | -0.000482 |    0.01667 |   0.145    |  0.05847 |   -0.1649  |        0.7552  |         1        |        0.04583  |     0.6572  |       0.4726  |
| cons.conf.idx  |  0.09814  |   -0.03474 |   0.007882 | -0.09209 |   -0.05142 |        0.195   |         0.04583  |        1        |     0.2766  |       0.1071  |
| euribor3m      | -0.01503  |   -0.03233 |   0.1594   |  0.3015  |   -0.4589  |        0.9703  |         0.6572   |        0.2766   |     1       |       0.9426  |
| nr.employed    | -0.04194  |   -0.04422 |   0.161    |  0.382   |   -0.5149  |        0.8972  |         0.4726   |        0.1071   |     0.9426  |       1       |

**Spearman:**

| index          |       age |   duration |   campaign |    pdays |   previous |   emp.var.rate |   cons.price.idx |   cons.conf.idx |   euribor3m |   nr.employed |
|:---------------|----------:|-----------:|-----------:|---------:|-----------:|---------------:|-----------------:|----------------:|------------:|--------------:|
| age            |  1        |    0.02825 |  -0.008091 | -0.0142  |   0.007179 |        0.01307 |          0.02698 |         0.08646 |     0.02695 |      0.009961 |
| duration       |  0.02825  |    1       |  -0.09831  | -0.08031 |   0.05692  |       -0.06894 |          0.01085 |        -0.02916 |    -0.08456 |     -0.09535  |
| campaign       | -0.008091 |   -0.09831 |   1        |  0.05996 |  -0.09775  |        0.1733  |          0.1216  |         0.01435 |     0.1579  |      0.154    |
| pdays          | -0.0142   |   -0.08031 |   0.05996  |  1       |  -0.5074   |        0.2277  |          0.03549 |        -0.08351 |     0.2861  |      0.2963   |
| previous       |  0.007179 |    0.05692 |  -0.09775  | -0.5074  |   1        |       -0.445   |         -0.2644  |        -0.1151  |    -0.4671  |     -0.4524   |
| emp.var.rate   |  0.01307  |   -0.06894 |   0.1733   |  0.2277  |  -0.445    |        1       |          0.65    |         0.2285  |     0.9387  |      0.9403   |
| cons.price.idx |  0.02698  |    0.01085 |   0.1216   |  0.03549 |  -0.2644   |        0.65    |          1       |         0.2351  |     0.4663  |      0.4301   |
| cons.conf.idx  |  0.08646  |   -0.02916 |   0.01435  | -0.08351 |  -0.1151   |        0.2285  |          0.2351  |         1       |     0.2443  |      0.1345   |
| euribor3m      |  0.02695  |   -0.08456 |   0.1579   |  0.2861  |  -0.4671   |        0.9387  |          0.4663  |         0.2443  |     1       |      0.9276   |
| nr.employed    |  0.009961 |   -0.09535 |   0.154    |  0.2963  |  -0.4524   |        0.9403  |          0.4301  |         0.1345  |     0.9276  |      1        |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

| variable    | prueba                                               |   p_valor |   cramers_v | significativo   |
|:------------|:-----------------------------------------------------|----------:|------------:|:----------------|
| job         | Chi-cuadrado                                         | 1.233e-10 |     0.1303  | True            |
| marital     | Chi-cuadrado                                         | 0.01629   |     0.04997 | True            |
| education   | Chi-cuadrado                                         | 0.002262  |     0.07357 | True            |
| default     | Chi-cuadrado (¡ojo: >20% de celdas con esperado <5!) | 5.6e-06   |     0.07663 | True            |
| housing     | Chi-cuadrado                                         | 0.7307    |     0.01234 | False           |
| loan        | Chi-cuadrado                                         | 0.5684    |     0.01656 | False           |
| contact     | Chi-cuadrado (Fisher como respaldo)                  | 1.848e-18 |     0.1366  | True            |
| month       | Chi-cuadrado                                         | 2.895e-59 |     0.2698  | True            |
| day_of_week | Chi-cuadrado                                         | 0.9723    |     0.01115 | False           |
| poutcome    | Chi-cuadrado                                         | 2.039e-99 |     0.3322  | True            |

## 8. Relevancia de variables frente a la clase (ranking)

| variable       |   anova_f_p |   kruskal_h_p |   info_mutua |
|:---------------|------------:|--------------:|-------------:|
| duration       |  1.903e-174 |    2.077e-110 |     0.07412  |
| pdays          |  1.443e-106 |    6.896e-101 |     0.03738  |
| nr.employed    |  1.842e-118 |    2.221e-70  |     0.06226  |
| euribor3m      |  1.408e-85  |    2.384e-65  |     0.07284  |
| emp.var.rate   |  7.823e-77  |    2.445e-50  |     0.0494   |
| previous       |  1.726e-62  |    1.021e-43  |     0.0229   |
| cons.price.idx |  2.55e-10   |    4.419e-08  |     0.06486  |
| campaign       |  1.013e-06  |    9.19e-05   |     0.007239 |
| cons.conf.idx  |  0.0004786  |    0.002666   |     0.06638  |
| age            |  0.0001057  |    0.142      |     0.00558  |

## 9. Multicolinealidad (VIF y número de condición)

| variable       |    VIF |
|:---------------|-------:|
| euribor3m      | 62.91  |
| emp.var.rate   | 31.95  |
| nr.employed    | 31.14  |
| cons.price.idx |  6.33  |
| cons.conf.idx  |  2.543 |
| previous       |  1.823 |
| pdays          |  1.616 |
| campaign       |  1.048 |
| duration       |  1.016 |
| age            |  1.016 |

Índice de condición de la matriz estandarizada: 18.90

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable       |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:---------------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| age            |                         32 |                     39 |                 9.5   |                 69.5  |
| duration       |                         87 |                    291 |              -218     |                638    |
| campaign       |                         87 |                    235 |                -2     |                  6    |
| pdays          |                        160 |                    160 |               999     |                999    |
| previous       |                        121 |                    596 |                 0     |                  0    |
| emp.var.rate   |                          0 |                      0 |                -6.6   |                  6.2  |
| cons.price.idx |                          0 |                      0 |                91.7   |                 95.37 |
| cons.conf.idx  |                          0 |                     43 |               -52.15  |                -26.95 |
| euribor3m      |                          0 |                      0 |                -4.107 |                 10.4  |
| nr.employed    |                          0 |                      0 |              4906     |               5422    |

Mahalanobis multivariado: 290 outlier(s) de 4119 filas evaluadas (umbral chi² = 29.6).

## 11. Balance de la variable objetivo

Clases: 2 (no: 3668, yes: 451)

Prueba: Test binomial

p-valor: 0

¿Desbalanceado respecto a distribución uniforme? Sí

