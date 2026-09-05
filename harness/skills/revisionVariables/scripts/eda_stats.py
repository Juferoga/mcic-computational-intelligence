#!/usr/bin/env python3
"""
eda_stats.py — Automatiza la revisión estadística exploratoria de variables
en un dataset de clasificación (ver SKILL.md / references/tabla_pruebas.md
para el marco teórico completo).

Uso:
    python eda_stats.py --data ruta/al/dataset.csv --target nombre_columna_clase \
        [--output-dir salida/] [--alpha 0.05] [--id-cols col1,col2]

Requiere: pandas, numpy, scipy, scikit-learn, matplotlib.
No depende de statsmodels ni scikit-posthocs: el VIF se calcula invirtiendo
la matriz de correlación y los post-hoc se aproximan con pruebas pareadas +
corrección de Bonferroni (se deja indicado cuándo conviene un paquete
especializado para el valor exacto).

Salida:
    <output-dir>/reporte.md         -> reporte narrativo con todos los resultados
    <output-dir>/figuras/*.png      -> histogramas, boxplots, Q-Q, mapas de calor
"""

import argparse
import os
import sys
import warnings
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    from sklearn.feature_selection import mutual_info_classif
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# --------------------------------------------------------------------------
# Utilidades generales
# --------------------------------------------------------------------------

def log(msg):
    print(f"[eda_stats] {msg}")


def classify_columns(df, target, id_cols, max_unique_for_categorical=15):
    """Separa columnas en continuas y categóricas usando heurísticas simples.
    El usuario puede corregir la clasificación a mano si el heurístico falla
    (p. ej. una variable codificada como entero que en realidad es nominal)."""
    numeric_cols, categorical_cols = [], []
    for col in df.columns:
        if col == target or col in id_cols:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique(dropna=True) <= max_unique_for_categorical:
                categorical_cols.append(col)
            else:
                numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols


def bonferroni_pairs(pvals):
    """Corrección de Bonferroni simple para una lista de p-values de
    comparaciones pareadas. Devuelve p-values ajustados (tope en 1.0)."""
    n = len(pvals)
    return [min(p * n, 1.0) for p in pvals]


# --------------------------------------------------------------------------
# Paso 1: estadística descriptiva
# --------------------------------------------------------------------------

def descriptive_stats(df, numeric_cols):
    rows = []
    for col in numeric_cols:
        s = df[col].dropna()
        rows.append({
            "variable": col,
            "n": s.shape[0],
            "faltantes": df[col].isna().sum(),
            "media": s.mean(),
            "mediana": s.median(),
            "desv_std": s.std(),
            "asimetria": stats.skew(s) if len(s) > 2 else np.nan,
            "curtosis": stats.kurtosis(s) if len(s) > 2 else np.nan,
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Paso 2: normalidad
# --------------------------------------------------------------------------

def normality_tests(series, alpha):
    """Aplica Shapiro-Wilk (si n es manejable) y D'Agostino-Pearson.
    Devuelve un dict con el veredicto y los p-values."""
    s = series.dropna().values
    result = {"n": len(s)}
    if len(s) < 3:
        result["veredicto"] = "n insuficiente"
        return result

    if 3 <= len(s) <= 5000:
        stat, p = stats.shapiro(s)
        result["shapiro_p"] = p
    else:
        # Con n grande, Shapiro-Wilk pierde utilidad práctica; usar K-S contra
        # una normal ajustada a media/desv. de la muestra (aprox. Lilliefors).
        stat, p = stats.kstest(s, stats.norm(loc=s.mean(), scale=s.std(ddof=1)).cdf)
        result["ks_lilliefors_p"] = p

    if len(s) >= 8:
        stat_k2, p_k2 = stats.normaltest(s)  # D'Agostino-Pearson K^2
        result["dagostino_p"] = p_k2

    p_ref = result.get("shapiro_p", result.get("ks_lilliefors_p"))
    result["veredicto"] = "normal" if p_ref is not None and p_ref > alpha else "no normal"
    return result


def run_normality_by_group(df, numeric_cols, target, alpha):
    records = []
    for col in numeric_cols:
        overall = normality_tests(df[col], alpha)
        overall["variable"] = col
        overall["grupo"] = "(global)"
        records.append(overall)
        for cls, sub in df.groupby(target)[col]:
            res = normality_tests(sub, alpha)
            res["variable"] = col
            res["grupo"] = str(cls)
            records.append(res)
    return pd.DataFrame(records)


# --------------------------------------------------------------------------
# Paso 3: homogeneidad de varianzas
# --------------------------------------------------------------------------

def homogeneity_tests(df, col, target, alpha):
    groups = [sub.dropna().values for _, sub in df.groupby(target)[col] if sub.dropna().shape[0] > 1]
    if len(groups) < 2:
        return {"variable": col, "veredicto": "no aplica (menos de 2 grupos con datos)"}
    out = {"variable": col}
    try:
        stat, p = stats.levene(*groups)
        out["levene_p"] = p
    except Exception:
        out["levene_p"] = np.nan
    try:
        stat, p = stats.fligner(*groups)
        out["fligner_p"] = p
    except Exception:
        out["fligner_p"] = np.nan
    p_ref = out.get("levene_p", np.nan)
    out["veredicto"] = "homogénea" if (not np.isnan(p_ref) and p_ref > alpha) else "heterogénea"
    return out


# --------------------------------------------------------------------------
# Paso 4/5: comparación entre clases (2 o más)
# --------------------------------------------------------------------------

def compare_variable_across_classes(df, col, target, alpha, normality_df, homogeneity_row):
    classes = df[target].dropna().unique()
    n_classes = len(classes)
    groups = {cls: df.loc[df[target] == cls, col].dropna().values for cls in classes}
    groups = {k: v for k, v in groups.items() if len(v) > 1}

    per_class_normal = all(
        normality_df.loc[
            (normality_df["variable"] == col) & (normality_df["grupo"] == str(cls)), "veredicto"
        ].eq("normal").all()
        for cls in groups.keys()
    ) if len(groups) else False
    var_homogenea = homogeneity_row.get("veredicto") == "homogénea"

    result = {"variable": col, "n_clases": n_classes}

    if n_classes == 2:
        (g1, g2) = list(groups.values())[:2] if len(groups) >= 2 else (None, None)
        if g1 is None:
            result["ruta"] = "no aplica"
            return result
        if per_class_normal:
            if var_homogenea:
                stat, p = stats.ttest_ind(g1, g2, equal_var=True)
                result["prueba"] = "t-test de Student"
            else:
                stat, p = stats.ttest_ind(g1, g2, equal_var=False)
                result["prueba"] = "t-test de Welch"
        else:
            stat, p = stats.mannwhitneyu(g1, g2, alternative="two-sided")
            result["prueba"] = "Mann-Whitney U"
        result["estadistico"] = stat
        result["p_valor"] = p
        result["significativo"] = p < alpha
    else:
        arrs = list(groups.values())
        if len(arrs) < 2:
            result["ruta"] = "no aplica"
            return result
        if per_class_normal and var_homogenea:
            stat, p = stats.f_oneway(*arrs)
            result["prueba"] = "ANOVA de un factor"
        else:
            stat, p = stats.kruskal(*arrs)
            result["prueba"] = "Kruskal-Wallis"
        result["estadistico"] = stat
        result["p_valor"] = p
        result["significativo"] = p < alpha

        # Post-hoc aproximado (pareado + Bonferroni) solo si el global es significativo
        if result["significativo"] and len(groups) > 2:
            keys = list(groups.keys())
            pvals, labels = [], []
            for a, b in combinations(keys, 2):
                if per_class_normal and var_homogenea:
                    _, pp = stats.ttest_ind(groups[a], groups[b], equal_var=True)
                else:
                    _, pp = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided")
                pvals.append(pp)
                labels.append(f"{a} vs {b}")
            adj = bonferroni_pairs(pvals)
            result["post_hoc"] = list(zip(labels, pvals, adj))
            result["post_hoc_nota"] = (
                "Aproximación con pruebas pareadas + Bonferroni. Para el valor exacto de "
                "Tukey HSD o Dunn's test, usar statsmodels / scikit-posthocs si están disponibles."
            )
    return result


# --------------------------------------------------------------------------
# Paso 6: correlación entre continuas
# --------------------------------------------------------------------------

def correlation_analysis(df, numeric_cols, method="pearson"):
    if len(numeric_cols) < 2:
        return None
    return df[numeric_cols].corr(method=method)


# --------------------------------------------------------------------------
# Paso 7: asociación entre categóricas (incluida la clase)
# --------------------------------------------------------------------------

def cramers_v(chi2_stat, n, r, k):
    return np.sqrt((chi2_stat / n) / (min(r - 1, k - 1))) if min(r - 1, k - 1) > 0 else np.nan


def categorical_association(df, col, target, alpha):
    table = pd.crosstab(df[col], df[target])
    r, k = table.shape
    n = table.values.sum()
    result = {"variable": col}
    chi2_stat, p, dof, expected = stats.chi2_contingency(table)
    low_expected = (expected < 5).mean() > 0.2
    if r == 2 and k == 2:
        _, p_fisher = stats.fisher_exact(table)
        result["prueba"] = "Fisher exacto" if low_expected else "Chi-cuadrado (Fisher como respaldo)"
        result["p_valor"] = p_fisher if low_expected else p
    else:
        result["prueba"] = "Chi-cuadrado" + (" (¡ojo: >20% de celdas con esperado <5!)" if low_expected else "")
        result["p_valor"] = p
    result["cramers_v"] = cramers_v(chi2_stat, n, r, k)
    result["significativo"] = result["p_valor"] < alpha
    return result


# --------------------------------------------------------------------------
# Paso 8: relevancia de variables frente a la clase
# --------------------------------------------------------------------------

def feature_relevance(df, numeric_cols, target):
    rows = []
    y = df[target]
    groups_by_col = {}
    for col in numeric_cols:
        sub = df[[col, target]].dropna()
        groups = [g[col].values for _, g in sub.groupby(target)]
        groups_by_col[col] = groups
        f_stat, f_p = stats.f_oneway(*groups) if len(groups) > 1 else (np.nan, np.nan)
        h_stat, h_p = stats.kruskal(*groups) if len(groups) > 1 else (np.nan, np.nan)
        rows.append({"variable": col, "anova_f_p": f_p, "kruskal_h_p": h_p})

    if HAS_SKLEARN and numeric_cols:
        try:
            sub = df[numeric_cols + [target]].dropna()
            mi = mutual_info_classif(sub[numeric_cols], sub[target], discrete_features=False, random_state=0)
            mi_map = dict(zip(numeric_cols, mi))
            for row in rows:
                row["info_mutua"] = mi_map.get(row["variable"], np.nan)
        except Exception as e:
            log(f"No se pudo calcular información mutua: {e}")
    return pd.DataFrame(rows).sort_values("kruskal_h_p")


# --------------------------------------------------------------------------
# Paso 9: multicolinealidad
# --------------------------------------------------------------------------

def multicollinearity(df, numeric_cols):
    sub = df[numeric_cols].dropna()
    if sub.shape[0] < 3 or len(numeric_cols) < 2:
        return None, None
    standardized = (sub - sub.mean()) / sub.std(ddof=0)
    corr = standardized.corr().values
    try:
        inv_corr = np.linalg.pinv(corr)
        vif = np.diag(inv_corr)
    except np.linalg.LinAlgError:
        vif = np.full(len(numeric_cols), np.nan)
    vif_df = pd.DataFrame({"variable": numeric_cols, "VIF": vif}).sort_values("VIF", ascending=False)
    try:
        cond_number = np.linalg.cond(standardized.values)
    except Exception:
        cond_number = np.nan
    return vif_df, cond_number


# --------------------------------------------------------------------------
# Paso 10: outliers
# --------------------------------------------------------------------------

def outlier_detection(df, numeric_cols):
    rows = []
    for col in numeric_cols:
        s = df[col].dropna()
        if len(s) < 4:
            continue
        z = (s - s.mean()) / s.std(ddof=0)
        n_zscore = (z.abs() > 3).sum()

        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_iqr = ((s < low) | (s > high)).sum()

        rows.append({
            "variable": col, "n_outliers_zscore(|z|>3)": n_zscore,
            "n_outliers_iqr(1.5x)": n_iqr, "limite_inferior_iqr": low, "limite_superior_iqr": high,
        })
    return pd.DataFrame(rows)


def mahalanobis_outliers(df, numeric_cols, alpha=0.001):
    sub = df[numeric_cols].dropna()
    if sub.shape[0] < len(numeric_cols) + 2 or len(numeric_cols) < 2:
        return None
    mean = sub.mean().values
    try:
        inv_cov = np.linalg.pinv(np.cov(sub.values, rowvar=False))
    except Exception:
        return None
    diffs = sub.values - mean
    d2 = np.einsum("ij,jk,ik->i", diffs, inv_cov, diffs)
    threshold = stats.chi2.ppf(1 - alpha, df=len(numeric_cols))
    n_outliers = int((d2 > threshold).sum())
    return {"n_filas_evaluadas": sub.shape[0], "umbral_chi2": threshold, "n_outliers_multivariados": n_outliers}


# --------------------------------------------------------------------------
# Paso 11: balance de clases
# --------------------------------------------------------------------------

def class_balance(df, target, alpha):
    counts = df[target].value_counts()
    n = counts.sum()
    k = len(counts)
    result = {"n_clases": k, "conteos": counts.to_dict()}
    if k == 2:
        p = stats.binomtest(counts.iloc[0], n, 0.5).pvalue
        result["prueba"] = "Test binomial"
        result["p_valor"] = p
    else:
        expected = [n / k] * k
        stat, p = stats.chisquare(counts.values, f_exp=expected)
        result["prueba"] = "Chi-cuadrado de bondad de ajuste (vs. uniforme)"
        result["p_valor"] = p
    result["desbalanceado"] = result["p_valor"] < alpha
    return result


# --------------------------------------------------------------------------
# Gráficos (sección 13 del documento)
# --------------------------------------------------------------------------

def make_plots(df, numeric_cols, target, outdir):
    if not HAS_MPL:
        log("matplotlib no disponible: se omiten las figuras.")
        return
    figdir = os.path.join(outdir, "figuras")
    os.makedirs(figdir, exist_ok=True)

    for col in numeric_cols:
        s = df[col].dropna()
        if len(s) < 3:
            continue
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))

        axes[0].hist(s, bins=30, density=True, alpha=0.6, color="#4C72B0")
        try:
            kde = stats.gaussian_kde(s)
            xs = np.linspace(s.min(), s.max(), 200)
            axes[0].plot(xs, kde(xs), color="black")
        except Exception:
            pass
        axes[0].set_title(f"Histograma + KDE: {col}")

        df.boxplot(column=col, by=target, ax=axes[1])
        axes[1].set_title(f"Boxplot por clase: {col}")
        axes[1].set_xlabel(target)

        stats.probplot(s, dist="norm", plot=axes[2])
        axes[2].set_title(f"Q-Q plot: {col}")

        plt.suptitle("")
        plt.tight_layout()
        plt.savefig(os.path.join(figdir, f"{col}_diagnostico.png"), dpi=110)
        plt.close(fig)

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(method="pearson")
        fig, ax = plt.subplots(figsize=(1 + 0.6 * len(numeric_cols), 1 + 0.6 * len(numeric_cols)))
        im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=90)
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_yticklabels(numeric_cols)
        plt.colorbar(im)
        ax.set_title("Mapa de calor de correlación (Pearson)")
        plt.tight_layout()
        plt.savefig(os.path.join(figdir, "correlacion_heatmap.png"), dpi=110)
        plt.close(fig)

    # Gráfico de distribución de clases
    fig, ax = plt.subplots(figsize=(8, 4))
    counts = df[target].value_counts()
    counts.plot(kind="bar", color="#4C72B0", ax=ax)
    ax.set_title(f"Distribución de la variable objetivo ({target})")
    ax.set_xlabel(target)
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=45 if len(counts) > 4 else 0)
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "distribucion_clases.png"), dpi=110)
    plt.close(fig)

    # Gráfico PCA 2D si sklearn está disponible
    if HAS_SKLEARN and len(numeric_cols) >= 2:
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            sub = df[numeric_cols + [target]].dropna()
            if sub.shape[0] >= 3:
                X_scaled = StandardScaler().fit_transform(sub[numeric_cols])
                pca = PCA(n_components=2)
                X_pca = pca.fit_transform(X_scaled)
                var_exp = pca.explained_variance_ratio_ * 100

                fig, ax = plt.subplots(figsize=(8, 6))
                classes = sub[target].unique()
                for cls in classes:
                    mask = (sub[target] == cls).values
                    ax.scatter(X_pca[mask, 0], X_pca[mask, 1], label=str(cls), alpha=0.7, edgecolors="none")
                ax.set_xlabel(f"PC1 ({var_exp[0]:.1f}% varianza explicada)")
                ax.set_ylabel(f"PC2 ({var_exp[1]:.1f}% varianza explicada)")
                ax.set_title(f"Proyección PCA 2D por {target}")
                ax.legend(title=target, bbox_to_anchor=(1.05, 1), loc="upper left")
                plt.tight_layout()
                plt.savefig(os.path.join(figdir, "pca_2d.png"), dpi=110)
                plt.close(fig)
        except Exception as e:
            log(f"No se pudo generar gráfico PCA: {e}")

    fig, ax = plt.subplots(figsize=(1 + 0.4 * len(df.columns), 4))
    ax.imshow(df.isna().values.T, aspect="auto", cmap="viridis")
    ax.set_yticks(range(len(df.columns)))
    ax.set_yticklabels(df.columns)
    ax.set_title("Mapa de valores faltantes (amarillo = faltante)")
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "faltantes_heatmap.png"), dpi=110)
    plt.close(fig)

    log(f"Figuras guardadas en {figdir}")


# --------------------------------------------------------------------------
# Reporte
# --------------------------------------------------------------------------

def build_report(path, sections):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Reporte de revisión estadística de variables\n\n")
        for title, content in sections:
            f.write(f"## {title}\n\n{content}\n\n")
    log(f"Reporte escrito en {path}")


def df_to_md(df, float_format="{:.4g}"):
    if df is None or df.empty:
        return "_Sin datos suficientes._"
    return df.to_markdown(index=False, floatfmt=".4g")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Revisión estadística de variables para datasets de clasificación.")
    parser.add_argument("--data", required=True, help="Ruta al CSV del dataset.")
    parser.add_argument("--target", required=True, help="Nombre de la columna de clase/objetivo.")
    parser.add_argument("--sep", default="auto", help="Separador CSV (default: auto, o ';', ',', r'\\s+').")
    parser.add_argument("--output-dir", default="salida_eda_stats", help="Carpeta de salida.")
    parser.add_argument("--alpha", type=float, default=0.05, help="Nivel de significancia.")
    parser.add_argument("--id-cols", default="", help="Columnas a excluir (ids), separadas por coma.")
    parser.add_argument("--numeric-cols", default="", help="Columnas numéricas explícitas (separadas por coma).")
    parser.add_argument("--categorical-cols", default="", help="Columnas categóricas explícitas (separadas por coma).")
    args = parser.parse_args()

    id_cols = [c.strip() for c in args.id_cols.split(",") if c.strip()]
    os.makedirs(args.output_dir, exist_ok=True)

    if args.sep == "auto":
        try:
            df = pd.read_csv(args.data, sep=None, engine="python")
        except Exception:
            try:
                df = pd.read_csv(args.data, sep=";")
            except Exception:
                df = pd.read_csv(args.data)
    elif args.sep in [r"\s+", "whitespace", "space"]:
        df = pd.read_csv(args.data, sep=r"\s+", engine="python")
    else:
        df = pd.read_csv(args.data, sep=args.sep)

    if args.target not in df.columns:
        sys.exit(f"La columna objetivo '{args.target}' no está en el dataset. Columnas disponibles: {list(df.columns)}")

    if args.numeric_cols:
        numeric_cols = [c.strip() for c in args.numeric_cols.split(",") if c.strip()]
    else:
        numeric_cols = None

    if args.categorical_cols:
        categorical_cols = [c.strip() for c in args.categorical_cols.split(",") if c.strip()]
    else:
        categorical_cols = None

    if numeric_cols is None or categorical_cols is None:
        auto_num, auto_cat = classify_columns(df, args.target, id_cols)
        if numeric_cols is None:
            numeric_cols = auto_num
        if categorical_cols is None:
            categorical_cols = auto_cat

    log(f"Variables continuas detectadas: {numeric_cols}")
    log(f"Variables categóricas detectadas: {categorical_cols}")

    sections = []

    # Paso 0/1
    desc = descriptive_stats(df, numeric_cols)
    sections.append(("0-1. Tipificación y estadística descriptiva",
                      f"Continuas: {numeric_cols}\n\nCategóricas: {categorical_cols}\n\n" + df_to_md(desc)))

    # Paso 2
    norm_df = run_normality_by_group(df, numeric_cols, args.target, args.alpha)
    sections.append(("2. Pruebas de normalidad (global y por clase)", df_to_md(norm_df)))

    # Paso 3
    homog_rows = [homogeneity_tests(df, col, args.target, args.alpha) for col in numeric_cols]
    homog_df = pd.DataFrame(homog_rows)
    sections.append(("3. Homogeneidad de varianzas (Levene / Fligner-Killeen)", df_to_md(homog_df)))

    # Paso 4/5
    comp_rows = []
    for col in numeric_cols:
        hrow = next((r for r in homog_rows if r["variable"] == col), {})
        res = compare_variable_across_classes(df, col, args.target, args.alpha, norm_df, hrow)
        comp_rows.append(res)
    comp_summary = pd.DataFrame([{k: v for k, v in r.items() if k != "post_hoc" and k != "post_hoc_nota"} for r in comp_rows])
    posthoc_text = ""
    for r in comp_rows:
        if r.get("post_hoc"):
            posthoc_text += f"\n**Post-hoc para `{r['variable']}`** ({r['post_hoc_nota']}):\n\n"
            for label, p, p_adj in r["post_hoc"]:
                posthoc_text += f"- {label}: p={p:.4g}, p_ajustado(Bonferroni)={p_adj:.4g}\n"
    sections.append(("4-5. Comparación de variables continuas entre clases",
                      df_to_md(comp_summary) + "\n" + posthoc_text))

    # Paso 6
    pearson_corr = correlation_analysis(df, numeric_cols, "pearson")
    spearman_corr = correlation_analysis(df, numeric_cols, "spearman")
    corr_text = "**Pearson:**\n\n" + df_to_md(pearson_corr.reset_index() if pearson_corr is not None else None)
    corr_text += "\n\n**Spearman:**\n\n" + df_to_md(spearman_corr.reset_index() if spearman_corr is not None else None)
    sections.append(("6. Correlación entre variables continuas", corr_text))

    # Paso 7
    cat_rows = [categorical_association(df, col, args.target, args.alpha) for col in categorical_cols]
    sections.append(("7. Asociación entre categóricas y la clase (chi²/Fisher/Cramér V)",
                      df_to_md(pd.DataFrame(cat_rows))))

    # Paso 8
    rel_df = feature_relevance(df, numeric_cols, args.target)
    sections.append(("8. Relevancia de variables frente a la clase (ranking)", df_to_md(rel_df)))

    # Paso 9
    vif_df, cond_number = multicollinearity(df, numeric_cols)
    vif_text = df_to_md(vif_df)
    vif_text += f"\n\nÍndice de condición de la matriz estandarizada: {cond_number:.2f}" if cond_number else ""
    sections.append(("9. Multicolinealidad (VIF y número de condición)", vif_text))

    # Paso 10
    out_df = outlier_detection(df, numeric_cols)
    maha = mahalanobis_outliers(df, numeric_cols)
    out_text = df_to_md(out_df)
    if maha:
        out_text += (
            f"\n\nMahalanobis multivariado: {maha['n_outliers_multivariados']} outlier(s) de "
            f"{maha['n_filas_evaluadas']} filas evaluadas (umbral chi² = {maha['umbral_chi2']:.3g})."
        )
    sections.append(("10. Detección de outliers (Z-score, IQR, Mahalanobis)", out_text))

    # Paso 11
    bal = class_balance(df, args.target, args.alpha)
    conteos_txt = ", ".join(f"{k}: {v}" for k, v in bal["conteos"].items())
    bal_txt = (
        f"Clases: {bal['n_clases']} ({conteos_txt})\n\n"
        f"Prueba: {bal['prueba']}\n\n"
        f"p-valor: {float(bal['p_valor']):.4g}\n\n"
        f"¿Desbalanceado respecto a distribución uniforme? {'Sí' if bal['desbalanceado'] else 'No'}"
    )
    sections.append(("11. Balance de la variable objetivo", bal_txt))

    build_report(os.path.join(args.output_dir, "reporte.md"), sections)
    make_plots(df, numeric_cols, args.target, args.output_dir)


if __name__ == "__main__":
    main()
