# Reporte de revisión estadística de variables

## 0-1. Tipificación y estadística descriptiva

Continuas: ['mcg', 'gvh', 'aac', 'alm1', 'alm2']

Categóricas: ['lip', 'chg']

| variable   |   n |   faltantes |   media |   mediana |   desv_std |   asimetria |   curtosis |
|:-----------|----:|------------:|--------:|----------:|-----------:|------------:|-----------:|
| mcg        | 336 |           0 |  0.5001 |     0.5   |     0.1946 |    -0.1652  |    -0.8643 |
| gvh        | 336 |           0 |  0.5    |     0.47  |     0.1482 |     0.7717  |     0.2378 |
| aac        | 336 |           0 |  0.5    |     0.495 |     0.1224 |     0.06259 |     1.298  |
| alm1       | 336 |           0 |  0.5002 |     0.455 |     0.2158 |     0.2614  |    -1.047  |
| alm2       | 336 |           0 |  0.4997 |     0.43  |     0.2094 |     0.4124  |    -0.9421 |

## 2. Pruebas de normalidad (global y por clase)

|   n |   shapiro_p |   dagostino_p | veredicto      | variable   | grupo    |
|----:|------------:|--------------:|:---------------|:-----------|:---------|
| 336 |   8.231e-06 |     2.274e-08 | no normal      | mcg        | (global) |
| 143 |   0.2757    |     0.8231    | normal         | mcg        | cp       |
|  77 |   0.3388    |     0.4356    | normal         | mcg        | im       |
|   2 | nan         |   nan         | n insuficiente | mcg        | imL      |
|   2 | nan         |   nan         | n insuficiente | mcg        | imS      |
|  35 |   0.07399   |     0.2691    | normal         | mcg        | imU      |
|  20 |   0.8161    |     0.7132    | normal         | mcg        | om       |
|   5 |   0.2636    |   nan         | normal         | mcg        | omL      |
|  52 |   4.011e-08 |     2.35e-10  | no normal      | mcg        | pp       |
| 336 |   3.863e-09 |     5.13e-07  | no normal      | gvh        | (global) |
| 143 |   0.1526    |     0.1042    | normal         | gvh        | cp       |
|  77 |   0.07407   |     0.133     | normal         | gvh        | im       |
|   2 | nan         |   nan         | n insuficiente | gvh        | imL      |
|   2 | nan         |   nan         | n insuficiente | gvh        | imS      |
|  35 |   0.8881    |     0.4405    | normal         | gvh        | imU      |
|  20 |   0.5871    |     0.5606    | normal         | gvh        | om       |
|   5 |   0.4367    |   nan         | normal         | gvh        | omL      |
|  52 |   0.1881    |     0.5513    | normal         | gvh        | pp       |
| 336 |   0.0002423 |     0.002894  | no normal      | aac        | (global) |
| 143 |   0.3087    |     0.1487    | normal         | aac        | cp       |
|  77 |   3.83e-05  |     1.729e-08 | no normal      | aac        | im       |
|   2 | nan         |   nan         | n insuficiente | aac        | imL      |
|   2 | nan         |   nan         | n insuficiente | aac        | imS      |
|  35 |   3.142e-05 |     1.01e-08  | no normal      | aac        | imU      |
|  20 |   0.4059    |     0.2107    | normal         | aac        | om       |
|   5 |   0.6606    |   nan         | normal         | aac        | omL      |
|  52 |   0.5054    |     0.1       | normal         | aac        | pp       |
| 336 |   1.431e-08 |     6.379e-19 | no normal      | alm1       | (global) |
| 143 |   0.3499    |     0.7666    | normal         | alm1       | cp       |
|  77 |   0.06144   |     0.01114   | normal         | alm1       | im       |
|   2 | nan         |   nan         | n insuficiente | alm1       | imL      |
|   2 | nan         |   nan         | n insuficiente | alm1       | imS      |
|  35 |   0.2091    |     0.06184   | normal         | alm1       | imU      |
|  20 |   0.1145    |     0.06525   | normal         | alm1       | om       |
|   5 |   0.754     |   nan         | normal         | alm1       | omL      |
|  52 |   0.001936  |     0.0001126 | no normal      | alm1       | pp       |
| 336 |   3.656e-11 |     3.419e-13 | no normal      | alm2       | (global) |
| 143 |   0.009613  |     0.002058  | no normal      | alm2       | cp       |
|  77 |   3.436e-08 |     5.058e-08 | no normal      | alm2       | im       |
|   2 | nan         |   nan         | n insuficiente | alm2       | imL      |
|   2 | nan         |   nan         | n insuficiente | alm2       | imS      |
|  35 |   1.555e-05 |     6.097e-09 | no normal      | alm2       | imU      |
|  20 |   0.3253    |     0.1205    | normal         | alm2       | om       |
|   5 |   0.5199    |   nan         | normal         | alm2       | omL      |
|  52 |   0.001984  |     4.051e-05 | no normal      | alm2       | pp       |

## 3. Homogeneidad de varianzas (Levene / Fligner-Killeen)

| variable   |   levene_p |   fligner_p | veredicto   |
|:-----------|-----------:|------------:|:------------|
| mcg        |  5.235e-10 |   4.174e-10 | heterogénea |
| gvh        |  0.003214  |   0.004325  | heterogénea |
| aac        |  0.7198    |   0.7036    | homogénea   |
| alm1       |  0.07224   |   0.03324   | homogénea   |
| alm2       |  0.0005868 |   0.0005654 | heterogénea |

## 4-5. Comparación de variables continuas entre clases

| variable   |   n_clases | prueba         |   estadistico |   p_valor | significativo   |
|:-----------|-----------:|:---------------|--------------:|----------:|:----------------|
| mcg        |          8 | Kruskal-Wallis |         184.4 | 2.305e-36 | True            |
| gvh        |          8 | Kruskal-Wallis |         164.3 | 4.037e-32 | True            |
| aac        |          8 | Kruskal-Wallis |         115.9 | 5.449e-22 | True            |
| alm1       |          8 | Kruskal-Wallis |         257.1 | 8.739e-52 | True            |
| alm2       |          8 | Kruskal-Wallis |         184.6 | 2.121e-36 | True            |

**Post-hoc para `mcg`** (Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles.):

- cp vs im: p=1.225e-06, p_ajustado(Bonferroni)=3.431e-05
- cp vs imS: p=0.01881, p_ajustado(Bonferroni)=0.5266
- cp vs imL: p=0.01564, p_ajustado(Bonferroni)=0.4379
- cp vs imU: p=1.148e-18, p_ajustado(Bonferroni)=3.216e-17
- cp vs om: p=2.832e-12, p_ajustado(Bonferroni)=7.929e-11
- cp vs omL: p=0.0001599, p_ajustado(Bonferroni)=0.004477
- cp vs pp: p=1.706e-22, p_ajustado(Bonferroni)=4.778e-21
- im vs imS: p=0.07015, p_ajustado(Bonferroni)=1
- im vs imL: p=0.04742, p_ajustado(Bonferroni)=1
- im vs imU: p=4.607e-10, p_ajustado(Bonferroni)=1.29e-08
- im vs om: p=6.638e-06, p_ajustado(Bonferroni)=0.0001859
- im vs omL: p=0.005911, p_ajustado(Bonferroni)=0.1655
- im vs pp: p=1.078e-08, p_ajustado(Bonferroni)=3.019e-07
- imS vs imL: p=1, p_ajustado(Bonferroni)=1
- imS vs imU: p=0.8665, p_ajustado(Bonferroni)=1
- imS vs om: p=0.6066, p_ajustado(Bonferroni)=1
- imS vs omL: p=1, p_ajustado(Bonferroni)=1
- imS vs pp: p=0.5813, p_ajustado(Bonferroni)=1
- imL vs imU: p=0.7622, p_ajustado(Bonferroni)=1
- imL vs om: p=0.2527, p_ajustado(Bonferroni)=1
- imL vs omL: p=0.5714, p_ajustado(Bonferroni)=1
- imL vs pp: p=0.09362, p_ajustado(Bonferroni)=1
- imU vs om: p=0.02927, p_ajustado(Bonferroni)=0.8196
- imU vs omL: p=0.4248, p_ajustado(Bonferroni)=1
- imU vs pp: p=0.001067, p_ajustado(Bonferroni)=0.02989
- om vs omL: p=0.5177, p_ajustado(Bonferroni)=1
- om vs pp: p=0.541, p_ajustado(Bonferroni)=1
- omL vs pp: p=0.2133, p_ajustado(Bonferroni)=1

**Post-hoc para `gvh`** (Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles.):

- cp vs im: p=6.144e-10, p_ajustado(Bonferroni)=1.72e-08
- cp vs imS: p=0.08206, p_ajustado(Bonferroni)=1
- cp vs imL: p=0.3916, p_ajustado(Bonferroni)=1
- cp vs imU: p=0.006154, p_ajustado(Bonferroni)=0.1723
- cp vs om: p=4.496e-12, p_ajustado(Bonferroni)=1.259e-10
- cp vs omL: p=0.008441, p_ajustado(Bonferroni)=0.2363
- cp vs pp: p=6.126e-23, p_ajustado(Bonferroni)=1.715e-21
- im vs imS: p=0.6618, p_ajustado(Bonferroni)=1
- im vs imL: p=0.7547, p_ajustado(Bonferroni)=1
- im vs imU: p=0.06075, p_ajustado(Bonferroni)=1
- im vs om: p=7.956e-09, p_ajustado(Bonferroni)=2.228e-07
- im vs omL: p=0.5803, p_ajustado(Bonferroni)=1
- im vs pp: p=2.705e-14, p_ajustado(Bonferroni)=7.573e-13
- imS vs imL: p=1, p_ajustado(Bonferroni)=1
- imS vs imU: p=0.3294, p_ajustado(Bonferroni)=1
- imS vs om: p=0.05166, p_ajustado(Bonferroni)=1
- imS vs omL: p=1, p_ajustado(Bonferroni)=1
- imS vs pp: p=0.04365, p_ajustado(Bonferroni)=1
- imL vs imU: p=0.8401, p_ajustado(Bonferroni)=1
- imL vs om: p=0.04522, p_ajustado(Bonferroni)=1
- imL vs omL: p=0.6933, p_ajustado(Bonferroni)=1
- imL vs pp: p=0.03695, p_ajustado(Bonferroni)=1
- imU vs om: p=4.061e-08, p_ajustado(Bonferroni)=1.137e-06
- imU vs omL: p=0.1013, p_ajustado(Bonferroni)=1
- imU vs pp: p=1.161e-11, p_ajustado(Bonferroni)=3.25e-10
- om vs omL: p=0.003044, p_ajustado(Bonferroni)=0.08524
- om vs pp: p=0.811, p_ajustado(Bonferroni)=1
- omL vs pp: p=0.00229, p_ajustado(Bonferroni)=0.06412

**Post-hoc para `aac`** (Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles.):

- cp vs im: p=7.625e-10, p_ajustado(Bonferroni)=2.135e-08
- cp vs imS: p=0.1247, p_ajustado(Bonferroni)=1
- cp vs imL: p=0.9797, p_ajustado(Bonferroni)=1
- cp vs imU: p=1.816e-09, p_ajustado(Bonferroni)=5.084e-08
- cp vs om: p=3.953e-12, p_ajustado(Bonferroni)=1.107e-10
- cp vs omL: p=0.06612, p_ajustado(Bonferroni)=1
- cp vs pp: p=0.2676, p_ajustado(Bonferroni)=1
- im vs imS: p=0.7906, p_ajustado(Bonferroni)=1
- im vs imL: p=0.1692, p_ajustado(Bonferroni)=1
- im vs imU: p=0.2289, p_ajustado(Bonferroni)=1
- im vs om: p=5.353e-09, p_ajustado(Bonferroni)=1.499e-07
- im vs omL: p=0.869, p_ajustado(Bonferroni)=1
- im vs pp: p=1.849e-08, p_ajustado(Bonferroni)=5.178e-07
- imS vs imL: p=0.3333, p_ajustado(Bonferroni)=1
- imS vs imU: p=0.4391, p_ajustado(Bonferroni)=1
- imS vs om: p=0.04528, p_ajustado(Bonferroni)=1
- imS vs omL: p=1, p_ajustado(Bonferroni)=1
- imS vs pp: p=0.05702, p_ajustado(Bonferroni)=1
- imL vs imU: p=0.1064, p_ajustado(Bonferroni)=1
- imL vs om: p=0.02969, p_ajustado(Bonferroni)=0.8312
- imL vs omL: p=0.381, p_ajustado(Bonferroni)=1
- imL vs pp: p=0.7656, p_ajustado(Bonferroni)=1
- imU vs om: p=3.987e-07, p_ajustado(Bonferroni)=1.116e-05
- imU vs omL: p=0.7587, p_ajustado(Bonferroni)=1
- imU vs pp: p=9.095e-09, p_ajustado(Bonferroni)=2.547e-07
- om vs omL: p=0.004274, p_ajustado(Bonferroni)=0.1197
- om vs pp: p=1.656e-10, p_ajustado(Bonferroni)=4.636e-09
- omL vs pp: p=0.03663, p_ajustado(Bonferroni)=1

**Post-hoc para `alm1`** (Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles.):

- cp vs im: p=5.978e-34, p_ajustado(Bonferroni)=1.674e-32
- cp vs imS: p=0.01837, p_ajustado(Bonferroni)=0.5144
- cp vs imL: p=0.02459, p_ajustado(Bonferroni)=0.6886
- cp vs imU: p=6.549e-20, p_ajustado(Bonferroni)=1.834e-18
- cp vs om: p=4.807e-08, p_ajustado(Bonferroni)=1.346e-06
- cp vs omL: p=0.0001597, p_ajustado(Bonferroni)=0.004472
- cp vs pp: p=5.564e-16, p_ajustado(Bonferroni)=1.558e-14
- im vs imS: p=0.2413, p_ajustado(Bonferroni)=1
- im vs imL: p=0.5954, p_ajustado(Bonferroni)=1
- im vs imU: p=0.4565, p_ajustado(Bonferroni)=1
- im vs om: p=3.28e-11, p_ajustado(Bonferroni)=9.185e-10
- im vs omL: p=0.0004638, p_ajustado(Bonferroni)=0.01299
- im vs pp: p=9.955e-19, p_ajustado(Bonferroni)=2.787e-17
- imS vs imL: p=1, p_ajustado(Bonferroni)=1
- imS vs imU: p=0.3638, p_ajustado(Bonferroni)=1
- imS vs om: p=0.1881, p_ajustado(Bonferroni)=1
- imS vs omL: p=1, p_ajustado(Bonferroni)=1
- imS vs pp: p=0.07739, p_ajustado(Bonferroni)=1
- imL vs imU: p=0.7879, p_ajustado(Bonferroni)=1
- imL vs om: p=0.2294, p_ajustado(Bonferroni)=1
- imL vs omL: p=1, p_ajustado(Bonferroni)=1
- imL vs pp: p=0.233, p_ajustado(Bonferroni)=1
- imU vs om: p=2.644e-09, p_ajustado(Bonferroni)=7.403e-08
- imU vs omL: p=0.0008471, p_ajustado(Bonferroni)=0.02372
- imU vs pp: p=2.437e-13, p_ajustado(Bonferroni)=6.824e-12
- om vs omL: p=0.01169, p_ajustado(Bonferroni)=0.3273
- om vs pp: p=0.8305, p_ajustado(Bonferroni)=1
- omL vs pp: p=0.004528, p_ajustado(Bonferroni)=0.1268

**Post-hoc para `alm2`** (Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles.):

- cp vs im: p=2.328e-25, p_ajustado(Bonferroni)=6.518e-24
- cp vs imS: p=0.5081, p_ajustado(Bonferroni)=1
- cp vs imL: p=0.728, p_ajustado(Bonferroni)=1
- cp vs imU: p=2.245e-18, p_ajustado(Bonferroni)=6.286e-17
- cp vs om: p=4.314e-05, p_ajustado(Bonferroni)=0.001208
- cp vs omL: p=0.004061, p_ajustado(Bonferroni)=0.1137
- cp vs pp: p=0.05674, p_ajustado(Bonferroni)=1
- im vs imS: p=0.3903, p_ajustado(Bonferroni)=1
- im vs imL: p=0.7194, p_ajustado(Bonferroni)=1
- im vs imU: p=0.6262, p_ajustado(Bonferroni)=1
- im vs om: p=5.028e-10, p_ajustado(Bonferroni)=1.408e-08
- im vs omL: p=0.0004477, p_ajustado(Bonferroni)=0.01254
- im vs pp: p=7.398e-16, p_ajustado(Bonferroni)=2.071e-14
- imS vs imL: p=1, p_ajustado(Bonferroni)=1
- imS vs imU: p=0.5666, p_ajustado(Bonferroni)=1
- imS vs om: p=0.09706, p_ajustado(Bonferroni)=1
- imS vs omL: p=0.1905, p_ajustado(Bonferroni)=1
- imS vs pp: p=0.3474, p_ajustado(Bonferroni)=1
- imL vs imU: p=0.8662, p_ajustado(Bonferroni)=1
- imL vs om: p=0.1878, p_ajustado(Bonferroni)=1
- imL vs omL: p=0.241, p_ajustado(Bonferroni)=1
- imL vs pp: p=0.6303, p_ajustado(Bonferroni)=1
- imU vs om: p=1.78e-09, p_ajustado(Bonferroni)=4.983e-08
- imU vs omL: p=0.0004224, p_ajustado(Bonferroni)=0.01183
- imU vs pp: p=2.699e-13, p_ajustado(Bonferroni)=7.558e-12
- om vs omL: p=0.3402, p_ajustado(Bonferroni)=1
- om vs pp: p=0.009036, p_ajustado(Bonferroni)=0.253
- omL vs pp: p=0.01843, p_ajustado(Bonferroni)=0.516


## 6. Correlación entre variables continuas

**Pearson:**

| index   |    mcg |      gvh |     aac |   alm1 |    alm2 |
|:--------|-------:|---------:|--------:|-------:|--------:|
| mcg     | 1      |  0.4548  | 0.2207  | 0.397  |  0.1671 |
| gvh     | 0.4548 |  1       | 0.06982 | 0.1735 | -0.1202 |
| aac     | 0.2207 |  0.06982 | 1       | 0.2795 |  0.2527 |
| alm1    | 0.397  |  0.1735  | 0.2795  | 1      |  0.8093 |
| alm2    | 0.1671 | -0.1202  | 0.2527  | 0.8093 |  1      |

**Spearman:**

| index   |     mcg |      gvh |    aac |   alm1 |     alm2 |
|:--------|--------:|---------:|-------:|-------:|---------:|
| mcg     | 1       |  0.4594  | 0.236  | 0.444  |  0.09125 |
| gvh     | 0.4594  |  1       | 0.0462 | 0.285  | -0.09233 |
| aac     | 0.236   |  0.0462  | 1      | 0.3439 |  0.2702  |
| alm1    | 0.444   |  0.285   | 0.3439 | 1      |  0.7151  |
| alm2    | 0.09125 | -0.09233 | 0.2702 | 0.7151 |  1       |

## 7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)

| variable   | prueba                                               |   p_valor |   cramers_v | significativo   |
|:-----------|:-----------------------------------------------------|----------:|------------:|:----------------|
| lip        | Chi-cuadrado (¡ojo: >20% de celdas con esperado <5!) | 3.749e-47 |      0.8368 | True            |
| chg        | Chi-cuadrado (¡ojo: >20% de celdas con esperado <5!) | 8.454e-33 |      0.7061 | True            |

## 8. Relevancia de variables frente a la clase (ranking)

| variable   |   anova_f_p |   kruskal_h_p |   info_mutua |
|:-----------|------------:|--------------:|-------------:|
| alm1       |  1.026e-108 |     8.739e-52 |       0.6847 |
| alm2       |  2.364e-74  |     2.121e-36 |       0.4703 |
| mcg        |  8.304e-50  |     2.305e-36 |       0.4257 |
| gvh        |  2.652e-56  |     4.037e-32 |       0.3738 |
| aac        |  2.762e-30  |     5.449e-22 |       0.262  |

## 9. Multicolinealidad (VIF y número de condición)

| variable   |   VIF |
|:-----------|------:|
| alm1       | 4.053 |
| alm2       | 3.71  |
| mcg        | 1.499 |
| gvh        | 1.472 |
| aac        | 1.11  |

Índice de condición de la matriz estandarizada: 4.03

## 10. Detección de outliers (Z-score, IQR, Mahalanobis)

| variable   |   n_outliers_zscore(|z|>3) |   n_outliers_iqr(1.5x) |   limite_inferior_iqr |   limite_superior_iqr |
|:-----------|---------------------------:|-----------------------:|----------------------:|----------------------:|
| mcg        |                          0 |                      0 |               -0.1438 |                 1.146 |
| gvh        |                          1 |                     13 |                0.145  |                 0.825 |
| aac        |                          3 |                      9 |                0.195  |                 0.795 |
| alm1       |                          0 |                      0 |               -0.24   |                 1.28  |
| alm2       |                          0 |                      0 |               -0.19   |                 1.25  |

Mahalanobis multivariado: 6 outlier(s) de 336 filas evaluadas (umbral chi² = 20.5).

## 11. Balance de la variable objetivo

Clases: 8 (cp: 143, im: 77, pp: 52, imU: 35, om: 20, omL: 5, imS: 2, imL: 2)

Prueba: Chi-cuadrado de bondad de ajuste (vs. uniforme)

p-valor: 1.802e-81

¿Desbalanceado respecto a distribución uniforme? Sí

