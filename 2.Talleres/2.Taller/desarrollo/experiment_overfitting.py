"""
Validación Experimental del Perceptrón Multicapa (MLP): Sobreajuste y Parada Temprana
Numeral 6 - Análisis del Fenómeno de Sobreajuste (Overfitting) y Algoritmo Early Stopping
Dataset: Breast Cancer Wisconsin Diagnostic (UCI ML Repository, D=30, K=2)

Asignatura: Inteligencia Computacional
Maestría en Ciencias de la Información y las Comunicaciones (MCIC)
Universidad Distrital Francisco José de Caldas
"""

from __future__ import annotations

import copy
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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from mlp import MultilayerPerceptron

# -----------------------------------------------------------------------------
# Configuración Estética Global y Directorios de Salida
# -----------------------------------------------------------------------------
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 13
plt.rcParams["figure.dpi"] = 300

DIR_DEV_FIG = str(BASE_DIR / "desarrollo" / "figuras")
DIR_INF_FIG = str(BASE_DIR / "informe" / "figuras")
DIR_DEV_RES = str(BASE_DIR / "desarrollo" / "resultados")
DIR_INF_RES = str(BASE_DIR / "informe" / "tablas")

for d in [DIR_DEV_FIG, DIR_INF_FIG, DIR_DEV_RES, DIR_INF_RES]:
    os.makedirs(d, exist_ok=True)


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
    """Guarda un fragmento de tabla LaTeX en desarrollo/ e informe/."""
    path_dev = os.path.join(DIR_DEV_RES, filename)
    path_inf = os.path.join(DIR_INF_RES, filename)
    with open(path_dev, "w", encoding="utf-8") as f:
        f.write(content)
    with open(path_inf, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [Tabla LaTeX guardada] -> {path_dev} y {path_inf}")


# -----------------------------------------------------------------------------
# Clase Gestora de Early Stopping y Checkpointing Profundo
# -----------------------------------------------------------------------------
class EarlyStoppingCheckpoint:
    """
    Controlador riguroso de Parada Temprana (Early Stopping) y Checkpointing sináptico.

    Monitorea el error de validación (E_val) época a época. Si E_val no decrece al menos
    en `min_delta` durante `patience` épocas consecutivas, activa la señal de parada temprana
    y preserva una copia profunda (deepcopy) de la mejor configuración de pesos y sesgos (W*, b*).

    Parámetros
    ----------
    patience : int, default=40
        Número de épocas de tolerancia consecutivas sin mejora significativa.
    min_delta : float, default=1e-4
        Umbral mínimo absoluto de reducción del error para calificar como mejora.
    """

    def __init__(self, patience: int = 40, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float("inf")
        self.best_epoch = -1
        self.best_weights: Optional[List[np.ndarray]] = None
        self.best_biases: Optional[List[np.ndarray]] = None
        self.patience_counter = 0
        self.stop_triggered = False
        self.trigger_epoch: Optional[int] = None

    def step(
        self,
        epoch: int,
        val_loss: float,
        weights: List[np.ndarray],
        biases: List[np.ndarray],
    ) -> bool:
        """
        Evalúa el error de validación de la época actual y actualiza el checkpoint.

        Retorna
        -------
        bool : True si se superó la paciencia (parada temprana activada), False en caso contrario.
        """
        if val_loss < (self.best_loss - self.min_delta):
            self.best_loss = val_loss
            self.best_epoch = epoch
            self.best_weights = copy.deepcopy(weights)
            self.best_biases = copy.deepcopy(biases)
            self.patience_counter = 0
        else:
            self.patience_counter += 1
            if self.patience_counter >= self.patience and not self.stop_triggered:
                self.stop_triggered = True
                self.trigger_epoch = epoch
                return True

        return False

    def restore_best(self, model: MultilayerPerceptron) -> None:
        """Restaura los pesos y sesgos sinápticos óptimos (W*, b*) en el modelo."""
        if self.best_weights is None or self.best_biases is None:
            raise ValueError("No existen pesos checkpointed para restaurar.")
        model.weights = copy.deepcopy(self.best_weights)
        model.biases = copy.deepcopy(self.best_biases)


# -----------------------------------------------------------------------------
# Carga, Partición y Preprocesamiento de Datos
# -----------------------------------------------------------------------------
def load_and_preprocess_breast_cancer(
    train_ratio: float = 0.50,
    val_ratio: float = 0.25,
    test_ratio: float = 0.25,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Carga el dataset Breast Cancer Wisconsin Diagnostic y realiza partición
    estratificada Train/Val/Test (50% / 25% / 25%) con estandarización z-score
    calculada estrictamente sobre Train para evitar fuga de información (data leakage).
    """
    assert np.isclose(train_ratio + val_ratio + test_ratio, 1.0), "Las proporciones deben sumar 1.0."

    data = load_breast_cancer()
    X = data.data  # shape (569, 30)
    y = data.target  # shape (569,), 0: Maligno, 1: Benigno

    # Primera división: 50% Train, 50% Temporal (Val + Test)
    X_tr, X_temp, y_tr, y_temp = train_test_split(
        X,
        y,
        test_size=(val_ratio + test_ratio),
        random_state=seed,
        stratify=y,
    )

    # Segunda división del bloque temporal: proporción equitativa 50%-50% (25% y 25% del total)
    val_relative_ratio = val_ratio / (val_ratio + test_ratio)
    X_va, X_te, y_va, y_te = train_test_split(
        X_temp,
        y_temp,
        test_size=(1.0 - val_relative_ratio),
        random_state=seed,
        stratify=y_temp,
    )

    # Estandarización z-score estricta (fit SOLO en Train)
    scaler = StandardScaler()
    X_tr_std = scaler.fit_transform(X_tr)
    X_va_std = scaler.transform(X_va)
    X_te_std = scaler.transform(X_te)

    return {
        "X_train": X_tr_std,
        "y_train": y_tr,
        "X_val": X_va_std,
        "y_val": y_va,
        "X_test": X_te_std,
        "y_test": y_te,
        "feature_names": data.feature_names,
        "target_names": data.target_names,
        "scaler": scaler,
        "n_samples_train": X_tr.shape[0],
        "n_samples_val": X_va.shape[0],
        "n_samples_test": X_te.shape[0],
        "n_features": X.shape[1],
    }


# -----------------------------------------------------------------------------
# Función de Entrenamiento Exhaustivo con Registro Época a Época
# -----------------------------------------------------------------------------
def train_overparameterized_mlp(
    data_dict: Dict[str, Any],
    layer_sizes: List[int] = [30, 64, 32, 1],
    learning_rate: float = 0.08,
    momentum: float = 0.50,
    max_epochs: int = 1500,
    patience: int = 40,
    min_delta: float = 1e-4,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Entrena una red deliberadamente sobreparametrizada durante `max_epochs` épocas
    en modo online muestra a muestra, registrando la trayectoria completa de
    E_train y E_val e implementando paralelamente el algoritmo de Early Stopping.
    """
    X_train = data_dict["X_train"]
    y_train = data_dict["y_train"]
    X_val = data_dict["X_val"]
    y_val = data_dict["y_val"]
    X_test = data_dict["X_test"]
    y_test = data_dict["y_test"]

    N_train = X_train.shape[0]

    # Instanciación de la red sobreparametrizada
    mlp = MultilayerPerceptron(
        layer_sizes=layer_sizes,
        activations="sigmoid",
        learning_rate=learning_rate,
        momentum=momentum,
        learning_mode="online",
        random_state=seed,
    )

    # Cálculo total de pesos y sesgos entrenables
    total_params = 0
    for l in range(len(layer_sizes) - 1):
        total_params += (layer_sizes[l] * layer_sizes[l + 1]) + layer_sizes[l + 1]

    checkpoint = EarlyStoppingCheckpoint(patience=patience, min_delta=min_delta)

    history_train_mse: List[float] = []
    history_val_mse: List[float] = []
    history_train_acc: List[float] = []
    history_val_acc: List[float] = []

    print("\n" + "=" * 70)
    print("INICIANDO ENTRENAMIENTO DE RED SOBREPARAMETRIZADA (NUMERAL 6)")
    print(f"Arquitectura: {layer_sizes} | Parámetros Totales: {total_params}")
    print(f"Patrones Train: {N_train} (Ratio Parámetros/Muestras = {total_params / N_train:.2f})")
    print(f"Épocas máximas: {max_epochs} | Paciencia: {patience} | Delta min: {min_delta}")
    print("=" * 70)

    t_start = time.perf_counter()
    stop_epoch_recorded = None

    for epoch in range(1, max_epochs + 1):
        # Actualización estocástica muestra a muestra (online SGD con momento)
        for idx in range(N_train):
            x_i = X_train[idx : idx + 1]
            y_i = y_train[idx : idx + 1].reshape(1, 1)

            pred_i = mlp.forward(x_i)
            gw, gb = mlp.backward(y_i, pred_i)
            mlp._update_weights(gw, gb, batch_factor=1.0)

        # Evaluación de métricas al cierre de la época
        pred_train = mlp.forward(X_train)
        pred_val = mlp.forward(X_val)

        epoch_train_mse = float(np.mean((y_train.reshape(-1, 1) - pred_train) ** 2))
        epoch_val_mse = float(np.mean((y_val.reshape(-1, 1) - pred_val) ** 2))

        epoch_train_acc = float(np.mean((pred_train.ravel() >= 0.5) == y_train))
        epoch_val_acc = float(np.mean((pred_val.ravel() >= 0.5) == y_val))

        history_train_mse.append(epoch_train_mse)
        history_val_mse.append(epoch_val_mse)
        history_train_acc.append(epoch_train_acc)
        history_val_acc.append(epoch_val_acc)

        # Monitoreo de Early Stopping (registra checkpoint óptimo)
        should_stop = checkpoint.step(epoch, epoch_val_mse, mlp.weights, mlp.biases)
        if should_stop and stop_epoch_recorded is None:
            stop_epoch_recorded = epoch
            print(
                f"  >>> [Early Stopping Trigger] Época {epoch}: Paciencia ({patience}) agotada. "
                f"Mejor Época = {checkpoint.best_epoch} (MSE Val = {checkpoint.best_loss:.6f})"
            )

        if epoch % 100 == 0 or epoch == 1 or epoch == checkpoint.best_epoch:
            print(
                f"Época {epoch:4d}/{max_epochs} | "
                f"Train MSE = {epoch_train_mse:.6f} | "
                f"Val MSE = {epoch_val_mse:.6f} | "
                f"Train Acc = {epoch_train_acc * 100:.1f}% | "
                f"Val Acc = {epoch_val_acc * 100:.1f}%"
            )

    t_total = time.perf_counter() - t_start
    print(f"\nEntrenamiento finalizado en {t_total:.2f} s ({t_total / max_epochs * 1000:.2f} ms/época)")

    # -------------------------------------------------------------------------
    # Evaluación Cuantitativa del Modelo Sobreajustado (Pesos Finales)
    # -------------------------------------------------------------------------
    overfit_weights = copy.deepcopy(mlp.weights)
    overfit_biases = copy.deepcopy(mlp.biases)

    pred_train_overfit = mlp.predict_proba(X_train)
    pred_test_overfit = mlp.predict_proba(X_test)
    y_pred_test_overfit = (pred_test_overfit.ravel() >= 0.5).astype(int)

    overfit_train_mse = history_train_mse[-1]
    overfit_val_mse = history_val_mse[-1]
    overfit_test_mse = float(np.mean((y_test.reshape(-1, 1) - pred_test_overfit) ** 2))
    overfit_test_acc = accuracy_score(y_test, y_pred_test_overfit)
    overfit_test_f1 = f1_score(y_test, y_pred_test_overfit, zero_division=0)
    overfit_test_auc = roc_auc_score(y_test, pred_test_overfit.ravel())
    overfit_test_brier = brier_score_loss(y_test, pred_test_overfit.ravel())
    overfit_gen_gap = abs(overfit_test_mse - overfit_train_mse)

    # -------------------------------------------------------------------------
    # Evaluación Cuantitativa del Modelo con Early Stopping (Pesos Óptimos W*, b*)
    # -------------------------------------------------------------------------
    checkpoint.restore_best(mlp)

    pred_train_es = mlp.predict_proba(X_train)
    pred_test_es = mlp.predict_proba(X_test)
    y_pred_test_es = (pred_test_es.ravel() >= 0.5).astype(int)

    es_best_epoch = checkpoint.best_epoch
    es_stop_epoch = stop_epoch_recorded if stop_epoch_recorded is not None else max_epochs
    es_train_mse = history_train_mse[es_best_epoch - 1]
    es_val_mse = checkpoint.best_loss
    es_test_mse = float(np.mean((y_test.reshape(-1, 1) - pred_test_es) ** 2))
    es_test_acc = accuracy_score(y_test, y_pred_test_es)
    es_test_f1 = f1_score(y_test, y_pred_test_es, zero_division=0)
    es_test_auc = roc_auc_score(y_test, pred_test_es.ravel())
    es_test_brier = brier_score_loss(y_test, pred_test_es.ravel())
    es_gen_gap = abs(es_test_mse - es_train_mse)

    # Ahorro computacional
    epochs_saved = max_epochs - es_stop_epoch
    compute_savings_pct = (epochs_saved / max_epochs) * 100.0
    time_saved_s = (epochs_saved / max_epochs) * t_total

    return {
        "mlp_instance": mlp,
        "total_params": total_params,
        "max_epochs": max_epochs,
        "best_epoch": es_best_epoch,
        "stop_epoch": es_stop_epoch,
        "history_train_mse": history_train_mse,
        "history_val_mse": history_val_mse,
        "history_train_acc": history_train_acc,
        "history_val_acc": history_val_acc,
        "pred_test_overfit": pred_test_overfit,
        "pred_test_es": pred_test_es,
        # Métricas Overfit
        "overfit_train_mse": overfit_train_mse,
        "overfit_val_mse": overfit_val_mse,
        "overfit_test_mse": overfit_test_mse,
        "overfit_test_acc": overfit_test_acc,
        "overfit_test_f1": overfit_test_f1,
        "overfit_test_auc": overfit_test_auc,
        "overfit_test_brier": overfit_test_brier,
        "overfit_gen_gap": overfit_gen_gap,
        # Métricas Early Stopping
        "es_train_mse": es_train_mse,
        "es_val_mse": es_val_mse,
        "es_test_mse": es_test_mse,
        "es_test_acc": es_test_acc,
        "es_test_f1": es_test_f1,
        "es_test_auc": es_test_auc,
        "es_test_brier": es_test_brier,
        "es_gen_gap": es_gen_gap,
        # Ahorro de recursos
        "epochs_saved": epochs_saved,
        "compute_savings_pct": compute_savings_pct,
        "time_saved_s": time_saved_s,
        "t_total": t_total,
    }


# -----------------------------------------------------------------------------
# Experimento Complementario: Sensibilidad a la Capacidad de la Red
# -----------------------------------------------------------------------------
def sweep_architectures_complexity(
    data_dict: Dict[str, Any],
    architectures: List[Tuple[str, List[int]]],
    learning_rate: float = 0.08,
    momentum: float = 0.50,
    max_epochs: int = 1500,
    patience: int = 40,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Evalúa el compromiso sesgo-varianza variando el número de capas y neuronas ocultas.
    Registra el comportamiento asintótico y el beneficio de Early Stopping para cada caso.
    """
    X_train = data_dict["X_train"]
    y_train = data_dict["y_train"]
    X_val = data_dict["X_val"]
    y_val = data_dict["y_val"]
    X_test = data_dict["X_test"]
    y_test = data_dict["y_test"]
    N_train = X_train.shape[0]

    records = []
    curves_dict: Dict[str, Dict[str, List[float]]] = {}

    print("\n" + "=" * 70)
    print("BARRIDO DE COMPLEJIDAD ARQUITECTÓNICA (VARIANDO NEURONAS OCULTAS)")
    print("=" * 70)

    for arch_label, layer_sizes in architectures:
        # Conteo de parámetros
        total_params = 0
        for l in range(len(layer_sizes) - 1):
            total_params += (layer_sizes[l] * layer_sizes[l + 1]) + layer_sizes[l + 1]

        mlp = MultilayerPerceptron(
            layer_sizes=layer_sizes,
            activations="sigmoid",
            learning_rate=learning_rate,
            momentum=momentum,
            learning_mode="online",
            random_state=seed,
        )

        checkpoint = EarlyStoppingCheckpoint(patience=patience, min_delta=1e-4)
        h_train: List[float] = []
        h_val: List[float] = []

        for epoch in range(1, max_epochs + 1):
            for idx in range(N_train):
                x_i = X_train[idx : idx + 1]
                y_i = y_train[idx : idx + 1].reshape(1, 1)
                pred_i = mlp.forward(x_i)
                gw, gb = mlp.backward(y_i, pred_i)
                mlp._update_weights(gw, gb, batch_factor=1.0)

            p_tr = mlp.forward(X_train)
            p_va = mlp.forward(X_val)
            e_tr = float(np.mean((y_train.reshape(-1, 1) - p_tr) ** 2))
            e_va = float(np.mean((y_val.reshape(-1, 1) - p_va) ** 2))

            h_train.append(e_tr)
            h_val.append(e_va)
            checkpoint.step(epoch, e_va, mlp.weights, mlp.biases)

        # Evaluación Modelo Final (Overfit)
        pred_test_overfit = mlp.predict_proba(X_test)
        overfit_test_mse = float(np.mean((y_test.reshape(-1, 1) - pred_test_overfit) ** 2))
        overfit_test_acc = accuracy_score(y_test, (pred_test_overfit.ravel() >= 0.5).astype(int))

        # Evaluación Modelo Early Stopping
        checkpoint.restore_best(mlp)
        pred_test_es = mlp.predict_proba(X_test)
        es_test_mse = float(np.mean((y_test.reshape(-1, 1) - pred_test_es) ** 2))
        es_test_acc = accuracy_score(y_test, (pred_test_es.ravel() >= 0.5).astype(int))

        best_ep = checkpoint.best_epoch

        records.append({
            "Etiqueta": arch_label,
            "Arquitectura": str(layer_sizes),
            "Parametros": total_params,
            "Ratio_Par_Muestras": round(total_params / N_train, 2),
            "Epoca_Optima": best_ep,
            "Train_MSE_Final": h_train[-1],
            "Val_MSE_Final": h_val[-1],
            "Val_MSE_Min": checkpoint.best_loss,
            "Overfit_Test_MSE": overfit_test_mse,
            "Overfit_Test_Acc": overfit_test_acc * 100.0,
            "ES_Test_MSE": es_test_mse,
            "ES_Test_Acc": es_test_acc * 100.0,
            "Gen_Gap_Overfit": abs(overfit_test_mse - h_train[-1]),
            "Gen_Gap_ES": abs(es_test_mse - h_train[best_ep - 1]),
        })

        curves_dict[arch_label] = {"val": h_val, "train": h_train}

        print(
            f"  {arch_label:18s} {str(layer_sizes):15s} | Params: {total_params:4d} | "
            f"Best Ep: {best_ep:3d} | Overfit Acc: {overfit_test_acc*100.0:.2f}% | "
            f"ES Acc: {es_test_acc*100.0:.2f}% | ES Test MSE: {es_test_mse:.5f}"
        )

    df_sweep = pd.DataFrame(records)
    return df_sweep, curves_dict


# -----------------------------------------------------------------------------
# Generación de Visualizaciones Rigurosas (300 DPI)
# -----------------------------------------------------------------------------
def plot_overfitting_main_curve(results: Dict[str, Any]) -> None:
    """
    Genera la Figura Principal de Sobreajuste con curvas conjuntas E_train vs. E_val,
    anotaciones de regiones teóricas, delimitación de parada temprana y recuadro zoom (inset).
    """
    history_train = results["history_train_mse"]
    history_val = results["history_val_mse"]
    best_epoch = results["best_epoch"]
    stop_epoch = results["stop_epoch"]
    max_epochs = results["max_epochs"]
    epochs = np.arange(1, max_epochs + 1)

    fig, ax = plt.subplots(figsize=(10, 6.2))

    # Curvas principales
    ax.plot(
        epochs,
        history_train,
        label=r"Error Entrenamiento ($E_{\mathrm{train}}$ - MSE)",
        color="#1f77b4",
        linewidth=2.2,
    )
    ax.plot(
        epochs,
        history_val,
        label=r"Error Validación ($E_{\mathrm{val}}$ - MSE)",
        color="#d62728",
        linewidth=2.2,
    )

    # Región 1: Subajuste (Underfitting)
    ax.axvspan(1, 10, color="#aec7e8", alpha=0.25, label="Zona de Subajuste (Underfitting)")

    # Región 2: Óptimo de parada
    ax.axvline(
        x=best_epoch,
        color="#2ca02c",
        linestyle="--",
        linewidth=2.0,
        label=f"Punto Óptimo de Parada ($t^* = {best_epoch}$, Mínimo $E_{{\\mathrm{{val}}}}$)",
    )

    # Región 3: Disparo de Early Stopping
    ax.axvline(
        x=stop_epoch,
        color="#ff7f0e",
        linestyle=":",
        linewidth=2.0,
        label=f"Disparo de Early Stopping ($t_{{\\mathrm{{stop}}}} = {stop_epoch}$, Paciencia $P=40$)",
    )

    # Región 4: Sobreajuste y Divergencia de Varianza
    ax.axvspan(
        stop_epoch,
        max_epochs,
        color="#ff9896",
        alpha=0.20,
        label="Zona de Sobreajuste y Divergencia de Varianza",
    )

    # Anotaciones con flechas
    min_val_loss = history_val[best_epoch - 1]
    ax.annotate(
        f"Mínimo Global Validación\n$E_{{\\mathrm{{val}}}}^* = {min_val_loss:.4f}$\n(Época {best_epoch})",
        xy=(best_epoch, min_val_loss),
        xytext=(best_epoch + 120, min_val_loss + 0.009),
        arrowprops=dict(facecolor="#2ca02c", edgecolor="#2ca02c", arrowstyle="->", lw=1.8),
        fontsize=9.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#2ca02c", lw=1.2),
    )

    final_train_loss = history_train[-1]
    final_val_loss = history_val[-1]

    ax.annotate(
        f"Divergencia por Sobreajuste:\n"
        f"$E_{{\\mathrm{{train}}}} \\to {final_train_loss:.6f}$\n"
        f"$E_{{\\mathrm{{val}}}} \\uparrow {final_val_loss:.4f}$",
        xy=(1350, final_val_loss),
        xytext=(1050, 0.009),
        arrowprops=dict(facecolor="#d62728", edgecolor="#d62728", arrowstyle="->", lw=1.8),
        fontsize=9.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#d62728", lw=1.2),
    )

    # Configuración de ejes
    ax.set_title(
        r"Dinámica de Sobreajuste y Parada Temprana en MLP Sobreparametrizado $[30, 64, 32, 1]$",
        fontsize=12.5,
        pad=12,
        fontweight="bold",
    )
    ax.set_xlabel("Épocas de Entrenamiento", fontsize=11, fontweight="bold")
    ax.set_ylabel("Error Cuadrático Medio (MSE)", fontsize=11, fontweight="bold")
    ax.set_xlim(0, max_epochs)
    ax.set_ylim(0, max(history_val) * 1.15)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.98), ncol=2, frameon=True, framealpha=0.92)

    # -------------------------------------------------------------------------
    # Recuadro Zoom (Inset Axes) para las primeras 120 épocas
    # -------------------------------------------------------------------------
    axins = inset_axes(ax, width="38%", height="38%", loc="center right", borderpad=2.5)
    zoom_epochs = 100
    axins.plot(epochs[:zoom_epochs], history_train[:zoom_epochs], color="#1f77b4", linewidth=1.8)
    axins.plot(epochs[:zoom_epochs], history_val[:zoom_epochs], color="#d62728", linewidth=1.8)
    axins.axvline(x=best_epoch, color="#2ca02c", linestyle="--", linewidth=1.5)
    axins.axvline(x=stop_epoch, color="#ff7f0e", linestyle=":", linewidth=1.5)
    axins.scatter([best_epoch], [min_val_loss], color="#2ca02c", s=50, zorder=5)

    axins.set_xlim(1, zoom_epochs)
    val_zoom_sub = history_val[:zoom_epochs]
    axins.set_ylim(min(val_zoom_sub) * 0.8, max(val_zoom_sub) * 1.05)
    axins.set_title("Detalle: Épocas 1 a 100", fontsize=8.5, fontweight="bold")
    axins.tick_params(labelsize=7.5)
    axins.grid(True, linestyle=":", alpha=0.6)
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5", lw=1.0)

    save_fig_dual(fig, "overfitting_curvas_aprendizaje_early_stopping.png")


def plot_generalization_comparative_panel(
    results: Dict[str, Any],
    sweep_df: pd.DataFrame,
    sweep_curves: Dict[str, Dict[str, List[float]]],
    y_test: np.ndarray,
) -> None:
    """
    Genera el panel comparativo de generalización (3 subplots):
    - Subplot A: Gráfico de barras contrastando Modelo Sobreajustado vs Early Stopping.
    - Subplot B: Distribución de probabilidades predichas en Test (calibración vs sobreconfianza).
    - Subplot C: Curvas de validación vs épocas para diferentes complejidades de red.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.0))

    # -------------------------------------------------------------------------
    # Panel A: Comparativa de Métricas Clave
    # -------------------------------------------------------------------------
    ax0 = axes[0]
    metric_labels = ["Test Accuracy (%)", "Test MSE (x100)", "Brecha Generalización (x100)"]
    val_overfit = [
        results["overfit_test_acc"] * 100.0,
        results["overfit_test_mse"] * 100.0,
        results["overfit_gen_gap"] * 100.0,
    ]
    val_es = [
        results["es_test_acc"] * 100.0,
        results["es_test_mse"] * 100.0,
        results["es_gen_gap"] * 100.0,
    ]

    x = np.arange(len(metric_labels))
    width = 0.35

    rects1 = ax0.bar(
        x - width / 2,
        val_overfit,
        width,
        label="Sobreajustado (Época 1500)",
        color="#d62728",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
    )
    rects2 = ax0.bar(
        x + width / 2,
        val_es,
        width,
        label=f"Early Stopping (Época {results['best_epoch']})",
        color="#2ca02c",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
    )

    ax0.set_title("A) Comparativa de Desempeño en Test", fontsize=11, fontweight="bold")
    ax0.set_xticks(x)
    ax0.set_xticklabels(metric_labels, fontsize=8.5, fontweight="bold")
    ax0.set_ylabel("Valor Escalar", fontsize=9.5)
    ax0.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax0.grid(axis="y", linestyle="--", alpha=0.7)

    # Etiquetas de valor en barras
    for rect in rects1:
        h = rect.get_height()
        ax0.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.0,
            fontweight="bold",
        )
    for rect in rects2:
        h = rect.get_height()
        ax0.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.0,
            fontweight="bold",
        )

    # -------------------------------------------------------------------------
    # Panel B: Distribución de Probabilidades Predichas en Test
    # -------------------------------------------------------------------------
    ax1 = axes[1]
    p_overfit = results["pred_test_overfit"].ravel()
    p_es = results["pred_test_es"].ravel()

    # Histograma con KDE para evidenciar saturación
    sns.kdeplot(
        p_overfit,
        ax=ax1,
        color="#d62728",
        label=f"Sobreajustado (Brier={results['overfit_test_brier']:.4f})",
        fill=True,
        alpha=0.25,
        linewidth=2.0,
        bw_adjust=0.5,
    )
    sns.kdeplot(
        p_es,
        ax=ax1,
        color="#2ca02c",
        label=f"Early Stopping (Brier={results['es_test_brier']:.4f})",
        fill=True,
        alpha=0.25,
        linewidth=2.0,
        bw_adjust=0.5,
    )

    ax1.set_title("B) Distribución de Probabilidades en Test", fontsize=11, fontweight="bold")
    ax1.set_xlabel(r"Probabilidad Predicha $\hat{P}(y = 1 \mid x)$", fontsize=9.5)
    ax1.set_ylabel("Densidad de Probabilidad (KDE)", fontsize=9.5)
    ax1.set_xlim(-0.05, 1.05)
    ax1.legend(loc="upper center", frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle="--", alpha=0.7)

    # -------------------------------------------------------------------------
    # Panel C: Error de Validación según Complejidad de la Red
    # -------------------------------------------------------------------------
    ax2 = axes[2]
    colors_arch = ["#9467bd", "#1f77b4", "#ff7f0e", "#d62728"]
    epochs_axis = np.arange(1, len(next(iter(sweep_curves.values()))["val"]) + 1)

    for idx, (label, curves) in enumerate(sweep_curves.items()):
        ax2.plot(
            epochs_axis,
            curves["val"],
            label=f"{label}",
            color=colors_arch[idx % len(colors_arch)],
            linewidth=1.8,
            alpha=0.9,
        )

    ax2.set_title("C) $E_{\\mathrm{val}}$ vs Épocas según Arquitectura", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Épocas", fontsize=9.5)
    ax2.set_ylabel("Error Cuadrático Medio de Validación", fontsize=9.5)
    ax2.set_xlim(0, len(epochs_axis))
    ax2.set_ylim(0, 0.045)
    ax2.legend(loc="upper right", frameon=True, fontsize=8.0)
    ax2.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    save_fig_dual(fig, "overfitting_comparativa_generalizacion.png")


# -----------------------------------------------------------------------------
# Generación de Tablas de Resultados (CSV y LaTeX)
# -----------------------------------------------------------------------------
def export_results_tables(
    results: Dict[str, Any],
    sweep_df: pd.DataFrame,
) -> None:
    """
    Genera y exporta las tablas cuantitativas en formatos CSV y LaTeX (booktabs).
    """
    # 1. Tabla Principal: Sobreajustado vs Early Stopping
    df_main = pd.DataFrame([
        {
            "Modelo": "Sobreajustado (Pesos Finales)",
            "Arquitectura": "[30, 64, 32, 1]",
            "Parametros": results["total_params"],
            "Epoca_Evaluada": results["max_epochs"],
            "Train_MSE": f"{results['overfit_train_mse']:.6f}",
            "Val_MSE": f"{results['overfit_val_mse']:.6f}",
            "Test_MSE": f"{results['overfit_test_mse']:.6f}",
            "Test_Accuracy_Pct": f"{results['overfit_test_acc'] * 100.0:.2f}",
            "Test_F1_Macro": f"{results['overfit_test_f1']:.4f}",
            "Brecha_Generalizacion": f"{results['overfit_gen_gap']:.6f}",
            "Ahorro_Epocas_Pct": "0.00%",
        },
        {
            "Modelo": "Early Stopping (Pesos Óptimos W*, b*)",
            "Arquitectura": "[30, 64, 32, 1]",
            "Parametros": results["total_params"],
            "Epoca_Evaluada": results["best_epoch"],
            "Train_MSE": f"{results['es_train_mse']:.6f}",
            "Val_MSE": f"{results['es_val_mse']:.6f}",
            "Test_MSE": f"{results['es_test_mse']:.6f}",
            "Test_Accuracy_Pct": f"{results['es_test_acc'] * 100.0:.2f}",
            "Test_F1_Macro": f"{results['es_test_f1']:.4f}",
            "Brecha_Generalizacion": f"{results['es_gen_gap']:.6f}",
            "Ahorro_Epocas_Pct": f"{results['compute_savings_pct']:.2f}%",
        },
    ])

    save_csv_dual(df_main, "tabla_sobreajuste_early_stopping.csv")
    save_csv_dual(sweep_df, "tabla_complejidad_arquitecturas.csv")

    # 2. Fragmento LaTeX Profesional
    tex_code = f"""% Tabla generada automáticamente por experiment_overfitting.py
\\begin{{table}}[htbp]
    \\centering
    \\small
    \\caption{{Comparativa Cuantitativa de Sobreajuste y Parada Temprana en Breast Cancer (Numeral 6)}}
    \\label{{tab:sobreajuste_early_stopping}}
    \\begin{{tabular}}{{lccccccr}}
        \\toprule
        \\textbf{{Modelo}} & \\textbf{{Época}} & \\textbf{{Train MSE}} & \\textbf{{Val MSE}} & \\textbf{{Test MSE}} & \\textbf{{Exactitud (\\%)}} & \\textbf{{Brecha $|E_{{\\text{{test}}}}-E_{{\\text{{tr}}}}|$}} & \\textbf{{Ahorro}} \\\\
        \\midrule
        Sobreajustado (Final)    & {results['max_epochs']} & {results['overfit_train_mse']:.6f} & {results['overfit_val_mse']:.6f} & {results['overfit_test_mse']:.6f} & {results['overfit_test_acc']*100.0:.2f} & {results['overfit_gen_gap']:.6f} & 0.00\\% \\\\
        Early Stopping ($W^*$)   & \\textbf{{{results['best_epoch']}}}  & \\textbf{{{results['es_train_mse']:.6f}}} & \\textbf{{{results['es_val_mse']:.6f}}} & \\textbf{{{results['es_test_mse']:.6f}}} & \\textbf{{{results['es_test_acc']*100.0:.2f}}} & \\textbf{{{results['es_gen_gap']:.6f}}} & \\textbf{{{results['compute_savings_pct']:.2f}\\%}} \\\\
        \\bottomrule
    \\end{{tabular}}
\\end{{table}}
"""
    save_tex_dual(tex_code, "tabla_sobreajuste_latex.tex")


# -----------------------------------------------------------------------------
# Punto de Entrada Principal de Ejecución
# -----------------------------------------------------------------------------
def main() -> None:
    print("\n" + "=" * 80)
    print("EJECUCIÓN DEL PROTOCOLO DE ANÁLISIS DE SOBREAJUSTE Y EARLY STOPPING (NUMERAL 6)")
    print("=" * 80)

    # 1. Carga y preprocesamiento estratificado
    data_dict = load_and_preprocess_breast_cancer(
        train_ratio=0.50,
        val_ratio=0.25,
        test_ratio=0.25,
        seed=42,
    )
    print(
        f"Partición generada: Train={data_dict['n_samples_train']}, "
        f"Val={data_dict['n_samples_val']}, Test={data_dict['n_samples_test']} "
        f"(Variables continuas D={data_dict['n_features']})"
    )

    # 2. Experimento Principal: Red sobreparametrizada y Early Stopping
    results = train_overparameterized_mlp(
        data_dict=data_dict,
        layer_sizes=[30, 64, 32, 1],
        learning_rate=0.08,
        momentum=0.50,
        max_epochs=1500,
        patience=40,
        min_delta=1e-4,
        seed=42,
    )

    # 3. Barrido de complejidad arquitectónica
    architectures = [
        ("Subajustada", [30, 2, 1]),
        ("Parsimoniosa", [30, 8, 1]),
        ("Balanceada", [30, 16, 8, 1]),
        ("Sobreparametrizada", [30, 64, 32, 1]),
    ]
    sweep_df, sweep_curves = sweep_architectures_complexity(
        data_dict=data_dict,
        architectures=architectures,
        learning_rate=0.08,
        momentum=0.50,
        max_epochs=1500,
        patience=40,
        seed=42,
    )

    # 4. Generación de Visualizaciones
    print("\nGenerando figuras de alta resolución...")
    plot_overfitting_main_curve(results)
    plot_generalization_comparative_panel(results, sweep_df, sweep_curves, data_dict["y_test"])

    # 5. Exportación de Tablas
    print("\nExportando tablas de resultados...")
    export_results_tables(results, sweep_df)

    print("\n" + "=" * 80)
    print("PROTOCOLO DE SOBREAJUSTE Y EARLY STOPPING FINALIZADO CON ÉXITO")
    print("=" * 80)


if __name__ == "__main__":
    main()
