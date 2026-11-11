"""Prueba de factibilidad del proyecto (compuerta de viabilidad, antes de la Entrega 2).

Responde con datos tres preguntas:
  1. ¿Hay suficientes commits etiquetados y cuál es la prevalencia por año?
  2. ¿Hay señal? AUC-PR de modelos simples frente a la prevalencia (= AUC-PR de la
     clase mayoritaria), entrenando con el pasado y evaluando año por año.
  3. ¿Se ve deriva hacia 2026? ¿Cuántos commits traen Assisted-by?

No es el experimento del proyecto: no hay ajuste de hiperparámetros ni modelo
difuso. El árbol de 15 hojas es solo un indicador de que unas pocas reglas
capturan señal. La prueba de 2026 aquí se usa una vez y solo para decidir
viabilidad; el experimento final volverá a congelar la partición.

Uso:  python src/factibilidad.py --datos ~/datos-kernel/commits.parquet
Salida: factibilidad/resultados.json, factibilidad/*.png
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

# ---------------------------------------------------------------- parámetros
SEMILLA = 20261107
ENTRENA = ("2019-01-01", "2023-01-01")
PERIODOS = {"2023": ("2023-01-01", "2024-01-01"), "2024": ("2024-01-01", "2025-01-01"),
            "2025": ("2025-01-01", "2026-01-01"), "2026 ene-jul": ("2026-01-01", "2026-08-01")}
N_BOOT = 200
SALIDA = Path(__file__).resolve().parent.parent / "factibilidad"
VARIABLES = ["lineas_add", "lineas_del", "n_archivos", "n_binarios", "n_dirs_raiz",
             "n_subsistemas", "n_reviewed", "n_acked", "n_tested", "n_reported", "n_signed",
             "n_codev", "n_link", "cc_stable", "es_fix", "asunto_fix", "len_asunto",
             "exp_autor", "dias_desde_primer_commit", "exp_autor_subsistema", "hora_utc",
             "dia_semana"]
AZUL, DORADO, VERDE, PLATA, SABLE = "#1291C0", "#B49739", "#00A859", "#98999A", "#373435"


def tramo(df, a, b):
    return df[(df["fecha"] >= pd.Timestamp(a, tz="UTC")) & (df["fecha"] < pd.Timestamp(b, tz="UTC"))]


def ic_ap(y, p, rng):
    n = len(y)
    vals = []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        if y[i].sum() > 0:
            vals.append(average_precision_score(y[i], p[i]))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    args = ap.parse_args()
    SALIDA.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEMILLA)

    df = pd.read_parquet(Path(args.datos).expanduser())
    corte = df["fecha"].max()
    obs = df[~df["censurado"]].copy()
    obs["anio"] = obs["fecha"].dt.year
    res = {"corte_repositorio": str(corte), "n_commits_total": int(len(df)),
           "n_observados_90d": int(len(obs)), "n_censurados": int(df["censurado"].sum())}

    # 1. Prevalencia por año
    por_anio = obs.groupby("anio").agg(n=("riesgoso", "size"), positivos=("riesgoso", "sum"),
                                       prevalencia=("riesgoso", "mean"),
                                       es_fix=("es_fix", "mean"))
    res["por_anio"] = {int(k): {c: (float(v) if c != "n" and c != "positivos" else int(v))
                                for c, v in r.items()} for k, r in por_anio.iterrows()}

    # 3a. Assisted-by en 2026
    d26 = df[df["fecha"] >= pd.Timestamp("2026-01-01", tz="UTC")].copy()
    d26["mes"] = d26["fecha"].dt.strftime("%Y-%m")
    ab = d26.groupby("mes").agg(commits=("assisted_by", "size"), assisted=("assisted_by", "sum"))
    res["assisted_by_por_mes"] = {k: {"commits": int(r.commits), "assisted": int(r.assisted)}
                                  for k, r in ab.iterrows()}
    o26 = tramo(obs, "2026-01-01", "2026-08-01")
    g = o26.groupby("assisted_by")["riesgoso"].agg(["size", "mean"])
    res["assisted_by_prevalencia_2026_observados"] = {
        ("con" if k else "sin"): {"n": int(r["size"]), "prevalencia": float(r["mean"])}
        for k, r in g.iterrows()}
    res["assisted_by_ejemplos_valor"] = d26.loc[d26["assisted_by"] == 1, "assisted_valor"] \
        .value_counts().head(8).to_dict()

    # 2. Señal: entrenar con el pasado, evaluar por año
    tr = tramo(obs, *ENTRENA)
    X, y = tr[VARIABLES].to_numpy(float), tr["riesgoso"].to_numpy()
    log1p = FunctionTransformer(lambda z: np.log1p(np.clip(z, 0, None)))
    modelos = {
        "regresion_logistica": make_pipeline(log1p, StandardScaler(),
                                             LogisticRegression(max_iter=2000)),
        "gradient_boosting": HistGradientBoostingClassifier(random_state=SEMILLA),
        "arbol_15_hojas": DecisionTreeClassifier(max_leaf_nodes=15, min_samples_leaf=200,
                                                 random_state=SEMILLA),
    }
    res["entrenamiento"] = {"tramo": ENTRENA, "n": int(len(tr)), "prevalencia": float(y.mean())}
    res["evaluacion"] = {}
    for nombre, m in modelos.items():
        m.fit(X, y)
        res["evaluacion"][nombre] = {}
        for per, (a, b) in PERIODOS.items():
            te = tramo(obs, a, b)
            if te["riesgoso"].sum() == 0:
                continue
            yt = te["riesgoso"].to_numpy()
            p = m.predict_proba(te[VARIABLES].to_numpy(float))[:, 1]
            res["evaluacion"][nombre][per] = {
                "n": int(len(te)), "prevalencia": float(yt.mean()),
                "auc_pr": float(average_precision_score(yt, p)), "ic95_auc_pr": ic_ap(yt, p, rng),
                "auc_roc": float(roc_auc_score(yt, p)),
                "auc_pr_sobre_prevalencia": float(average_precision_score(yt, p) / yt.mean())}
    res["reglas_arbol_15_hojas"] = export_text(modelos["arbol_15_hojas"],
                                               feature_names=VARIABLES, max_depth=6)

    (SALIDA / "resultados.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))

    # Figuras
    fig, ax = plt.subplots(figsize=(6, 2.6))
    ax.bar(por_anio.index, por_anio["prevalencia"] * 100, color=AZUL)
    ax.set_ylabel("% riesgosos (Fixes: ≤90 d)")
    ax.set_title("Prevalencia por año (commits observados ≥90 días)", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(SALIDA / "prevalencia_por_anio.png", dpi=200)

    fig, ax = plt.subplots(figsize=(6, 2.8))
    pers = list(PERIODOS)
    for nombre, color in zip(modelos, [AZUL, DORADO, VERDE]):
        v = [res["evaluacion"][nombre].get(p, {}).get("auc_pr", np.nan) for p in pers]
        ax.plot(pers, v, "o-", color=color, label=nombre.replace("_", " "))
    prev = [res["evaluacion"]["regresion_logistica"].get(p, {}).get("prevalencia", np.nan)
            for p in pers]
    ax.plot(pers, prev, "s--", color=PLATA, label="clase mayoritaria (prevalencia)")
    ax.set_ylabel("AUC-PR")
    ax.set_title("Entrenado con 2019–2022, evaluado por periodo", fontsize=10)
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(SALIDA / "auc_pr_por_periodo.png", dpi=200)
    print(json.dumps({k: v for k, v in res.items() if k != "reglas_arbol_15_hojas"},
                     indent=1, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
