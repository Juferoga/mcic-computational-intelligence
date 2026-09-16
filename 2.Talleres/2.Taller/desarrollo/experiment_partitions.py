"""
Validación Experimental del Perceptrón Multicapa (MLP) en Múltiples Particiones
Numeral 5 - Datasets Wine, Breast Cancer Wisconsin y Banknote Authentication

Comparativa Multidimensional: MLP vs. Perceptrón Simple vs. Adaline (Taller 1)
Particiones evaluadas: 60-40, 70-30, 80-20, 90-10 (randperm reproducible, seed=42)

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Configuración de rutas canónicas en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "desarrollo"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler

from mlp import MultilayerPerceptron

# -----------------------------------------------------------------------------
# Configuración Estética Global y Directorios de Salida
# -----------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 12
plt.rcParams["figure.dpi"] = 300

DIR_DEV_FIG = str(BASE_DIR / "desarrollo" / "figuras")
DIR_INF_FIG = str(BASE_DIR / "informe" / "figuras")
DIR_DEV_RES = str(BASE_DIR / "desarrollo" / "resultados")
DIR_INF_RES = str(BASE_DIR / "informe" / "tablas")

for directory in [DIR_DEV_FIG, DIR_INF_FIG, DIR_DEV_RES, DIR_INF_RES]:
    os.makedirs(directory, exist_ok=True)


def save_fig_dual(fig: plt.Figure, filename: str) -> None:
    """Guarda una figura en alta resolución (300 DPI) en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_FIG, filename)
    path_inf = os.path.join(DIR_INF_FIG, filename)
    fig.savefig(path_dev, dpi=300, bbox_inches="tight")
    fig.savefig(path_inf, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Figura guardada] -> {path_dev} y {path_inf}")


def save_csv_dual(df: pd.DataFrame, filename: str) -> None:
    """Guarda un DataFrame tabular en formato CSV en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_RES, filename)
    path_inf = os.path.join(DIR_INF_RES, filename)
    df.to_csv(path_dev, index=False)
    df.to_csv(path_inf, index=False)
    print(f"  [Tabla CSV guardada] -> {path_dev} y {path_inf}")


def save_tex_dual(content: str, filename: str) -> None:
    """Guarda un fragmento LaTeX en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_RES, filename)
    path_inf = os.path.join(DIR_INF_RES, filename)
    with open(path_dev, "w", encoding="utf-8") as f:
        f.write(content)
    with open(path_inf, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [Tabla LaTeX guardada] -> {path_dev} y {path_inf}")


# -----------------------------------------------------------------------------
# Definiciones de Modelos Lineales del Taller 1 (Perceptrón Simple y Adaline)
# -----------------------------------------------------------------------------
class PerceptronSimple:
    """
    Perceptrón Simple de Rosenblatt con regla delta de aprendizaje supervisado (Regla 3).
    Actualización: Delta w_i = alpha * [d(x) - y(x)] * x_i.
    """

    def __init__(
        self,
        n_inputs: int,
        threshold: float = 0.0,
        alpha: float = 0.05,
        max_epochs: int = 150,
        random_state: Optional[int] = 42,
    ):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.alpha = alpha
        self.max_epochs = max_epochs
        self.random_state = random_state
        self.weights = np.zeros(n_inputs + 1, dtype=float)

    def net_input(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X_b = np.insert(X, 0, 1.0)
        else:
            X_b = np.insert(X, 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        net = self.net_input(X)
        return np.where(net >= self.threshold, 1, 0)

    def fit(self, X: np.ndarray, d: np.ndarray) -> Dict[str, Any]:
        X = np.asarray(X, dtype=float)
        d = np.asarray(d, dtype=int).ravel()
        n_samples = X.shape[0]
        X_b = np.insert(X, 0, 1.0, axis=1)

        history_errors: List[int] = []
        converged = False

        for epoch in range(self.max_epochs):
            errors = 0
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                net = np.dot(xi, self.weights)
                yi = 1 if net >= self.threshold else 0
                if yi != di:
                    self.weights += self.alpha * (di - yi) * xi
                    errors += 1

            history_errors.append(errors)
            if errors == 0:
                converged = True
                break

        return {
            "epochs": len(history_errors),
            "converged": converged,
            "final_errors": history_errors[-1] if history_errors else 0,
            "history_errors": history_errors,
        }


class Adaline:
    """
    Neurona Lineal Adaptativa (Adaline) con algoritmo Widrow-Hoff (LMS).
    Actualización: Delta w_i = alpha * [d(x) - net(x)] * x_i.
    Criterio de clasificación: salida binaria con umbral threshold=0.5.
    """

    def __init__(
        self,
        n_inputs: int,
        threshold: float = 0.5,
        alpha: float = 0.005,
        max_epochs: int = 250,
        tol: float = 1e-5,
    ):
        self.n_inputs = n_inputs
        self.threshold = threshold
        self.alpha = alpha
        self.max_epochs = max_epochs
        self.tol = tol
        self.weights = np.zeros(n_inputs + 1, dtype=float)

    def net_input(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X_b = np.insert(X, 0, 1.0)
        else:
            X_b = np.insert(X, 0, 1.0, axis=1)
        return np.dot(X_b, self.weights)

    def predict(self, X: np.ndarray) -> np.ndarray:
        y_linear = self.net_input(X)
        return np.where(y_linear >= self.threshold, 1, 0)

    def fit(self, X: np.ndarray, d: np.ndarray) -> Dict[str, Any]:
        X = np.asarray(X, dtype=float)
        d = np.asarray(d, dtype=float).ravel()
        n_samples = X.shape[0]
        X_b = np.insert(X, 0, 1.0, axis=1)

        history_mse: List[float] = []
        converged = False

        for epoch in range(self.max_epochs):
            for i in range(n_samples):
                xi = X_b[i]
                di = d[i]
                yi = np.dot(xi, self.weights)
                self.weights += self.alpha * (di - yi) * xi

            y_all = np.dot(X_b, self.weights)
            mse = float(np.mean((d - y_all) ** 2))
            history_mse.append(mse)

            if epoch > 5 and abs(history_mse[-2] - history_mse[-1]) < self.tol:
                converged = True
                break

        return {
            "epochs": len(history_mse),
            "converged": converged,
            "final_mse": history_mse[-1] if history_mse else float("inf"),
            "history_mse": history_mse,
        }


class MulticlassLinearClassifierOvR:
    """
    Ensemble One-vs-Rest (OvR) para clasificación multiclase (K > 2)
    empleando Perceptrón Simple o Adaline como clasificadores base.
    """

    def __init__(self, base_type: str, n_inputs: int, num_classes: int, **kwargs):
        self.base_type = base_type.lower()
        self.n_inputs = n_inputs
        self.num_classes = num_classes
        self.kwargs = kwargs
        self.models: List[Union[PerceptronSimple, Adaline]] = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        self.models = []
        epochs_list: List[int] = []
        converged_list: List[bool] = []

        for c in range(self.num_classes):
            d_c = (y == c).astype(int)
            if self.base_type == "perceptron":
                model = PerceptronSimple(n_inputs=self.n_inputs, **self.kwargs)
            elif self.base_type == "adaline":
                model = Adaline(n_inputs=self.n_inputs, **self.kwargs)
            else:
                raise ValueError(f"Tipo base '{self.base_type}' no soportado.")

            res = model.fit(X, d_c)
            epochs_list.append(res["epochs"])
            converged_list.append(res["converged"])
            self.models.append(model)

        return {
            "epochs": int(np.max(epochs_list)),
            "converged": bool(all(converged_list)),
            "submodels_epochs": epochs_list,
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = np.column_stack([m.net_input(X) for m in self.models])
        return np.argmax(scores, axis=1)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        preds = self.predict(X)
        return float(np.mean(preds == y))


# -----------------------------------------------------------------------------
# Funciones de Partición y Carga de Datasets (randperm seed=42)
# -----------------------------------------------------------------------------
def split_dataset_randperm(
    X: np.ndarray, y: np.ndarray, train_pct: float, seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Réplica exacta del muestreo aleatorio reproducible de Dataset_train_test.mlx:
        rng(seed)
        ind = randperm(No_examples)
        No_examples_train = round(train_pct * No_examples)
        train_data = data(ind(1:No_examples_train), :)
        test_data  = data(ind(No_examples_train+1:end), :)
    """
    n_samples = len(y)
    rng = np.random.RandomState(seed)
    perm_indices = rng.permutation(n_samples)

    n_train = int(round(train_pct * n_samples))
    train_idx = perm_indices[:n_train]
    test_idx = perm_indices[n_train:]

    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]


def load_datasets_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Carga y prepara los tres datasets del numeral 5:
      1. Wine Recognition (178 muestras, 13 variables físico-químicas, 3 clases).
      2. Breast Cancer Wisconsin Diagnostic (569 muestras, 30 variables continuas, 2 clases).
      3. Banknote Authentication (1372 muestras, 4 variables wavelets, 2 clases).
    """
    # 1. Wine
    wine = load_wine()
    X_wine = wine.data
    y_wine = wine.target
    wine_classes = [c.replace("class_", "Clase ") for c in wine.target_names]

    # 2. Breast Cancer Wisconsin
    cancer = load_breast_cancer()
    X_cancer = cancer.data
    y_cancer = cancer.target  # 0: Maligno, 1: Benigno
    cancer_classes = ["Maligno", "Benigno"]

    # 3. Banknote Authentication
    banknote_path = BASE_DIR / "bibliografia" / "data_banknote_authentication.txt"
    if not banknote_path.exists():
        banknote_path = BASE_DIR.parent / "1.Taller" / "bibliografia" / "data_banknote_authentication.txt"

    if not banknote_path.exists():
        raise FileNotFoundError(f"No se encontró data_banknote_authentication.txt en {banknote_path}")

    data_bn = np.loadtxt(str(banknote_path), delimiter=",")
    X_banknote = data_bn[:, :4]
    y_banknote = data_bn[:, 4].astype(int)  # 0: Auténtico, 1: Falso
    banknote_classes = ["Auténtico", "Falsificado"]

    return {
        "wine": {
            "name": "Wine Recognition",
            "short_name": "Wine",
            "X": X_wine,
            "y": y_wine,
            "n_samples": len(y_wine),
            "n_features": X_wine.shape[1],
            "num_classes": 3,
            "class_names": wine_classes,
            "is_multiclass": True,
            "mlp_arch": [13, 10, 3],
            "mlp_lr": 0.08,
            "mlp_epochs": 400,
            "mlp_target_error": 0.005,
        },
        "cancer": {
            "name": "Breast Cancer Wisconsin",
            "short_name": "Breast Cancer",
            "X": X_cancer,
            "y": y_cancer,
            "n_samples": len(y_cancer),
            "n_features": X_cancer.shape[1],
            "num_classes": 2,
            "class_names": cancer_classes,
            "is_multiclass": False,
            "mlp_arch": [30, 16, 8, 1],
            "mlp_lr": 0.05,
            "mlp_epochs": 300,
            "mlp_target_error": 0.010,
        },
        "banknote": {
            "name": "Banknote Authentication",
            "short_name": "Banknote",
            "X": X_banknote,
            "y": y_banknote,
            "n_samples": len(y_banknote),
            "n_features": X_banknote.shape[1],
            "num_classes": 2,
            "class_names": banknote_classes,
            "is_multiclass": False,
            "mlp_arch": [4, 8, 4, 1],
            "mlp_lr": 0.08,
            "mlp_epochs": 200,
            "mlp_target_error": 0.005,
        },
    }


# -----------------------------------------------------------------------------
# Pipeline Experimental Sistemático sobre Particiones
# -----------------------------------------------------------------------------
def run_partition_experiment() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta el protocolo comparativo multidimensional para los 3 datasets
    a través de las 4 particiones obligatorias (60-40, 70-30, 80-20, 90-10).
    """
    datasets_meta = load_datasets_metadata()
    partitions = [
        (0.60, "60-40"),
        (0.70, "70-30"),
        (0.80, "80-20"),
        (0.90, "90-10"),
    ]

    all_records: List[Dict[str, Any]] = []
    models_store: Dict[str, Any] = {}

    print("\n===================================================================")
    print("INICIANDO PROTOCOLO EXPERIMENTAL DE PARTICIONES (NUMERAL 5)")
    print("Datasets: Wine, Breast Cancer Wisconsin, Banknote Authentication")
    print("Particiones: 60-40, 70-30, 80-20, 90-10 | Semilla randperm = 42")
    print("===================================================================\n")

    for ds_key, meta in datasets_meta.items():
        print(f"\n--- Evaluando Dataset: {meta['name']} (N={meta['n_samples']}, D={meta['n_features']}, K={meta['num_classes']}) ---")
        models_store[ds_key] = {"partitions": {}, "meta": meta}

        X_all = meta["X"]
        y_all = meta["y"]
        is_multi = meta["is_multiclass"]

        for train_pct, part_name in partitions:
            # 1. División reproducible con randperm (seed=42)
            X_tr, y_tr, X_te, y_te = split_dataset_randperm(
                X_all, y_all, train_pct=train_pct, seed=42
            )

            # 2. Estandarización z-score estricta ajustada SOLO en Train (Cero Data Leakage)
            scaler = StandardScaler()
            X_tr_std = scaler.fit_transform(X_tr)
            X_te_std = scaler.transform(X_te)

            models_store[ds_key]["partitions"][part_name] = {
                "X_tr_std": X_tr_std,
                "y_tr": y_tr,
                "X_te_std": X_te_std,
                "y_te": y_te,
                "models": {},
            }

            # -------------------------------------------------------------
            # Modelo A: Perceptrón Simple
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            if is_multi:
                p_model = MulticlassLinearClassifierOvR(
                    base_type="perceptron",
                    n_inputs=meta["n_features"],
                    num_classes=meta["num_classes"],
                    threshold=0.0,
                    alpha=0.05,
                    max_epochs=150,
                )
                res_p = p_model.fit(X_tr_std, y_tr)
                p_preds_tr = p_model.predict(X_tr_std)
                p_preds_te = p_model.predict(X_te_std)
            else:
                p_model = PerceptronSimple(
                    n_inputs=meta["n_features"],
                    threshold=0.0,
                    alpha=0.05,
                    max_epochs=150,
                )
                res_p = p_model.fit(X_tr_std, y_tr)
                p_preds_tr = p_model.predict(X_tr_std)
                p_preds_te = p_model.predict(X_te_std)
            t_p = (time.perf_counter() - t0) * 1000.0  # ms

            p_acc_tr = accuracy_score(y_tr, p_preds_tr)
            p_acc_te = accuracy_score(y_te, p_preds_te)
            p_f1_te = f1_score(y_te, p_preds_te, average="macro", zero_division=0)
            p_prec_te = precision_score(y_te, p_preds_te, average="macro", zero_division=0)
            p_rec_te = recall_score(y_te, p_preds_te, average="macro", zero_division=0)
            p_cm = confusion_matrix(y_te, p_preds_te)

            all_records.append({
                "Dataset": meta["short_name"],
                "Particion": part_name,
                "Train_Pct": train_pct,
                "Test_Pct": round(1.0 - train_pct, 2),
                "Modelo": "Perceptrón Simple",
                "Arquitectura": f"[{meta['n_features']}, {meta['num_classes'] if is_multi else 1}] (Lineal)",
                "Train_Acc": p_acc_tr,
                "Test_Acc": p_acc_te,
                "Precision_Macro": p_prec_te,
                "Recall_Macro": p_rec_te,
                "F1_Macro": p_f1_te,
                "Tiempo_ms": t_p,
                "Epocas": res_p["epochs"],
                "Convergencia": res_p["converged"],
            })

            models_store[ds_key]["partitions"][part_name]["models"]["Perceptron"] = {
                "model": p_model,
                "preds": p_preds_te,
                "acc": p_acc_te,
                "f1": p_f1_te,
                "cm": p_cm,
                "time_ms": t_p,
                "epochs": res_p["epochs"],
            }

            # -------------------------------------------------------------
            # Modelo B: Adaline / LMS
            # -------------------------------------------------------------
            t0 = time.perf_counter()
            if is_multi:
                a_model = MulticlassLinearClassifierOvR(
                    base_type="adaline",
                    n_inputs=meta["n_features"],
                    num_classes=meta["num_classes"],
                    threshold=0.5,
                    alpha=0.005,
                    max_epochs=250,
                    tol=1e-5,
                )
                res_a = a_model.fit(X_tr_std, y_tr)
                a_preds_tr = a_model.predict(X_tr_std)
                a_preds_te = a_model.predict(X_te_std)
            else:
                a_model = Adaline(
                    n_inputs=meta["n_features"],
                    threshold=0.5,
                    alpha=0.005,
                    max_epochs=250,
                    tol=1e-5,
                )
                res_a = a_model.fit(X_tr_std, y_tr)
                a_preds_tr = a_model.predict(X_tr_std)
                a_preds_te = a_model.predict(X_te_std)
            t_a = (time.perf_counter() - t0) * 1000.0  # ms

            a_acc_tr = accuracy_score(y_tr, a_preds_tr)
            a_acc_te = accuracy_score(y_te, a_preds_te)
            a_f1_te = f1_score(y_te, a_preds_te, average="macro", zero_division=0)
            a_prec_te = precision_score(y_te, a_preds_te, average="macro", zero_division=0)
            a_rec_te = recall_score(y_te, a_preds_te, average="macro", zero_division=0)
            a_cm = confusion_matrix(y_te, a_preds_te)

            all_records.append({
                "Dataset": meta["short_name"],
                "Particion": part_name,
                "Train_Pct": train_pct,
                "Test_Pct": round(1.0 - train_pct, 2),
                "Modelo": "Adaline / LMS",
                "Arquitectura": f"[{meta['n_features']}, {meta['num_classes'] if is_multi else 1}] (Lineal)",
                "Train_Acc": a_acc_tr,
                "Test_Acc": a_acc_te,
                "Precision_Macro": a_prec_te,
                "Recall_Macro": a_rec_te,
                "F1_Macro": a_f1_te,
                "Tiempo_ms": t_a,
                "Epocas": res_a["epochs"],
                "Convergencia": res_a["converged"],
            })

            models_store[ds_key]["partitions"][part_name]["models"]["Adaline"] = {
                "model": a_model,
                "preds": a_preds_te,
                "acc": a_acc_te,
                "f1": a_f1_te,
                "cm": a_cm,
                "time_ms": t_a,
                "epochs": res_a["epochs"],
            }

            # -------------------------------------------------------------
            # Modelo C: Multilayer Perceptron (MLP con Momento)
            # -------------------------------------------------------------
            y_tr_mlp = (
                MultilayerPerceptron.to_one_hot(y_tr, meta["num_classes"])
                if is_multi
                else y_tr
            )
            mlp = MultilayerPerceptron(
                layer_sizes=meta["mlp_arch"],
                activations="sigmoid",
                learning_rate=meta["mlp_lr"],
                momentum=0.70,
                learning_mode="online",
                random_state=42,
            )

            t0 = time.perf_counter()
            res_mlp = mlp.fit(
                X_tr_std,
                y_tr_mlp,
                max_epochs=meta["mlp_epochs"],
                target_error=meta["mlp_target_error"],
            )
            t_mlp = (time.perf_counter() - t0) * 1000.0  # ms

            mlp_preds_tr = mlp.predict(X_tr_std)
            mlp_preds_te = mlp.predict(X_te_std)

            mlp_acc_tr = accuracy_score(y_tr, mlp_preds_tr)
            mlp_acc_te = accuracy_score(y_te, mlp_preds_te)
            mlp_f1_te = f1_score(y_te, mlp_preds_te, average="macro", zero_division=0)
            mlp_prec_te = precision_score(y_te, mlp_preds_te, average="macro", zero_division=0)
            mlp_rec_te = recall_score(y_te, mlp_preds_te, average="macro", zero_division=0)
            mlp_cm = confusion_matrix(y_te, mlp_preds_te)

            all_records.append({
                "Dataset": meta["short_name"],
                "Particion": part_name,
                "Train_Pct": train_pct,
                "Test_Pct": round(1.0 - train_pct, 2),
                "Modelo": "MLP (Backpropagation)",
                "Arquitectura": str(meta["mlp_arch"]),
                "Train_Acc": mlp_acc_tr,
                "Test_Acc": mlp_acc_te,
                "Precision_Macro": mlp_prec_te,
                "Recall_Macro": mlp_rec_te,
                "F1_Macro": mlp_f1_te,
                "Tiempo_ms": t_mlp,
                "Epocas": res_mlp["epochs"],
                "Convergencia": res_mlp["converged"],
            })

            models_store[ds_key]["partitions"][part_name]["models"]["MLP"] = {
                "model": mlp,
                "preds": mlp_preds_te,
                "acc": mlp_acc_te,
                "f1": mlp_f1_te,
                "cm": mlp_cm,
                "time_ms": t_mlp,
                "epochs": res_mlp["epochs"],
                "history_mse": res_mlp["history_mse"],
            }

            print(
                f"  [{part_name}] Perceptrón: {p_acc_te*100:5.2f}% ({t_p:6.1f}ms, {res_p['epochs']:3d} ep) | "
                f"Adaline: {a_acc_te*100:5.2f}% ({t_a:6.1f}ms, {res_a['epochs']:3d} ep) | "
                f"MLP {meta['mlp_arch']}: {mlp_acc_te*100:5.2f}% ({t_mlp:6.1f}ms, {res_mlp['epochs']:3d} ep)"
            )

    df_all = pd.DataFrame(all_records)
    return df_all, models_store


# -----------------------------------------------------------------------------
# Generación de Visualizaciones de Alta Resolución (DPI 300)
# -----------------------------------------------------------------------------
def plot_dataset_accuracy_curves(df_all: pd.DataFrame) -> None:
    """
    Genera gráficos individuales de Test Accuracy vs. Tamaño de Partición
    para cada dataset, comparando MLP vs Perceptrón vs Adaline.
    """
    datasets = df_all["Dataset"].unique()
    palette = {
        "Perceptrón Simple": "#1f77b4",
        "Adaline / LMS": "#2ca02c",
        "MLP (Backpropagation)": "#d62728",
    }
    markers = {
        "Perceptrón Simple": "o",
        "Adaline / LMS": "s",
        "MLP (Backpropagation)": "^",
    }

    file_names = {
        "Wine": "particiones_wine_accuracy.png",
        "Breast Cancer": "particiones_cancer_accuracy.png",
        "Banknote": "particiones_banknote_accuracy.png",
    }

    for ds in datasets:
        df_ds = df_all[df_all["Dataset"] == ds]
        fig, ax = plt.subplots(figsize=(8, 5))

        for model_name, color in palette.items():
            df_m = df_ds[df_ds["Modelo"] == model_name]
            x_vals = df_m["Train_Pct"] * 100
            y_vals = df_m["Test_Acc"] * 100
            ax.plot(
                x_vals,
                y_vals,
                marker=markers[model_name],
                linewidth=2.2,
                markersize=8,
                label=model_name,
                color=color,
            )
            # Etiquetas numéricas en cada punto
            for x, y in zip(x_vals, y_vals):
                ax.annotate(
                    f"{y:.1f}%",
                    xy=(x, y),
                    xytext=(0, 7),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    fontweight="bold",
                    color=color,
                )

        ax.set_title(
            f"Sensibilidad de la Exactitud de Prueba ante la Partición Train/Test\n"
            f"Dataset: {ds} (Comparativa MLP vs. Perceptrón vs. Adaline)",
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlabel("Proporción de Entrenamiento (% Train)", fontsize=10)
        ax.set_ylabel("Exactitud en Conjunto de Prueba (Test Accuracy %)", fontsize=10)
        ax.set_xticks([60, 70, 80, 90])
        ax.set_xticklabels(["60% (60-40)", "70% (70-30)", "80% (80-20)", "90% (90-10)"])
        y_min = max(0.0, df_ds["Test_Acc"].min() * 100 - 5.0)
        ax.set_ylim(y_min, 103.5)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="lower right", frameon=True, fontsize=9)
        plt.tight_layout()

        save_fig_dual(fig, file_names[ds])


def plot_global_accuracy_panel(df_all: pd.DataFrame) -> None:
    """
    Panel comparativo 1x3 mostrando la exactitud de prueba a través de los 3 datasets.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
    fig.suptitle(
        "Comparativa Multidimensional del Desempeño Generalizador (Test Accuracy)\n"
        "Evolución en Función de la Partición Train-Test para los Tres Datasets",
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )

    datasets = ["Wine", "Breast Cancer", "Banknote"]
    palette = {
        "Perceptrón Simple": "#1f77b4",
        "Adaline / LMS": "#2ca02c",
        "MLP (Backpropagation)": "#d62728",
    }
    markers = {
        "Perceptrón Simple": "o",
        "Adaline / LMS": "s",
        "MLP (Backpropagation)": "^",
    }

    for idx, ds in enumerate(datasets):
        ax = axes[idx]
        df_ds = df_all[df_all["Dataset"] == ds]

        for model_name, color in palette.items():
            df_m = df_ds[df_ds["Modelo"] == model_name]
            x_vals = df_m["Train_Pct"] * 100
            y_vals = df_m["Test_Acc"] * 100
            ax.plot(
                x_vals,
                y_vals,
                marker=markers[model_name],
                linewidth=2.0,
                markersize=7,
                label=model_name,
                color=color,
            )

        ax.set_title(f"Dataset: {ds}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Proporción Train (%)", fontsize=10)
        if idx == 0:
            ax.set_ylabel("Exactitud en Test (%)", fontsize=10)
        ax.set_xticks([60, 70, 80, 90])
        ax.set_xticklabels(["60%", "70%", "80%", "90%"])
        ax.set_ylim(85.0, 102.5)
        ax.grid(True, linestyle="--", alpha=0.6)
        if idx == 0:
            ax.legend(loc="lower right", frameon=True, fontsize=8)

    plt.tight_layout()
    save_fig_dual(fig, "particiones_comparativa_global_accuracy.png")


def plot_convergence_and_time_bars(df_all: pd.DataFrame) -> None:
    """
    Gráfico de barras agrupadas comparando tiempos de entrenamiento (ms)
    y épocas requeridas en la partición canónica 80-20.
    """
    df_80 = df_all[df_all["Particion"] == "80-20"].copy()
    datasets = ["Wine", "Breast Cancer", "Banknote"]
    models = ["Perceptrón Simple", "Adaline / LMS", "MLP (Backpropagation)"]
    colors = ["#1f77b4", "#2ca02c", "#d62728"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    x = np.arange(len(datasets))
    width = 0.25

    # Panel A: Tiempos de entrenamiento (ms, escala logarítmica para visualización óptima)
    ax0 = axes[0]
    for i, model in enumerate(models):
        times = [
            df_80[(df_80["Dataset"] == ds) & (df_80["Modelo"] == model)]["Tiempo_ms"].values[0]
            for ds in datasets
        ]
        rects = ax0.bar(x + (i - 1) * width, times, width, label=model, color=colors[i])
        for rect in rects:
            h = rect.get_height()
            ax0.annotate(
                f"{h:.1f}ms",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
            )

    ax0.set_title("A) Tiempo Computacional de Entrenamiento (Partición 80-20)", fontweight="bold")
    ax0.set_ylabel("Tiempo de Cómputo (ms - Escala Logarítmica)")
    ax0.set_yscale("log")
    ax0.set_xticks(x)
    ax0.set_xticklabels(datasets)
    ax0.grid(True, linestyle=":", alpha=0.6, which="both")
    ax0.legend(loc="upper left", frameon=True, fontsize=8)

    # Panel B: Épocas requeridas
    ax1 = axes[1]
    for i, model in enumerate(models):
        epochs = [
            df_80[(df_80["Dataset"] == ds) & (df_80["Modelo"] == model)]["Epocas"].values[0]
            for ds in datasets
        ]
        rects = ax1.bar(x + (i - 1) * width, epochs, width, label=model, color=colors[i])
        for rect in rects:
            h = rect.get_height()
            ax1.annotate(
                f"{int(h)}",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
            )

    ax1.set_title("B) Épocas Ejecutadas hasta Convergencia / Parada (80-20)", fontweight="bold")
    ax1.set_ylabel("Número de Épocas")
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", frameon=True, fontsize=8)

    plt.tight_layout()
    save_fig_dual(fig, "particiones_comparativa_tiempos_epocas.png")


def plot_confusion_matrices_grid(models_store: Dict[str, Any]) -> None:
    """
    Panel 3x3 de matrices de confusión sobre el conjunto Test en la partición 80-20.
    Filas: Datasets (Wine, Cancer, Banknote).
    Columnas: Modelos (MLP, Perceptrón, Adaline).
    """
    fig, axes = plt.subplots(3, 3, figsize=(13, 11))
    fig.suptitle(
        "Panel Comparativo de Matrices de Confusión (Partición 80-20 Test)\n"
        "Evaluación Cruzada: MLP vs. Perceptrón Simple vs. Adaline",
        fontsize=13,
        fontweight="bold",
        y=0.99,
    )

    dataset_keys = ["wine", "cancer", "banknote"]
    model_keys = [("MLP", "Blues"), ("Perceptron", "Greens"), ("Adaline", "Oranges")]

    for row_idx, ds_key in enumerate(dataset_keys):
        part_data = models_store[ds_key]["partitions"]["80-20"]
        class_names = models_store[ds_key]["meta"]["class_names"]
        ds_name = models_store[ds_key]["meta"]["short_name"]

        for col_idx, (m_name, cmap) in enumerate(model_keys):
            ax = axes[row_idx, col_idx]
            info = part_data["models"][m_name]
            cm = info["cm"]
            acc = info["acc"] * 100.0
            f1 = info["f1"]

            sns.heatmap(
                cm,
                annot=True,
                fmt="d",
                cmap=cmap,
                cbar=False,
                xticklabels=class_names,
                yticklabels=class_names,
                ax=ax,
                annot_kws={"size": 10, "weight": "bold"},
            )

            ax.set_title(
                f"{ds_name} - {m_name}\nAcc: {acc:.1f}% | F1: {f1:.3f}",
                fontsize=9.5,
                fontweight="bold",
            )
            if row_idx == 2:
                ax.set_xlabel("Clase Predicha", fontsize=9)
            else:
                ax.set_xlabel("")
            if col_idx == 0:
                ax.set_ylabel(f"Clase Real\n({ds_name})", fontsize=9, fontweight="bold")
            else:
                ax.set_ylabel("")

    plt.tight_layout()
    save_fig_dual(fig, "particiones_matrices_confusion_80_20.png")


def plot_learning_curves_mlp(models_store: Dict[str, Any]) -> None:
    """
    Curvas de aprendizaje MSE del MLP para cada partición en los 3 datasets.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    fig.suptitle(
        "Dinámica de Convergencia del MLP: Curvas de Error Cuadrático Medio (MSE)\n"
        "Evolución del Error de Entrenamiento a través de las Cuatro Particiones",
        fontsize=12,
        fontweight="bold",
        y=1.03,
    )

    dataset_keys = ["wine", "cancer", "banknote"]
    colors = {
        "60-40": "#1f77b4",
        "70-30": "#2ca02c",
        "80-20": "#ff7f0e",
        "90-10": "#9467bd",
    }

    for idx, ds_key in enumerate(dataset_keys):
        ax = axes[idx]
        ds_name = models_store[ds_key]["meta"]["short_name"]
        arch = models_store[ds_key]["meta"]["mlp_arch"]

        for part_name, color in colors.items():
            mlp_info = models_store[ds_key]["partitions"][part_name]["models"]["MLP"]
            history = mlp_info["history_mse"]
            ax.plot(
                range(1, len(history) + 1),
                history,
                label=f"Part. {part_name} ({len(history)} ep)",
                color=color,
                linewidth=1.8,
                alpha=0.9,
            )

        ax.set_title(f"{ds_name} - MLP {arch}", fontsize=10.5, fontweight="bold")
        ax.set_xlabel("Épocas", fontsize=9.5)
        if idx == 0:
            ax.set_ylabel("MSE de Entrenamiento", fontsize=9.5)
        ax.set_yscale("log")
        ax.grid(True, linestyle=":", alpha=0.6, which="both")
        ax.legend(loc="upper right", frameon=True, fontsize=8)

    plt.tight_layout()
    save_fig_dual(fig, "particiones_curvas_aprendizaje_mlp.png")


# -----------------------------------------------------------------------------
# Exportación de Tablas CSV y Fragmentos LaTeX con Booktabs
# -----------------------------------------------------------------------------
def export_results_tables(df_all: pd.DataFrame) -> None:
    """
    Genera y guarda las tablas CSV específicas por dataset, la tabla comparativa
    global frente al Taller 1 y los fragmentos LaTeX listos para el informe.
    """
    # 1. Tablas individuales por dataset
    datasets = ["Wine", "Breast Cancer", "Banknote"]
    csv_names = {
        "Wine": "tabla_particiones_wine.csv",
        "Breast Cancer": "tabla_particiones_cancer.csv",
        "Banknote": "tabla_particiones_banknote.csv",
    }

    for ds in datasets:
        df_sub = df_all[df_all["Dataset"] == ds].copy()
        df_sub_clean = df_sub[[
            "Particion",
            "Modelo",
            "Arquitectura",
            "Train_Acc",
            "Test_Acc",
            "Precision_Macro",
            "Recall_Macro",
            "F1_Macro",
            "Tiempo_ms",
            "Epocas",
            "Convergencia",
        ]]
        save_csv_dual(df_sub_clean, csv_names[ds])

    # 2. Tabla comparativa Taller 1 vs MLP (focalizada en Banknote y global)
    df_bn = df_all[df_all["Dataset"] == "Banknote"].copy()
    # Agregar datos de referencia histórica del Taller 1 (Banknote seed=2021)
    historical_taller1 = [
        {"Particion": "60-40", "Modelo": "Taller 1 Perceptrón (ref)", "Test_Acc": 0.9927, "F1_Macro": 0.9919, "Epocas": 100},
        {"Particion": "70-30", "Modelo": "Taller 1 Perceptrón (ref)", "Test_Acc": 0.9806, "F1_Macro": 0.9779, "Epocas": 100},
        {"Particion": "80-20", "Modelo": "Taller 1 Perceptrón (ref)", "Test_Acc": 0.9782, "F1_Macro": 0.9754, "Epocas": 100},
        {"Particion": "90-10", "Modelo": "Taller 1 Perceptrón (ref)", "Test_Acc": 0.9783, "F1_Macro": 0.9750, "Epocas": 100},
        {"Particion": "60-40", "Modelo": "Taller 1 Adaline (ref)", "Test_Acc": 0.9690, "F1_Macro": 0.9665, "Epocas": 27},
        {"Particion": "70-30", "Modelo": "Taller 1 Adaline (ref)", "Test_Acc": 0.9709, "F1_Macro": 0.9681, "Epocas": 24},
        {"Particion": "80-20", "Modelo": "Taller 1 Adaline (ref)", "Test_Acc": 0.9709, "F1_Macro": 0.9675, "Epocas": 21},
        {"Particion": "90-10", "Modelo": "Taller 1 Adaline (ref)", "Test_Acc": 0.9710, "F1_Macro": 0.9670, "Epocas": 20},
    ]
    df_hist = pd.DataFrame(historical_taller1)
    df_comp_bn = pd.concat([
        df_bn[["Particion", "Modelo", "Test_Acc", "F1_Macro", "Tiempo_ms", "Epocas"]],
        df_hist,
    ], ignore_index=True)
    save_csv_dual(df_comp_bn, "tabla_comparativa_taller1_vs_mlp.csv")

    # 3. Fragmento LaTeX formateado con booktabs para informe/main.tex (Líneas 193-208)
    latex_table_main = generate_latex_main_table(df_all)
    save_tex_dual(latex_table_main, "tabla_particiones_latex.tex")

    # 4. Tabla LaTeX comparativa exhaustiva de métricas y tiempos
    latex_table_full = generate_latex_full_table(df_all)
    save_tex_dual(latex_table_full, "tabla_comparativa_completa_particiones.tex")


def generate_latex_main_table(df_all: pd.DataFrame) -> str:
    """
    Genera el fragmento de tabla exacto listo para reemplazar el bloque TODO
    de la subsección 'Wine y Breast Cancer Wisconsin --- distintas particiones' en informe/main.tex.
    """
    lines = [
        r"\begin{table}[htbp]",
        r"    \centering",
        r"    \small",
        r"    \caption{Exactitud de prueba (\%) según proporción de partición (Numeral 5)}",
        r"    \label{tab:particiones_exactitud}",
        r"    \begin{tabular}{lcccc}",
        r"        \toprule",
        r"        \textbf{Dataset} & \textbf{Partición} & \textbf{MLP (\%)} & \textbf{Perceptrón (\%)} & \textbf{Adaline (\%)} \\",
        r"        \midrule",
    ]

    datasets = ["Wine", "Breast Cancer", "Banknote"]
    for ds_idx, ds in enumerate(datasets):
        df_ds = df_all[df_all["Dataset"] == ds]
        partitions = ["60-40", "70-30", "80-20", "90-10"]

        for part in partitions:
            mlp_acc = df_ds[(df_ds["Particion"] == part) & (df_ds["Modelo"] == "MLP (Backpropagation)")]["Test_Acc"].values[0] * 100.0
            p_acc = df_ds[(df_ds["Particion"] == part) & (df_ds["Modelo"] == "Perceptrón Simple")]["Test_Acc"].values[0] * 100.0
            a_acc = df_ds[(df_ds["Particion"] == part) & (df_ds["Modelo"] == "Adaline / LMS")]["Test_Acc"].values[0] * 100.0

            lines.append(
                f"        {ds:13s} & {part} & \\textbf{{{mlp_acc:5.2f}}} & {p_acc:5.2f} & {a_acc:5.2f} \\\\"
            )

        if ds_idx < len(datasets) - 1:
            lines.append(r"        \midrule")

    lines.extend([
        r"        \bottomrule",
        r"    \end{tabular}",
        r"\end{table}",
    ])
    return "\n".join(lines) + "\n"


def generate_latex_full_table(df_all: pd.DataFrame) -> str:
    """
    Genera tabla LaTeX integral que incluye Exactitud, F1-Score Macro, Tiempos y Épocas.
    """
    lines = [
        r"\begin{table*}[htbp]",
        r"    \centering",
        r"    \scriptsize",
        r"    \caption{Matriz comparativa multidimensional de desempeño: MLP vs. Perceptrón vs. Adaline bajo cuatro particiones}",
        r"    \label{tab:comparativa_multidimensional_particiones}",
        r"    \begin{tabular}{llccccccr}",
        r"        \toprule",
        r"        \textbf{Dataset} & \textbf{Partición} & \textbf{Modelo} & \textbf{Exactitud Train (\%)} & \textbf{Exactitud Test (\%)} & \textbf{F1 Macro} & \textbf{Tiempo (ms)} & \textbf{Épocas} & \textbf{Conv.} \\",
        r"        \midrule",
    ]

    for _, row in df_all.iterrows():
        conv_sym = r"\checkmark" if row["Convergencia"] else r"$\times$"
        lines.append(
            f"        {row['Dataset']} & {row['Particion']} & {row['Modelo']} & "
            f"{row['Train_Acc']*100:.2f} & {row['Test_Acc']*100:.2f} & {row['F1_Macro']:.4f} & "
            f"{row['Tiempo_ms']:.1f} & {row['Epocas']} & {conv_sym} \\\\"
        )

    lines.extend([
        r"        \bottomrule",
        r"    \end{tabular}",
        r"\end{table*}",
    ])
    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# Función Principal de Ejecución
# -----------------------------------------------------------------------------
def main() -> None:
    print("===================================================================")
    print("  TALLER 2 - ITERACIÓN 3: DATASETS EN MÚLTIPLES PARTICIONES (NUMERAL 5)")
    print("  Evaluación Sistemática: Wine, Breast Cancer y Banknote")
    print("===================================================================\n")

    # 1. Ejecutar el protocolo experimental
    df_all, models_store = run_partition_experiment()

    # 2. Generar visualizaciones académicas (300 DPI)
    print("\n[1/3] Generando gráficos de alta resolución (300 DPI)...")
    plot_dataset_accuracy_curves(df_all)
    plot_global_accuracy_panel(df_all)
    plot_convergence_and_time_bars(df_all)
    plot_confusion_matrices_grid(models_store)
    plot_learning_curves_mlp(models_store)

    # 3. Guardar tablas CSV y LaTeX
    print("\n[2/3] Exportando tablas CSV y fragmentos LaTeX con booktabs...")
    export_results_tables(df_all)

    # 4. Resumen ejecutivo de resultados clave
    print("\n[3/3] Resumen de Resultados Clave en Partición Canónica 80-20:")
    df_80 = df_all[df_all["Particion"] == "80-20"]
    for ds in ["Wine", "Breast Cancer", "Banknote"]:
        print(f"\n  >>> Dataset: {ds} (Partición 80-20) <<<")
        sub = df_80[df_80["Dataset"] == ds]
        for _, r in sub.iterrows():
            print(
                f"      * {r['Modelo']:22s} | Test Acc: {r['Test_Acc']*100:5.2f}% | "
                f"F1: {r['F1_Macro']:.4f} | Tiempo: {r['Tiempo_ms']:6.1f}ms | Épocas: {r['Epocas']:3d}"
            )

    print("\n===================================================================")
    print("PIPELINE DE PARTICIONES COMPLETADO CON ÉXITO.")
    print(f"  Figuras generadas en: {DIR_DEV_FIG} e {DIR_INF_FIG}")
    print(f"  Tablas generadas en:  {DIR_DEV_RES} e {DIR_INF_RES}")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
