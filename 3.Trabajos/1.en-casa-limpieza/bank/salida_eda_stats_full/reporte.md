# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']

Categóricas: ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome']

| variable   |     n |   faltantes |     media |   mediana |   desv_std |   asimetria |   curtosis |
|:-----------|------:|------------:|----------:|----------:|-----------:|------------:|-----------:|
| age        | 45211 |           0 |   40.94   |        39 |     10.62  |     0.6848  |     0.3194 |
| balance    | 45211 |           0 | 1362      |       448 |   3045     |     8.36    |   140.7    |
| day        | 45211 |           0 |   15.81   |        16 |      8.322 |     0.09308 |    -1.06   |
| duration   | 45211 |           0 |  258.2    |       180 |    257.5   |     3.144   |    18.15   |
| campaign   | 45211 |           0 |    2.764  |         2 |      3.098 |     4.898   |    39.25   |
| pdays      | 45211 |           0 |   40.2    |        -1 |    100.1   |     2.616   |     6.934  |
| previous   | 45211 |           0 |    0.5803 |         0 |      2.303 |    41.85    |  4506      |

## 2. Pruebas de normalidad (global y por clase)

|     n |   ks_lilliefors_p |   dagostino_p | veredicto   | variable   | grupo    |
|------:|------------------:|--------------:|:------------|:-----------|:---------|
| 45211 |        0          |    0          | no normal   | age        | (global) |
| 39922 |        1.961e-309 |    0          | no normal   | age        | no       |
|  5289 |        7.427e-65  |    2.958e-113 | no normal   | age        | yes      |
| 45211 |        0          |    0          | no normal   | balance    | (global) |
| 39922 |        0          |    0          | no normal   | balance    | no       |
|  5289 |        0          |    0          | no normal   | balance    | yes      |
| 45211 |        2.216e-286 |    0          | no normal   | day        | (global) |
| 39922 |        6.452e-265 |    0          | no normal   | day        | no       |
|  5289 |        8.921e-24  |    0          | no normal   | day        | yes      |
| 45211 |        0          |    0          | no normal   | duration   | (global) |
| 39922 |        0          |    0          | no normal   | duration   | no       |
|  5289 |        4.015e-62  |    0          | no normal   | duration   | yes      |
| 45211 |        0          |    0          | no normal   | campaign   | (global) |
| 39922 |        0          |    0          | no normal   | campaign   | no       |
|  5289 |        0          |    0          | no normal   | campaign   | yes      |
| 45211 |        0          |    0          | no normal   | pdays      | (global) |
| 39922 |        0          |    0          | no normal   | pdays      | no       |
|  5289 |        0          |    0          | no normal   | pdays      | yes      |
| 45211 |        0          |    0          | no normal   | previous   | (global) |
| 39922 |        0          |    0          | no normal   | previous   | no       |
|  5289 |        0          |    0          | no normal   | previous   | yes      |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable   |   levene_p |   fligner_p | veredicto   |
|:-----------|-----------:|------------:|:------------|
| age        | 2.421e-133 |  3.153e-108 | heterogénea |
| balance    | 5.02e-15   |  3.866e-97  | heterogénea |
| day        | 0.01776    |  1.042e-08  | heterogénea |
| duration   | 0          |  0          | heterogénea |
| campaign   | 8.22e-33   |  5.92e-31   | heterogénea |
| pdays      | 3.791e-108 |  6.666e-187 | heterogénea |
| previous   | 7.802e-88  |  9.019e-267 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable   |   n_clases | prueba         |   estadistico |    p_valor | significativo   |
|:-----------|-----------:|:---------------|--------------:|-----------:|:----------------|
| age        |          2 | Mann-Whitney U |     1.072e+08 | 0.06282    | False           |
| balance    |          2 | Mann-Whitney U |     8.656e+07 | 6.594e-101 | True            |
| day        |          2 | Mann-Whitney U |     1.112e+08 | 3.326e-10  | True            |
| duration   |          2 | Mann-Whitney U |     4.063e+07 | 0          | True            |
| campaign   |          2 | Mann-Whitney U |     1.208e+08 | 1.948e-71  | True            |
| pdays      |          2 | Mann-Whitney U |     8.589e+07 | 2.484e-235 | True            |
| previous   |          2 | Mann-Whitney U |     8.397e+07 | 3.492e-283 | True            |


## 6. Correlación entre variables continuas

**Pearson:**

| index    |       age |   balance |       day |   duration |   campaign |     pdays |   previous |
|:---------|----------:|----------:|----------:|-----------:|-----------:|----------:|-----------:|
| age      |  1        |  0.09778  | -0.00912  |  -0.004648 |    0.00476 | -0.02376  |   0.001288 |
| balance  |  0.09778  |  1        |  0.004503 |   0.02156  |   -0.01458 |  0.003435 |   0.01667  |
| day      | -0.00912  |  0.004503 |  1        |  -0.03021  |    0.1625  | -0.09304  |  -0.05171  |
| duration | -0.004648 |  0.02156  | -0.03021  |   1        |   -0.08457 | -0.001565 |   0.001203 |
| campaign |  0.00476  | -0.01458  |  0.1625   |  -0.08457  |    1       | -0.08863  |  -0.03286  |
| pdays    | -0.02376  |  0.003435 | -0.09304  |  -0.001565 |   -0.08863 |  1        |   0.4548   |
| previous |  0.001288 |  0.01667  | -0.05171  |   0.001203 |   -0.03286 |  0.4548   |   1        |

**Spearman:**

| index    |       age |   balance |       day |   duration |   campaign |    pdays |   previous |
|:---------|----------:|----------:|----------:|-----------:|-----------:|---------:|-----------:|
| age      |  1        |  0.09638  | -0.008948 |   -0.03326 |    0.03714 | -0.01747 |   -0.0119  |
| balance  |  0.09638  |  1        |  0.001329 |    0.04265 |   -0.03096 |  0.06968 |    0.07954 |
| day      | -0.008948 |  0.001329 |  1        |   -0.05814 |    0.1396  | -0.09223 |   -0.08778 |
| duration | -0.03326  |  0.04265  | -0.05814  |    1       |   -0.108   |  0.0287  |    0.03117 |
| campaign |  0.03714  | -0.03096  |  0.1396   |   -0.108   |    1       | -0.1123  |   -0.1084  |
| pdays    | -0.01747  |  0.06968  | -0.09223  |    0.0287  |   -0.1123  |  1       |    0.9856  |
| previous | -0.0119   |  0.07954  | -0.08778  |    0.03117 |   -0.1084  |  0.9856  |    1       |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

| variable   | prueba                              |    p_valor |   cramers_v | significativo   |
|:-----------|:------------------------------------|-----------:|------------:|:----------------|
| job        | Chi-cuadrado                        | 3.337e-172 |     0.136   | True            |
| marital    | Chi-cuadrado                        | 2.145e-43  |     0.06593 | True            |
| education  | Chi-cuadrado                        | 1.627e-51  |     0.0727  | True            |
| default    | Chi-cuadrado (Fisher como respaldo) | 2.454e-06  |     0.02216 | True            |
| housing    | Chi-cuadrado (Fisher como respaldo) | 2.919e-192 |     0.1391  | True            |
| loan       | Chi-cuadrado (Fisher como respaldo) | 1.665e-47  |     0.06809 | True            |
| contact    | Chi-cuadrado                        | 1.252e-225 |     0.1514  | True            |
| month      | Chi-cuadrado                        | 0          |     0.2602  | True            |
| poutcome   | Chi-cuadrado                        | 0          |     0.3117  | True            |

## 8. Relevancia de variables frente a la clase (ranking)

| variable   |   anova_f_p |   kruskal_h_p |   info_mutua |
|:-----------|------------:|--------------:|-------------:|
| duration   |  0          |    0          |     0.07114  |
| previous   |  7.802e-88  |    3.492e-283 |     0.01133  |
| pdays      |  3.791e-108 |    2.484e-235 |     0.02857  |
| balance    |  2.521e-29  |    6.594e-101 |     0.02292  |
| campaign   |  1.012e-54  |    1.948e-71  |     0.005593 |
| day        |  1.654e-09  |    3.326e-10  |     0.006551 |
| age        |  8.826e-08  |    0.06282    |     0.01183  |

## 9. Multicolinealidad (VIF y número de condición)

| variable   |   VIF |
|:-----------|------:|
| pdays      | 1.276 |
| previous   | 1.262 |
| campaign   | 1.04  |
| day        | 1.034 |
| balance    | 1.011 |
| age        | 1.011 |
| duration   | 1.008 |

Índice de condición de la matriz estandarizada: 1.67

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable   |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:-----------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| age        |                        381 |                    487 |                  10.5 |                  70.5 |
| balance    |                        745 |                   4729 |               -1962   |                3462   |
| day        |                          0 |                      0 |                 -11.5 |                  40.5 |
| duration   |                        963 |                   3235 |                -221   |                 643   |
| campaign   |                        840 |                   3064 |                  -2   |                   6   |
| pdays      |                       1723 |                   8257 |                  -1   |                  -1   |
| previous   |                        582 |                   8257 |                   0   |                   0   |

Mahalanobis multivariado: 1518 outlier(s) de 45211 filas evaluadas (umbral chi² = 24.3).

## 11. Balance de la variable objetivo

Clases: 2 (no: 39922, yes: 5289)

Prueba: Test binomial

p-valor: 0

¿Desbalanceado respecto a distribución uniforme? Sí

