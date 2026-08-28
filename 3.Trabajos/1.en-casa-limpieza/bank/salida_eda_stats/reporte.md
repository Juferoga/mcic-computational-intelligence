# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']

Categóricas: ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']

| variable   |    n |   faltantes |     media |   mediana |   desv_std |   asimetria |   curtosis |
|:-----------|-----:|------------:|----------:|----------:|-----------:|------------:|-----------:|
| age        | 4521 |           0 |   41.17   |        39 |     10.58  |      0.6993 |     0.3471 |
| balance    | 4521 |           0 | 1423      |       444 |   3010     |      6.594  |    88.29   |
| day        | 4521 |           0 |   15.92   |        16 |      8.248 |      0.0946 |    -1.04   |
| duration   | 4521 |           0 |  264      |       185 |    259.9   |      2.771  |    12.51   |
| campaign   | 4521 |           0 |    2.794  |         2 |      3.11  |      4.742  |    37.13   |
| pdays      | 4521 |           0 |   39.77   |        -1 |    100.1   |      2.716  |     7.947  |
| previous   | 4521 |           0 |    0.5426 |         0 |      1.694 |      5.873  |    51.94   |

## 2. Pruebas de normalidad (global y por clase)

|    n |   shapiro_p |   dagostino_p | veredicto   | variable   | grupo    |
|-----:|------------:|--------------:|:------------|:-----------|:---------|
| 4521 |   9.428e-34 |    1.987e-70  | no normal   | age        | (global) |
| 4000 |   6.981e-31 |    4.099e-48  | no normal   | age        | no       |
|  521 |   4.444e-13 |    4.927e-12  | no normal   | age        | yes      |
| 4521 |   1.124e-77 |    0          | no normal   | balance    | (global) |
| 4000 |   2.181e-75 |    0          | no normal   | balance    | no       |
|  521 |   3.078e-31 |    7.151e-109 | no normal   | balance    | yes      |
| 4521 |   2.459e-33 |    3.086e-278 | no normal   | day        | (global) |
| 4000 |   4.948e-32 |    6.777e-260 | no normal   | day        | no       |
|  521 |   1.371e-09 |    5.331e-20  | no normal   | day        | yes      |
| 4521 |   6.241e-64 |    0          | no normal   | duration   | (global) |
| 4000 |   1.286e-60 |    0          | no normal   | duration   | no       |
|  521 |   3.993e-20 |    3.161e-38  | no normal   | duration   | yes      |
| 4521 |   5.175e-75 |    0          | no normal   | campaign   | (global) |
| 4000 |   4.318e-72 |    0          | no normal   | campaign   | no       |
|  521 |   6.93e-33  |    4.03e-110  | no normal   | campaign   | yes      |
| 4521 |   5.779e-79 |    0          | no normal   | pdays      | (global) |
| 4000 |   3.279e-77 |    0          | no normal   | pdays      | no       |
|  521 |   1.279e-31 |    3.652e-58  | no normal   | pdays      | yes      |
| 4521 |   4.543e-83 |    0          | no normal   | previous   | (global) |
| 4000 |   2.103e-81 |    0          | no normal   | previous   | no       |
|  521 |   6.7e-33   |    3.262e-71  | no normal   | previous   | yes      |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable   |   levene_p |   fligner_p | veredicto   |
|:-----------|-----------:|------------:|:------------|
| age        |  1.261e-12 |   8.094e-11 | heterogénea |
| balance    |  0.7452    |   1.1e-07   | homogénea   |
| day        |  0.689     |   0.3784    | homogénea   |
| duration   |  2.981e-67 |   4.488e-84 | heterogénea |
| campaign   |  0.001257  |   0.01014   | heterogénea |
| pdays      |  2.287e-12 |   8.494e-20 | heterogénea |
| previous   |  3.478e-15 |   3.191e-27 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable   |   n_clases | prueba         |   estadistico |    p_valor | significativo   |
|:-----------|-----------:|:---------------|--------------:|-----------:|:----------------|
| age        |          2 | Mann-Whitney U |     1.011e+06 | 0.274      | False           |
| balance    |          2 | Mann-Whitney U |     8.932e+05 | 1.096e-07  | True            |
| day        |          2 | Mann-Whitney U |     1.064e+06 | 0.4272     | False           |
| duration   |          2 | Mann-Whitney U |     3.855e+05 | 2.329e-121 | True            |
| campaign   |          2 | Mann-Whitney U |     1.159e+06 | 1.4e-05    | True            |
| pdays      |          2 | Mann-Whitney U |     8.523e+05 | 5.717e-24  | True            |
| previous   |          2 | Mann-Whitney U |     8.332e+05 | 1.055e-28  | True            |


## 6. Correlación entre variables continuas

**Pearson:**

| index    |       age |   balance |       day |   duration |   campaign |     pdays |   previous |
|:---------|----------:|----------:|----------:|-----------:|-----------:|----------:|-----------:|
| age      |  1        |  0.08382  | -0.01785  |  -0.002367 |  -0.005148 | -0.008894 |  -0.003511 |
| balance  |  0.08382  |  1        | -0.008677 |  -0.01595  |  -0.009976 |  0.009437 |   0.0262   |
| day      | -0.01785  | -0.008677 |  1        |  -0.02463  |   0.1607   | -0.09435  |  -0.05911  |
| duration | -0.002367 | -0.01595  | -0.02463  |   1        |  -0.06838  |  0.01038  |   0.01808  |
| campaign | -0.005148 | -0.009976 |  0.1607   |  -0.06838  |   1        | -0.09314  |  -0.06783  |
| pdays    | -0.008894 |  0.009437 | -0.09435  |   0.01038  |  -0.09314  |  1        |   0.5776   |
| previous | -0.003511 |  0.0262   | -0.05911  |   0.01808  |  -0.06783  |  0.5776   |   1        |

**Spearman:**

| index    |        age |   balance |      day |   duration |   campaign |     pdays |   previous |
|:---------|-----------:|----------:|---------:|-----------:|-----------:|----------:|-----------:|
| age      |  1         |   0.076   | -0.02382 |   -0.03673 |    0.02508 | -0.001197 |  0.0006265 |
| balance  |  0.076     |   1       | -0.01276 |    0.05418 |   -0.03272 |  0.06221  |  0.06847   |
| day      | -0.02382   |  -0.01276 |  1       |   -0.05086 |    0.1441  | -0.08411  | -0.07815   |
| duration | -0.03673   |   0.05418 | -0.05086 |    1       |   -0.09015 |  0.0364   |  0.0403    |
| campaign |  0.02508   |  -0.03272 |  0.1441  |   -0.09015 |    1       | -0.1383   | -0.1373    |
| pdays    | -0.001197  |   0.06221 | -0.08411 |    0.0364  |   -0.1383  |  1        |  0.9863    |
| previous |  0.0006265 |   0.06847 | -0.07815 |    0.0403  |   -0.1373  |  0.9863   |  1         |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

| variable   | prueba                              |   p_valor |   cramers_v | significativo   |
|:-----------|:------------------------------------|----------:|------------:|:----------------|
| job        | Chi-cuadrado                        | 1.901e-10 |     0.1235  | True            |
| marital    | Chi-cuadrado                        | 7.374e-05 |     0.06488 | True            |
| education  | Chi-cuadrado                        | 0.001625  |     0.05805 | True            |
| default    | Chi-cuadrado (Fisher como respaldo) | 1         |     0       | False           |
| housing    | Chi-cuadrado (Fisher como respaldo) | 2.715e-12 |     0.104   | True            |
| loan       | Chi-cuadrado (Fisher como respaldo) | 2.915e-06 |     0.06955 | True            |
| contact    | Chi-cuadrado                        | 8.304e-20 |     0.1394  | True            |
| month      | Chi-cuadrado                        | 2.195e-47 |     0.2354  | True            |
| poutcome   | Chi-cuadrado                        | 1.54e-83  |     0.2925  | True            |

## 8. Relevancia de variables frente a la clase (ranking)

| variable   |   anova_f_p |   kruskal_h_p |   info_mutua |
|:-----------|------------:|--------------:|-------------:|
| duration   |   2.15e-174 |    2.328e-121 |     0.07068  |
| previous   |   3.478e-15 |    1.055e-28  |     0.01664  |
| pdays      |   2.287e-12 |    5.716e-24  |     0.03183  |
| balance    |   0.2287    |    1.096e-07  |     0.009563 |
| campaign   |   3.886e-05 |    1.4e-05    |     0.002028 |
| age        |   0.002425  |    0.274      |     0.007117 |
| day        |   0.4497    |    0.4272     |     0.00647  |

## 9. Multicolinealidad (VIF y número de condición)

| variable   |   VIF |
|:-----------|------:|
| pdays      | 1.514 |
| previous   | 1.502 |
| campaign   | 1.038 |
| day        | 1.034 |
| balance    | 1.008 |
| age        | 1.008 |
| duration   | 1.005 |

Índice de condición de la matriz estandarizada: 1.97

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable   |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:-----------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| age        |                         44 |                     38 |                   9   |                  73   |
| balance    |                         88 |                    506 |               -2048   |                3596   |
| day        |                          0 |                      0 |                  -9   |                  39   |
| duration   |                         88 |                    330 |                -233.5 |                 666.5 |
| campaign   |                         87 |                    318 |                  -2   |                   6   |
| pdays      |                        171 |                    816 |                  -1   |                  -1   |
| previous   |                         99 |                    816 |                   0   |                   0   |

Mahalanobis multivariado: 180 outlier(s) de 4521 filas evaluadas (umbral chi² = 24.3).

## 11. Balance de la variable objetivo

Clases: 2 (no: 4000, yes: 521)

Prueba: Test binomial

p-valor: 0

¿Desbalanceado respecto a distribución uniforme? Sí

