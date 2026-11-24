"""Piezas comunes del experimento: datos, particiones, modelos, métricas y registro.

Todas las decisiones metodológicas viven aquí para que cada etapa
(e2_exploracion, e3_referencias, e4_busqueda, final_prueba) use exactamente
las mismas.

Partición temporal (nunca aleatoria):
  - Inicio del entrenamiento: 2019-01-01 (antes la prevalencia sube por la
    adopción del trailer Fixes:, no por riesgo; ver factibilidad/README.md).
  - Validación con ventana creciente: para cada año V en 2023, 2024 y 2025 se
    entrena con [2019-01-01, inicio(V) - 90 d) y se valida con el año V. El
    hueco de 90 días evita usar etiquetas que aún no existirían al momento
    de entrenar.
  - Prueba: commits del 2026-01-01 al 2026-07-31 (todos con >=90 días de
    observación). El modelo final se entrena con [2019-01-01, 2025-10-03).
"""
import csv
import datetime as dt
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, matthews_corrcoef, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados"
CONFIG = RAIZ / "config"
DATOS = Path(os.environ.get("DATOS_KERNEL", "~/datos-kernel/commits.parquet")).expanduser()

INICIO = "2019-01-01"
HUECO_DIAS = 90
VENTANAS_VAL = {"2023": ("2023-01-01", "2024-01-01"), "2024": ("2024-01-01", "2025-01-01"),
                "2025": ("2025-01-01", "2026-01-01")}
PRUEBA = ("2026-01-01", "2026-08-01")
N_BOOT = 1000
SEMILLAS = [11, 23, 37, 41, 53]

# Variables conocidas al integrar el commit (D5). Todas numéricas.
VARIABLES = ["lineas_add", "lineas_del", "n_archivos", "n_binarios", "n_dirs_raiz",
             "n_subsistemas", "n_reviewed", "n_acked", "n_tested", "n_reported", "n_signed",
             "n_codev", "n_link", "cc_stable", "es_fix", "asunto_fix", "len_asunto",
             "exp_autor", "dias_desde_primer_commit", "exp_autor_subsistema", "hora_utc",
             "dia_semana"]
# Subconjunto legible para las reglas difusas: tamaño, difusión, revisión, propósito y
# experiencia (las familias de Kamei et al.), fijado antes de ver resultados.
VARIABLES_DIFUSO = ["lineas_add", "lineas_del", "n_archivos", "n_subsistemas", "n_reviewed",
                    "n_signed", "es_fix", "cc_stable", "exp_autor", "exp_autor_subsistema"]
# Iteración 2 (config/protocolo_iteracion2.json): las 10 originales más 9 de VARIABLES. Se
# excluyen n_dirs_raiz (correlación 0,97 con n_subsistemas), hora_utc y dia_semana.
VARIABLES_DIFUSO_AMPLIADAS = VARIABLES_DIFUSO + [
    "n_acked", "n_tested", "n_reported", "n_link", "n_codev", "asunto_fix", "len_asunto",
    "n_binarios", "dias_desde_primer_commit"]
CONJUNTOS_DIFUSO = {"originales_10": VARIABLES_DIFUSO, "ampliadas": VARIABLES_DIFUSO_AMPLIADAS}
ANIOS_DESLIZANTE = 3


# ------------------------------------------------------------------ datos
def cargar():
    df = pd.read_parquet(DATOS)
    df = df[(~df["censurado"])].copy()
    return df.sort_values("t_commit").reset_index(drop=True)


def _ts(x):
    t = pd.Timestamp(x)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def tramo(df, a, b):
    f = df["fecha"]
    return df[(f >= _ts(a)) & (f < _ts(b))]


def particion(df, inicio_eval, ventana="creciente"):
    """Entrenamiento con hueco de 90 días antes de inicio_eval.

    ventana="creciente" (iteración 1): desde INICIO. ventana="deslizante_3a" (iteración 2):
    solo los ANIOS_DESLIZANTE años anteriores al fin del entrenamiento.
    """
    fin = _ts(inicio_eval) - pd.Timedelta(days=HUECO_DIAS)
    if ventana == "creciente":
        return tramo(df, INICIO, fin)
    if ventana == "deslizante_3a":
        return tramo(df, fin - pd.DateOffset(years=ANIOS_DESLIZANTE), fin)
    raise ValueError(ventana)


def huella_prueba(df):
    """SHA-256 de los hashes y etiquetas de la prueba: prueba que no cambió."""
    te = tramo(df, *PRUEBA)
    h = hashlib.sha256()
    for c, r in zip(te["hash"], te["riesgoso"]):
        h.update(f"{c}{r}".encode())
    return h.hexdigest(), int(len(te))


# ------------------------------------------------------------------ modelos
def _log1p(z):
    return np.log1p(np.clip(z, 0, None))


def modelo(nombre, semilla=0, variables=None, **hp):
    """variables: lista de variables del difuso (por omisión VARIABLES_DIFUSO, iteración 1)."""
    from difuso import ClasificadorDifuso
    variables = VARIABLES_DIFUSO if variables is None else list(variables)
    if nombre == "mayoritaria":
        return Mayoritaria()
    if nombre == "logistica":
        return make_pipeline(FunctionTransformer(_log1p), StandardScaler(),
                             LogisticRegression(C=hp.get("C", 1.0), max_iter=3000))
    if nombre == "gboosting":
        return HistGradientBoostingClassifier(
            learning_rate=hp.get("learning_rate", 0.1), max_leaf_nodes=hp.get("max_leaf_nodes", 31),
            max_iter=hp.get("max_iter", 200), random_state=semilla)
    if nombre == "difuso_evolutivo":
        return ClasificadorDifuso(variables, evolutivo=True, semilla=semilla, **hp)
    if nombre == "difuso_sin_evolucion":
        return ClasificadorDifuso(variables, evolutivo=False, semilla=semilla, **hp)
    raise ValueError(nombre)


def columnas(nombre, variables=None):
    if nombre.startswith("difuso"):
        return VARIABLES_DIFUSO if variables is None else list(variables)
    return VARIABLES


class Mayoritaria:
    """Referencia trivial: siempre 'no riesgoso'. Puntaje constante = prevalencia."""
    def fit(self, X, y):
        self.p_ = float(np.mean(y))
        return self

    def predict_proba(self, X):
        n = len(X)
        return np.column_stack([np.full(n, 1 - self.p_), np.full(n, self.p_)])


def n_parametros(nombre, m):
    if nombre == "mayoritaria":
        return 1
    if nombre == "logistica":
        lr = m[-1]
        return int(lr.coef_.size + lr.intercept_.size)
    if nombre == "gboosting":
        return int(sum(p.get_n_leaf_nodes() * 2 - 1 for it in m._predictors for p in it))
    return int(m.n_parametros())


def ajustar(nombre, tr, semilla=0, variables=None, **hp):
    m = modelo(nombre, semilla, variables=variables, **hp)
    X = tr[columnas(nombre, variables)].to_numpy(float)
    t0 = time.time()
    m.fit(X, tr["riesgoso"].to_numpy())
    return m, time.time() - t0


def predecir(nombre, m, te):
    t0 = time.time()
    # el difuso guarda sus variables; así se predice con las mismas con que se ajustó
    cols = list(m.variables) if nombre.startswith("difuso") else columnas(nombre)
    p = m.predict_proba(te[cols].to_numpy(float))[:, 1]
    return p, time.time() - t0


# ------------------------------------------------------------------ métricas
def umbral_mcc(y, p):
    """Umbral que maximiza el MCC (se elige en validación y se aplica en prueba)."""
    cand = np.unique(np.quantile(p, np.linspace(0.5, 0.995, 120)))
    mcc = [matthews_corrcoef(y, p >= u) for u in cand]
    return float(cand[int(np.argmax(mcc))])


def metricas(y, p, umbral=None):
    y = np.asarray(y)
    r = {"n": int(len(y)), "prevalencia": float(y.mean()),
         "auc_pr": float(average_precision_score(y, p)) if y.sum() else float("nan"),
         "auc_roc": float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else float("nan")}
    r["auc_pr_sobre_prev"] = r["auc_pr"] / r["prevalencia"]
    if umbral is not None:
        yp = p >= umbral
        tp, fn = int((yp & (y == 1)).sum()), int((~yp & (y == 1)).sum())
        tn, fp = int((~yp & (y == 0)).sum()), int((yp & (y == 0)).sum())
        r.update({"umbral": umbral, "mcc": float(matthews_corrcoef(y, yp)),
                  "sensibilidad": tp / max(tp + fn, 1), "especificidad": tn / max(tn + fp, 1),
                  "marcados": float(yp.mean()), "tp": tp, "fp": fp, "tn": tn, "fn": fn})
    return r


def bootstrap_ic(y, p, f=average_precision_score, n=N_BOOT, semilla=0):
    rng = np.random.default_rng(semilla)
    y, p = np.asarray(y), np.asarray(p)
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if y[i].sum():
            vals.append(f(y[i], p[i]))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


# ------------------------------------------------------------------ registro
CAMPOS_REGISTRO = ["fecha_hora", "etapa", "modelo", "config", "semilla", "ventana",
                   "n_entrenamiento", "auc_pr_val", "auc_roc_val", "tiempo_entrenamiento_s",
                   "n_parametros", "observaciones"]


def registrar(**fila):
    RESULTADOS.mkdir(exist_ok=True)
    ruta = RESULTADOS / "registro_experimentos.csv"
    nuevo = not ruta.exists()
    fila["fecha_hora"] = dt.datetime.now().isoformat(timespec="seconds")
    fila["config"] = json.dumps(fila.get("config", {}), sort_keys=True)
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_REGISTRO)
        if nuevo:
            w.writeheader()
        w.writerow({k: fila.get(k, "") for k in CAMPOS_REGISTRO})


def guardar_json(ruta, obj):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=float))
